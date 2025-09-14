from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Any
import uuid
from datetime import datetime

from ssl_analyzer import SSLAnalyzer
from report_generator_tsc import create_tsc_style_pdf_report

# 분석 결과를 저장할 메모리 저장소 (실제로는 데이터베이스를 사용해야 함)
analysis_results = {}

def _generate_issues_from_ssl_result(ssl_result: Dict[str, Any]) -> List[Dict[str, str]]:
    """SSL 결과에서 이슈 목록 생성"""
    issues = []
    
    # 인증서 만료 임박
    days_until_expiry = ssl_result.get("days_until_expiry", 0)
    if days_until_expiry < 30:
        issues.append({
            "title": "SSL 인증서 만료 임박",
            "description": f"인증서가 {days_until_expiry}일 후 만료됩니다. 갱신이 필요합니다.",
            "severity": "high" if days_until_expiry < 7 else "medium"
        })
    
    # 인증서 유효성
    if not ssl_result.get("certificate_valid", True):
        issues.append({
            "title": "유효하지 않은 SSL 인증서",
            "description": "SSL 인증서가 유효하지 않습니다. 인증서를 확인하고 교체하세요.",
            "severity": "critical"
        })
    
    # 자체 서명 인증서
    if ssl_result.get("is_self_signed", False):
        issues.append({
            "title": "자체 서명 인증서 사용",
            "description": "자체 서명된 인증서를 사용하고 있습니다. 신뢰할 수 있는 CA에서 발급받은 인증서로 교체하세요.",
            "severity": "high"
        })
    
    # 보안 헤더 누락
    missing_headers = ssl_result.get("missing_security_headers", [])
    if missing_headers:
        critical_headers = ["Strict-Transport-Security", "Content-Security-Policy", "X-Frame-Options"]
        critical_missing = [h for h in missing_headers if h in critical_headers]
        
        if critical_missing:
            issues.append({
                "title": "중요 보안 헤더 누락",
                "description": f"다음 중요 보안 헤더가 누락되었습니다: {', '.join(critical_missing)}",
                "severity": "high"
            })
        
        if len(missing_headers) > len(critical_missing):
            other_missing = [h for h in missing_headers if h not in critical_headers]
            issues.append({
                "title": "보안 헤더 누락",
                "description": f"다음 보안 헤더가 누락되었습니다: {', '.join(other_missing)}",
                "severity": "medium"
            })
    
    # HSTS 비활성화
    if not ssl_result.get("hsts_enabled", False):
        issues.append({
            "title": "HSTS (HTTP Strict Transport Security) 비활성화",
            "description": "HSTS 헤더가 설정되지 않아 중간자 공격에 취약할 수 있습니다.",
            "severity": "medium"
        })
    
    return issues

def _generate_recommendations_from_ssl_result(ssl_result: Dict[str, Any]) -> List[str]:
    """SSL 결과에서 권장사항 생성"""
    recommendations = []
    
    # SSL 등급 기반 권장사항
    ssl_grade = ssl_result.get("ssl_grade", "F")
    if ssl_grade in ["F", "D", "C"]:
        recommendations.append("SSL 구성을 전면적으로 검토하고 최신 보안 프로토콜을 적용하세요.")
        recommendations.append("약한 암호화 스위트를 비활성화하고 강력한 암호화를 사용하세요.")
    elif ssl_grade == "B":
        recommendations.append("SSL 구성을 개선하여 A 등급을 목표로 하세요.")
    
    # 보안 헤더 권장사항
    missing_headers = ssl_result.get("missing_security_headers", [])
    if "Strict-Transport-Security" in missing_headers:
        recommendations.append("HSTS (HTTP Strict Transport Security) 헤더를 설정하여 HTTPS 연결을 강제하세요.")
    if "Content-Security-Policy" in missing_headers:
        recommendations.append("CSP (Content Security Policy) 헤더를 설정하여 XSS 공격을 방지하세요.")
    if "X-Frame-Options" in missing_headers:
        recommendations.append("X-Frame-Options 헤더를 설정하여 클릭재킹 공격을 방지하세요.")
    
    # 인증서 만료 권장사항
    days_until_expiry = ssl_result.get("days_until_expiry", 0)
    if days_until_expiry < 60:
        recommendations.append("SSL 인증서 자동 갱신 시스템을 구축하여 만료를 방지하세요.")
    
    # 기본 권장사항
    if not recommendations:
        recommendations.append("정기적인 보안 점검을 통해 보안 상태를 유지하세요.")
        recommendations.append("보안 헤더 및 SSL 구성을 주기적으로 모니터링하세요.")
    
    return recommendations

