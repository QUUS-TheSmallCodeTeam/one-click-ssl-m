from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
import uuid
import asyncio
from datetime import datetime

from ssl_analyzer import SSLAnalyzer
from typing import Dict, Any
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

app = FastAPI(
    title="원클릭SSL API",
    description="웹사이트 보안 분석 및 보고서 생성 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js 개발 서버
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
# report_generator = ReportGenerator()

@app.get("/")
async def root():
    return {"message": "원클릭SSL API", "version": "1.0.0"}

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
            "created_at": datetime.now().isoformat()
        }
        
        # PDF 보고서 생성은 임시로 스킵
        # asyncio.create_task(
        #     report_generator.generate_pdf_report(analysis_id, response_data)
        # )
        
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 중 오류 발생: {str(e)}")

@app.get("/api/v1/reports/{report_id}/download")
async def download_report(report_id: str):
    """MD 디자인 요소가 적용된 PDF 보고서를 다운로드합니다."""
    try:
        # 실제 분석 결과 대신 샘플 데이터 사용 (실제로는 DB에서 가져와야 함)
        analysis_data = {
            "domain": "example.com",
            "analysis_date": "2024-01-15 14:30:25",
            "security_grade": "B",
            "security_score": 75,
            "alert_message": "보안 검토가 필요합니다.",
            "user_loss_rate": 25.5,
            "annual_loss": 250000000,
            "seo_impact": 15,
            "trust_damage": 30,
            "conclusion_summary": "보안 강화를 권장합니다."
        }

        pdf_bytes = create_styled_pdf_report(analysis_data)

        def iter_pdf():
            yield pdf_bytes

        filename = f"{analysis_data.get('domain', 'report')}_security_report.pdf"
        return StreamingResponse(
            iter_pdf(),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        # 상세한 오류 로깅
        import traceback
        error_details = traceback.format_exc()
        print(f"PDF 생성 오류: {str(e)}")
        print(f"상세 오류: {error_details}")

        # 오류 응답 반환
        return {"error": f"PDF 생성 중 오류가 발생했습니다: {str(e)}"}

@app.post("/api/v1/reports/generate-pdf")
async def generate_pdf_report(request: dict):
    """PDF 보고서를 생성합니다 (별도 엔드포인트)."""
    try:
        analysis_data = request.get("analysis_data", {})
        pdf_bytes = create_styled_pdf_report(analysis_data)

        return {
            "success": True,
            "pdf_size": len(pdf_bytes),
            "filename": f"{analysis_data.get('domain', 'report')}_security_report.pdf"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

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

def create_styled_pdf_report(analysis_data: Dict[str, Any]) -> bytes:
    """보안 분석 데이터를 간단한 PDF로 변환합니다."""
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()

        story = []

        # 제목
        title = f"{analysis_data.get('domain', 'Unknown')} Security Report"
        story.append(Paragraph(title, styles['Heading1']))
        story.append(Spacer(1, 12))

        # 내용
        content = f"Analysis Date: {analysis_data.get('analysis_date', 'N/A')}\n"
        content += f"Security Grade: {analysis_data.get('security_grade', 'N/A')}\n"
        content += f"Score: {analysis_data.get('security_score', 0)}/100\n\n"

        content += "Business Impact:\n"
        content += f"- User Loss Rate: {analysis_data.get('user_loss_rate', 0)}%\n"
        content += f"- Annual Loss: ${analysis_data.get('annual_loss', 0):,}\n"

        story.append(Paragraph(content, styles['Normal']))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    except Exception as e:
        print(f"PDF 생성 중 오류: {str(e)}")
        # 오류 발생 시 아주 기본적인 PDF 생성
        return create_basic_pdf()

def create_basic_pdf() -> bytes:
    """기본적인 PDF를 생성합니다."""
    from reportlab.pdfgen import canvas

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    # 아주 기본적인 텍스트
    c.drawString(100, 750, "Security Analysis Report")
    c.drawString(100, 700, "Basic PDF Generation Test")

    c.save()
    buffer.seek(0)
    return buffer.getvalue()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)