app = FastAPI(
    title="원클릭 SSL체크 API",
    description="웹사이트 SSL/TLS 보안을 원클릭으로 분석하고 보고서를 생성하는 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for Hugging Face deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 요청/응답 모델
class AnalyzeRequest(BaseModel):
    url: HttpUrl

class SecurityIssue(BaseModel):
    type: str
    severity: str
    title: str
    description: str

class BusinessImpact(BaseModel):
    revenue_loss_annual: int
    seo_impact: int
    user_trust_impact: int

class AnalyzeResponse(BaseModel):
    id: str
    url: str
    ssl_grade: str
    security_score: int
    issues: List[SecurityIssue]
    business_impact: BusinessImpact
    recommendations: List[str]
    created_at: str

# 전역 인스턴스
ssl_analyzer = SSLAnalyzer()

@app.get("/")
async def root():
    """API root endpoint"""
    return {"message": "원클릭 SSL체크 API", "version": "1.0.0"}

@app.post("/api/v1/analyze", response_model=AnalyzeResponse)
async def analyze_website(request: AnalyzeRequest):
    """웹사이트 보안 분석을 수행합니다."""
    try:
        url = str(request.url)
        analysis_id = str(uuid.uuid4())
        
        # 실제 SSL 분석 수행
        ssl_result = await ssl_analyzer.analyze(url)
        
        # 보안 점수 계산
        security_score = calculate_security_score(ssl_result)
        
        # 문제점 추출
        issues = extract_issues(ssl_result)
        
        # 비즈니스 영향 계산
        business_impact = calculate_business_impact(security_score, ssl_result, issues)
        
        # 개선 권장사항 생성
        recommendations = generate_recommendations(ssl_result, issues)
        
        # 응답 데이터 구성
        response_data = {
            "id": analysis_id,
            "url": url,
            "ssl_grade": ssl_result.get("ssl_grade", "F"),
            "security_score": security_score,
            "issues": issues,
            "business_impact": business_impact,
            "recommendations": recommendations,
            "created_at": datetime.now().isoformat(),
            "ssl_result": ssl_result  # PDF 생성을 위한 원본 SSL 결과 포함
        }

        # 분석 결과를 메모리에 저장 (실제로는 데이터베이스에 저장)
        analysis_results[analysis_id] = response_data
        print(f"분석 결과 저장됨: {analysis_id} - {url}")

        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 중 오류 발생: {str(e)}")

@app.get("/api/v1/reports/{report_id}/download")
async def download_report(report_id: str):
    """MD 디자인 요소가 적용된 PDF 보고서를 다운로드합니다."""
    print(f"PDF 다운로드 요청: {report_id}")  # 디버그 로그

    try:
        # 저장된 분석 결과 조회
        if report_id not in analysis_results:
            raise HTTPException(status_code=404, detail=f"분석 결과가 존재하지 않습니다: {report_id}")

        saved_result = analysis_results[report_id]
        ssl_result = saved_result.get("ssl_result", {})

        # PDF용 데이터 구성 - 실제 분석 결과 형식에 맞춤
        analysis_data = {
            "domain": ssl_result.get("domain", saved_result.get("url", "").replace("https://", "").replace("http://", "")),
            "analysis_date": ssl_result.get("analyzed_at", saved_result.get("created_at", datetime.now().isoformat())),
            "security_grade": ssl_result.get("ssl_grade", "F"),
            "security_score": int((ssl_result.get("headers_score", 0) + (90 if ssl_result.get("ssl_grade") in ['A+', 'A', 'A-'] else 70 if ssl_result.get("ssl_grade") == 'B' else 50)) / 2),
            "alert_message": f"SSL 상태: {ssl_result.get('ssl_status', 'unknown')} - 등급: {ssl_result.get('ssl_grade', 'F')}",
            "ssl_result": ssl_result,  # 전체 SSL 결과 포함
            "certificate_valid": ssl_result.get("certificate_valid", False),
            "days_until_expiry": ssl_result.get("days_until_expiry", 0),
            "missing_security_headers": ssl_result.get("missing_security_headers", []),
            "security_headers_present": ssl_result.get("security_headers_present", []),
            "issues": _generate_issues_from_ssl_result(ssl_result),
            "recommendations": _generate_recommendations_from_ssl_result(ssl_result),
            "user_loss_rate": saved_result.get("business_impact", {}).get("revenue_loss_annual", 0) / 10000000,
            "annual_loss": saved_result.get("business_impact", {}).get("revenue_loss_annual", 0),
            "seo_impact": saved_result.get("business_impact", {}).get("seo_impact", 0),
            "trust_damage": saved_result.get("business_impact", {}).get("user_trust_impact", 0),
            "conclusion_summary": f"SSL 등급: {ssl_result.get('ssl_grade', 'F')} - {len(ssl_result.get('missing_security_headers', []))}개의 보안 헤더 누락"
        }

        print("PDF 생성 시작...")  # 디버그 로그
        print(f"분석 데이터 키: {list(analysis_data.keys())}")  # 디버그 로그
        pdf_bytes = create_tsc_style_pdf_report(analysis_data)
        print(f"PDF 생성 완료: {len(pdf_bytes)} bytes")  # 디버그 로그

        def iter_pdf():
            yield pdf_bytes

        filename = f"{analysis_data.get('domain', 'report')}_security_report.pdf"
        print(f"파일명: {filename}")  # 디버그 로그

        response = StreamingResponse(
            iter_pdf(),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        print("StreamingResponse 생성 완료")  # 디버그 로그
        return response

    except Exception as e:
        # 상세한 오류 로깅
        import traceback
        error_details = traceback.format_exc()
        print(f"PDF 생성 오류: {str(e)}")
        print(f"상세 오류: {error_details}")

        # 오류 응답 반환
        return {"error": f"PDF 생성 중 오류가 발생했습니다: {str(e)}"}


def calculate_security_score(ssl_result: dict) -> int:
    """실제 SSL 분석 결과를 바탕으로 보안 점수를 계산합니다 (TSC 보고서 기준)."""
    
    # SSL 상태에 따른 기본 점수
    ssl_status = ssl_result.get('ssl_status', 'connection_error')
    
    if ssl_status == 'no_ssl' or not ssl_result.get('port_443_open', False):
        # TSC 보고서: SSL 서비스 완전 부재
        return 0
    elif ssl_status == 'expired':
        return 10  # 만료된 인증서
    elif ssl_status == 'self_signed':
        return 25  # 자체 서명 인증서
    elif ssl_status == 'verify_failed':
        return 30  # 인증서 검증 실패
    elif ssl_status == 'valid':
        # 정상 SSL 인증서의 경우 등급에 따른 점수
        ssl_grade = ssl_result.get("ssl_grade", "B")
        grade_scores = {"A+": 95, "A": 90, "A-": 85, "B": 75, "C": 60, "D": 40}
        score = grade_scores.get(ssl_grade, 40)
        
        # 보안 헤더 상태 반영
        missing_headers = ssl_result.get("missing_security_headers", [])
        score -= len(missing_headers) * 3
        
        # 인증서 만료 임박도
        days_until_expiry = ssl_result.get('days_until_expiry', 0)
        if days_until_expiry < 30:
            score -= 10
        
        return max(0, score)
    else:
        return 0  # 연결 오류

def extract_issues(ssl_result: dict) -> List[dict]:
    """SSL 분석 결과에서 보안 문제를 추출합니다 (TSC 보고서 기준)."""
    print(ssl_result)
    issues = []
    
    ssl_status = ssl_result.get('ssl_status', 'connection_error')
    
    # 1. SSL 서비스 완전 부재 (TSC 보고서 주요 문제)
    if ssl_status == 'no_ssl' or not ssl_result.get('port_443_open', False):
        issues.append({
            "type": "ssl_service",
            "severity": "critical",
            "title": "HTTPS 서비스 완전 부재",
            "description": "443 포트가 닫혀있어 HTTPS 서비스가 전혀 제공되지 않습니다."
        })
        issues.append({
            "type": "data_encryption",
            "severity": "critical",
            "title": "모든 데이터 평문 전송",
            "description": "암호화 없이 모든 데이터가 평문으로 전송되어 도청 위험에 노출됩니다."
        })
        issues.append({
            "type": "browser_warning",
            "severity": "high",
            "title": "브라우저 보안 경고",
            "description": "모든 브라우저에서 '안전하지 않음' 경고 메시지가 표시됩니다."
        })
    
    # 2. 만료된 인증서
    if ssl_status == 'expired':
        issues.append({
            "type": "certificate",
            "severity": "critical",
            "title": "SSL 인증서 만료",
            "description": "SSL 인증서가 만료되어 브라우저에서 보안 경고를 표시합니다."
        })
    
    # 3. 자체 서명 인증서
    if ssl_status == 'self_signed':
        issues.append({
            "type": "certificate",
            "severity": "high",
            "title": "자체 서명 인증서",
            "description": "신뢰할 수 있는 인증기관에서 발급하지 않은 인증서로, 브라우저에서 경고를 표시합니다."
        })

    # 4. 인증서 검증 실패
    if ssl_status == 'verify_failed':
        issues.append({
            "type": "certificate",
            "severity": "critical",
            "title": "SSL 인증서 검증 실패",
            "description": "브라우저에서 SSL 인증서를 신뢰할 수 없습니다. 인증 기관이 유효하지 않거나 체인이 불완전합니다."
        })

    # 5. 보안 헤더 누락 (정상 SSL인 경우에도 체크)
    missing_headers = ssl_result.get("missing_security_headers", [])
    for header in missing_headers:
        issues.append({
            "type": "security_header",
            "severity": "medium",
            "title": f"{header} 헤더 누락",
            "description": f"{header} 보안 헤더가 설정되지 않았습니다."
        })
    
    # 5. 인증서 만료 임박 (정상 SSL인 경우에만 체크)
    if ssl_status == 'valid':
        days_until_expiry = ssl_result.get('days_until_expiry', 0)
        if 0 < days_until_expiry < 30:
            issues.append({
                "type": "certificate",
                "severity": "medium",
                "title": "SSL 인증서 만료 임박",
                "description": f"SSL 인증서가 {days_until_expiry}일 후에 만료됩니다."
            })
    
    return issues

def calculate_business_impact(security_score: int, ssl_result: dict, issues: List[dict]) -> dict:
    """보안 점수와 SSL 분석 결과를 바탕으로 비즈니스 영향을 계산합니다 (TSC 보고서 기준)."""
    
    ssl_status = ssl_result.get('ssl_status', 'connection_error')
    
    # TSC 보고서를 참고한 비즈니스 영향 계산
    if ssl_status == 'no_ssl' or not ssl_result.get('port_443_open', False):
        # SSL 서비스 완전 부재 - TSC 보고서 수치 사용
        return {
            "revenue_loss_annual": 1_008_000_000,  # TSC: 10.08억원
            "seo_impact": 35,  # 30-40% 하락 (보고서 기준)
            "user_trust_impact": 80  # 70-90% 이탈률 (보고서 기준)
        }
    
    elif ssl_status == 'expired':
        # 만료된 SSL 인증서
        return {
            "revenue_loss_annual": 600_000_000,  # 6억원
            "seo_impact": 25,
            "user_trust_impact": 70
        }
    
    elif ssl_status == 'self_signed':
        # 자체 서명 인증서
        return {
            "revenue_loss_annual": 400_000_000,  # 4억원
            "seo_impact": 20,
            "user_trust_impact": 60
        }
    
    elif ssl_status == 'valid':
        # 정상 SSL - 보안 점수에 따른 세분화된 영향
        base_revenue = 1_000_000_000
        loss_rate = max(0, (100 - security_score) / 100 * 0.15)  # 최대 15% 손실
        revenue_loss = int(base_revenue * loss_rate)
        
        seo_impact = max(0, (100 - security_score) // 15)  # 최대 6% 하락
        user_trust_impact = max(0, (100 - security_score) // 3)  # 최대 33% 영향
        
        return {
            "revenue_loss_annual": revenue_loss,
            "seo_impact": seo_impact,
            "user_trust_impact": user_trust_impact
        }
    
    else:
        # 연결 오류 등
        return {
            "revenue_loss_annual": 800_000_000,  # 8억원
            "seo_impact": 30,
            "user_trust_impact": 75
        }

def generate_recommendations(ssl_result: dict, issues: List[dict]) -> List[str]:
    """분석 결과를 바탕으로 개선 권장사항을 생성합니다 (TSC 보고서 기준)."""
    recommendations = []
    
    ssl_status = ssl_result.get('ssl_status', 'connection_error')
    
    if ssl_status == 'no_ssl' or not ssl_result.get('port_443_open', False):
        # TSC 보고서의 주요 권장사항
        recommendations.append("긴급: SSL 인증서 설치 및 HTTPS 서비스 활성화 (오늘 실행)")
        recommendations.append("필수: Let's Encrypt 무료 SSL 적용 (투자 0원)")
        recommendations.append("권장: HTTP → HTTPS 자동 리다이렉션 설정 (이번 주)")
        recommendations.append("장기: 보안 모니터링 체계 구축 (1개월)")
    
    elif ssl_status == 'expired':
        recommendations.append("새로운 SSL 인증서를 즉시 발급하세요.")
        recommendations.append("Let's Encrypt 자동 갱신 시스템을 설정하세요.")
    
    elif ssl_status == 'self_signed':
        recommendations.append("신뢰할 수 있는 인증기관(CA)에서 SSL 인증서를 발급받으세요.")
        recommendations.append("Let's Encrypt를 이용하여 무료로 인증서를 발급받을 수 있습니다.")
    
    elif ssl_status == 'valid':
        # 정상 SSL인 경우 세부 개선사항
        missing_headers = ssl_result.get("missing_security_headers", [])
        if missing_headers:
            recommendations.append("누락된 보안 헤더들을 웹서버 설정에 추가하세요.")
        
        ssl_grade = ssl_result.get("ssl_grade", "B")
        if ssl_grade in ["B", "C", "D"]:
            recommendations.append("SSL 등급 A 이상 달성을 위해 TLS 1.3 지원 및 보안 설정을 강화하세요.")
        
        days_until_expiry = ssl_result.get('days_until_expiry', 0)
        if 0 < days_until_expiry < 30:
            recommendations.append("인증서 만료가 임박했습니다. 자동 갱신 시스템을 확인하세요.")
        
        if not missing_headers and ssl_grade in ['A+', 'A', 'A-']:
            recommendations.append("현재 보안 설정이 우수합니다. 지속적인 모니터링을 권장합니다.")
    
    else:
        recommendations.append("서버 연결 문제를 해결한 후 SSL 인증서를 설치하세요.")
    
    return recommendations


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)