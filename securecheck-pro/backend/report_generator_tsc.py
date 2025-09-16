"""
TSC 보고서 형식의 전문적인 PDF 보고서 생성 모듈
TSC_Website_Security_Analysis_Report.md 형식을 따름
"""

from typing import Dict, Any, List
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os


def register_korean_fonts():
    """한글 폰트 등록"""
    try:
        # 현재 디렉토리 기준으로 폰트 파일 경로 설정
        current_dir = os.path.dirname(os.path.abspath(__file__))
        noto_regular_path = os.path.join(current_dir, 'fonts', 'NotoSansKR-Regular.ttf')
        noto_bold_path = os.path.join(current_dir, 'fonts', 'NotoSansKR-Bold.ttf')
        
        print(f"Regular 폰트 파일 경로: {noto_regular_path}")
        print(f"Bold 폰트 파일 경로: {noto_bold_path}")
        print(f"Regular 폰트 파일 존재 여부: {os.path.exists(noto_regular_path)}")
        print(f"Bold 폰트 파일 존재 여부: {os.path.exists(noto_bold_path)}")
        
        # Noto Sans KR TTF 폰트 사용
        if os.path.exists(noto_regular_path) and os.path.exists(noto_bold_path):
            try:
                pdfmetrics.registerFont(TTFont('Korean', noto_regular_path))
                pdfmetrics.registerFont(TTFont('Korean-Bold', noto_bold_path))
                print("Noto Sans KR TTF 폰트 등록 성공")
                return 'Korean'
            except Exception as e:
                print(f"Noto TTF 폰트 등록 오류: {e}")
        elif os.path.exists(noto_regular_path):
            try:
                pdfmetrics.registerFont(TTFont('Korean', noto_regular_path))
                pdfmetrics.registerFont(TTFont('Korean-Bold', noto_regular_path))
                print("Noto Sans KR Regular TTF 폰트 등록 성공 (Bold는 Regular 대체)")
                return 'Korean'
            except Exception as e:
                print(f"Noto TTF 폰트 등록 오류: {e}")
        
        # macOS 시스템 폰트 경로들 (백업)
        font_paths = [
            '/System/Library/Fonts/AppleSDGothicNeo.ttc',  # macOS 기본 한글 폰트
            '/System/Library/Fonts/Helvetica.ttc',
            '/Library/Fonts/NanumGothic.ttc',
            '/Library/Fonts/Arial Unicode MS.ttf',
        ]
        
        # 사용 가능한 첫 번째 폰트 등록
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont('Korean', font_path))
                    pdfmetrics.registerFont(TTFont('Korean-Bold', font_path))
                    print(f"시스템 폰트 등록 성공: {font_path}")
                    return 'Korean'
                except Exception as e:
                    print(f"시스템 폰트 등록 실패: {font_path}, 오류: {e}")
                    continue
        
        # 폰트 등록 실패시 기본 폰트 사용
        print("한글 폰트 등록 실패, 기본 폰트 사용")
        return 'Helvetica'
        
    except Exception as e:
        print(f"폰트 등록 중 오류 발생: {e}")
        return 'Helvetica'


def create_tsc_style_pdf_report(analysis_data: Dict[str, Any]) -> bytes:
    """TSC 보고서 형식의 전문적인 보안 분석 보고서 생성 - TSC_Website_Security_Analysis_Report.md 형식 준수"""
    try:
        # 한글 폰트 등록
        korean_font = register_korean_fonts()
        korean_bold_font = f'{korean_font}-Bold' if korean_font == 'Korean' else korean_font
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4,
            rightMargin=40, 
            leftMargin=40, 
            topMargin=40, 
            bottomMargin=40
        )
        
        # 스타일 정의 - TSC 보고서 스타일에 맞춤 (한글 폰트 적용)
        styles = getSampleStyleSheet()
        
        # 메인 제목 스타일 (TSC 형식)
        title_style = ParagraphStyle(
            'TSCTitle',
            parent=styles['Title'],
            fontSize=18,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=15,
            alignment=TA_CENTER,
            fontName=korean_bold_font
        )
        
        # 섹션 제목 스타일 (## 형식)
        section_style = ParagraphStyle(
            'SectionTitle',
            parent=styles['Heading1'],
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=10,
            spaceBefore=15,
            fontName=korean_bold_font
        )
        
        # 서브섹션 스타일 (### 형식)
        subsection_style = ParagraphStyle(
            'SubsectionTitle',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=8,
            spaceBefore=12,
            fontName=korean_bold_font
        )
        
        # 소제목 스타일 (#### 형식)
        subheading_style = ParagraphStyle(
            'SubHeading',
            parent=styles['Heading3'],
            fontSize=11,
            textColor=colors.HexColor('#555555'),
            spaceAfter=6,
            spaceBefore=8,
            fontName=korean_bold_font
        )
        
        # 본문 스타일
        body_style = ParagraphStyle(
            'BodyText',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            leading=12,
            spaceAfter=6,
            alignment=TA_LEFT,
            fontName=korean_font
        )
        
        # 강조 텍스트 스타일
        emphasis_style = ParagraphStyle(
            'EmphasisText',
            parent=body_style,
            fontSize=10,
            textColor=colors.HexColor('#e74c3c'),
            fontName=korean_bold_font
        )
        
        # 코드 블록 스타일 (TSC 형식) - 한글 지원 개선
        code_style = ParagraphStyle(
            'CodeBlock',
            parent=styles['Code'],
            fontSize=9,
            textColor=colors.HexColor('#2c3e50'),
            backColor=colors.HexColor('#f8f9fa'),
            borderColor=colors.HexColor('#dee2e6'),
            borderWidth=0.5,
            borderPadding=10,
            fontName=korean_font,  # 한글 코드도 한글 폰트로
            leftIndent=15,
            rightIndent=15,
            spaceBefore=8,
            spaceAfter=8
        )
        
        # 데이터 추출 및 변환 - TSC 보고서 형식에 맞춤
        domain = analysis_data.get('domain', 'Unknown Domain')
        analysis_date = datetime.now().strftime("%Y년 %m월 %d일")
        
        # SSL 및 보안 데이터
        certificate_valid = analysis_data.get('certificate_valid', False)
        certificate_expired = analysis_data.get('certificate_expired', True)
        days_until_expiry = analysis_data.get('days_until_expiry', 0)
        ssl_grade = analysis_data.get('ssl_grade', 'F')
        security_score = analysis_data.get('security_score', 0)
        
        # 보안 헤더 정보
        missing_headers = analysis_data.get('missing_security_headers', [])
        present_headers = analysis_data.get('security_headers_present', [])
        
        # 비즈니스 영향 계산
        monthly_visitors = 10000  # 기본 추정값
        conversion_rate = 0.02  # 2%
        order_conversion = 0.1  # 10%
        avg_order_value = 50000000  # 5천만원
        
        # 보안 문제로 인한 손실 계산
        # Updated loss rates matching new grading criteria
        loss_rates = {
            'F': 0.50,  # 50% loss
            'D': 0.30,  # 30% loss
            'C': 0.20,  # 20% loss
            'B': 0.10,  # 10% loss
            'A': 0.05,  # 5% loss
            'A-': 0.05,  # 5% loss (same as A)
            'A+': 0.02  # 2% loss
        }
        security_loss_rate = loss_rates.get(ssl_grade, 0.5)
        monthly_loss_visitors = int(monthly_visitors * security_loss_rate)
        annual_revenue_loss = monthly_loss_visitors * 12 * conversion_rate * order_conversion * avg_order_value
        
        story = []
        
        # ============= TSC 스타일 헤더 (단일 제목) =============
        story.append(Paragraph(f"{domain} 웹사이트 보안 및 서버 설정 문제 분석 보고서", title_style))
        story.append(Spacer(1, 20))
        
        # TSC 형식의 기본 정보 (더 깔끔하게)
        header_info = f"""
        <b>분석 대상</b>: {domain}<br/>
        <b>분석 일시</b>: {analysis_date}<br/>
        <b>분석자</b>: 원클릭SSL Security Analysis Team<br/>
        <b>보고서 버전</b>: 1.0
        """
        story.append(Paragraph(header_info, body_style))
        story.append(Spacer(1, 20))
        
        # TSC 스타일 분리선
        story.append(Paragraph("---", body_style))
        story.append(Spacer(1, 15))
        
        # ============= Executive Summary (TSC 형식) - 이모지 대신 텍스트 =============
        story.append(Paragraph("Executive Summary", section_style))
        
        # TSC 스타일 상태 평가
        if ssl_grade == 'F' or not certificate_valid:
            status_summary = f"""
{domain} 웹사이트에 대한 보안 분석 결과, <b>중대한 SSL 인증서 및 서버 설정 문제</b>가 
발견되었습니다. 현재 HTTPS 연결이 정상 작동하지 않아 고객의 개인정보 보호와 
브랜드 신뢰도에 부정적 영향을 미치고 있습니다.
"""
        elif ssl_grade in ['D', 'C']:
            status_summary = f"""
{domain} 웹사이트에 대한 보안 분석 결과, <b>보안 설정 개선이 필요한 상태</b>로
확인되었습니다. 기본적인 SSL 인증서는 설치되어 있으나, 추가적인 보안 강화가
필요한 상황입니다.
"""
        elif ssl_grade == 'B':
            status_summary = f"""
{domain} 웹사이트는 기본적인 SSL 보안이 적용되어 있으나 <b>추가 보안 강화를 통한
경쟁력 향상이 가능한 상태</b>입니다. 업계 최고 수준의 보안을 구현하여
고객 신뢰도를 극대화할 수 있습니다.
"""
        elif ssl_grade in ['A', 'A-']:
            status_summary = f"""
{domain} 웹사이트는 <b>우수한 SSL 보안 수준</b>을 유지하고 있습니다.
약간의 개선으로 최고 등급(A+)을 달성할 수 있습니다.
"""
        else:  # A+
            status_summary = f"""
{domain} 웹사이트는 <b>업계 최고 수준의 SSL 보안</b>을 구현하고 있습니다.
현재 수준을 유지하며 지속적인 모니터링이 권장됩니다.
"""
        
        story.append(Paragraph(status_summary, body_style))
        story.append(Spacer(1, 12))
        
        # 주요 발견사항 (TSC 스타일) - 이모지 대신 텍스트
        story.append(Paragraph("주요 발견사항", subsection_style))
        
        findings_content = ""
        if ssl_grade == 'F':
            findings_content += "- ❌ <b>SSL 인증서 미설치</b> 또는 HTTPS 서비스 중단<br/>"
            findings_content += "- ❌ <b>보안 연결 없이 HTTP만 서비스</b> 중<br/>"
            findings_content += "- ⚠️ <b>고객 데이터 보호 취약성</b> 존재<br/>"
        elif not certificate_valid:
            findings_content += "- ❌ <b>SSL 인증서 검증 실패</b><br/>"
            findings_content += "- ⚠️ <b>브라우저 보안 경고</b> 발생 가능<br/>"
        elif ssl_grade in ['D', 'C']:
            findings_content += "- ⚠️ <b>SSL 설정 개선 필요</b><br/>"
            findings_content += "- ⚠️ <b>보안 헤더 미설정</b><br/>"
        
        if len(missing_headers) > 5:
            findings_content += f"- ⚠️ <b>보안 헤더 {len(missing_headers)}개 누락</b><br/>"
        
        if days_until_expiry < 30 and days_until_expiry > 0:
            findings_content += f"- ⚠️ <b>SSL 인증서 만료 임박</b> ({days_until_expiry}일 남음)<br/>"
        
        if not findings_content:
            findings_content = "- ✅ <b>심각한 보안 문제가 발견되지 않았습니다</b><br/>"
        
        story.append(Paragraph(findings_content, body_style))
        story.append(Spacer(1, 12))
        
        # 비즈니스 영향 (TSC 스타일) - 이모지 대신 텍스트
        story.append(Paragraph("비즈니스 영향", subsection_style))
        
        if ssl_grade in ['F', 'D']:
            business_impact = f"""
- <b>고객 신뢰도 하락</b>: 브라우저 보안 경고로 인한 사용자 이탈 위험<br/>
- <b>SEO 불이익</b>: Google 검색 순위 하락 가능성<br/>
- <b>전문성 의심</b>: 기술 기업으로서의 신뢰도 손상<br/>
- <b>법적 리스크</b>: 개인정보보호법 준수 미흡<br/>
- <b>예상 연간 손실</b>: {annual_revenue_loss:,.0f}원
"""
        else:
            business_impact = """
- <b>현재 상태 양호</b>: 지속적인 보안 관리 필요<br/>
- <b>브랜드 신뢰도</b>: 현재 수준 유지<br/>
- <b>법적 준수</b>: 기본 요구사항 충족
"""
        
        story.append(Paragraph(business_impact, body_style))
        story.append(Spacer(1, 12))
        
        # 권장 조치 (TSC 스타일) - 이모지 대신 텍스트
        story.append(Paragraph("권장 조치 (우선순위별)", subsection_style))
        
        recommendations_content = ""
        if ssl_grade == 'F':
            recommendations_content += "1. <b>긴급</b>: HTTPS 서버 설정 수정 (1일 이내)<br/>"
            recommendations_content += "2. <b>필수</b>: Let's Encrypt 무료 SSL 인증서 적용 (1주 이내)<br/>"
            recommendations_content += "3. <b>권장</b>: 보안 강화 및 모니터링 시스템 구축 (1개월 이내)<br/>"
        elif ssl_grade in ['D', 'C']:
            recommendations_content += "1. <b>필수</b>: SSL 설정 강화 (1주 이내)<br/>"
            recommendations_content += "2. <b>권장</b>: 보안 헤더 설정 (2주 이내)<br/>"
            recommendations_content += "3. <b>권장</b>: 정기적인 보안 점검 체계 구축 (1개월 이내)<br/>"
        elif ssl_grade == 'B':
            recommendations_content += "1. <b>권장</b>: 보안 헤더 최적화 (2주 이내)<br/>"
            recommendations_content += "2. <b>권장</b>: SSL 설정 미세 튜닝 (1개월 이내)<br/>"
            recommendations_content += "3. <b>권장</b>: 성능 모니터링 강화<br/>"
        elif ssl_grade in ['A', 'A-']:
            recommendations_content += "1. <b>권장</b>: 모든 보안 헤더 적용 (A+ 달성)<br/>"
            recommendations_content += "2. <b>권장</b>: 지속적인 보안 모니터링<br/>"
            recommendations_content += "3. <b>권장</b>: 새로운 보안 기술 적용 검토<br/>"
        else:  # A+
            recommendations_content += "1. <b>현재 수준 유지</b>: 최고 보안 수준 유지<br/>"
            recommendations_content += "2. <b>권장</b>: 정기적인 보안 감사<br/>"
            recommendations_content += "3. <b>권장</b>: 새로운 보안 트렌드 반영<br/>"
        
        story.append(Paragraph(recommendations_content, body_style))
        story.append(Spacer(1, 15))
        
        story.append(Paragraph("---", body_style))
        story.append(PageBreak())
        
        # ============= 상세 기술 분석 (TSC 형식) - 이모지 대신 텍스트 =============
        story.append(Paragraph("상세 기술 분석", section_style))
        
        # 1. SSL 인증서 상태 분석
        story.append(Paragraph("1. SSL 인증서 상태 분석", subsection_style))
        
        # 현재 인증서 정보 (TSC 스타일)
        story.append(Paragraph("현재 인증서 정보", subheading_style))
        
        # 코드 블럭 대신 깔끔한 텍스트 박스 사용
        cert_info_text = f"""
인증서 세부사항:<br/>
- Domain: {domain}<br/>
- Valid: {'Yes' if certificate_valid else 'No'}<br/>
- Days Until Expiry: {days_until_expiry}일<br/>
- SSL Grade: {ssl_grade}
"""
        story.append(Paragraph(cert_info_text, code_style))
        story.append(Spacer(1, 10))
        
        # 문제점 분석 테이블 (TSC 스타일) - 이모지 대신 텍스트
        story.append(Paragraph("문제점 분석", subheading_style))
        
        cert_analysis_data = [
            ['항목', '현재 상태', '문제점', '위험도']
        ]
        
        # 인증서 타입
        if not certificate_valid:
            cert_analysis_data.append([
                '인증서 타입', 
                '검증 실패', 
                '브라우저 경고, 신뢰 불가', 
                '🔴 높음'
            ])
        else:
            cert_analysis_data.append([
                '인증서 타입', 
                '유효', 
                '없음', 
                '🟢 낮음'
            ])
        
        # SSL 등급
        if ssl_grade == 'F':
            cert_analysis_data.append([
                'SSL 등급',
                ssl_grade,
                'SSL 미적용 또는 심각한 문제',
                '🔴 높음'
            ])
        elif ssl_grade in ['D', 'C']:
            cert_analysis_data.append([
                'SSL 등급',
                ssl_grade,
                '설정 개선 필요',
                '🟡 중간'
            ])
        else:
            cert_analysis_data.append([
                'SSL 등급',
                ssl_grade,
                '양호',
                '🟢 낮음'
            ])
        
        # 유효기간
        if days_until_expiry < 7:
            cert_analysis_data.append([
                '유효기간',
                f'{days_until_expiry}일 남음',
                '즉시 갱신 필요',
                '🔴 높음'
            ])
        elif days_until_expiry < 30:
            cert_analysis_data.append([
                '유효기간',
                f'{days_until_expiry}일 남음',
                '갱신 준비 필요',
                '🟡 중간'
            ])
        else:
            cert_analysis_data.append([
                '유효기간',
                f'{days_until_expiry}일 남음',
                '정상',
                '🟢 낮음'
            ])
        
        cert_table = Table(cert_analysis_data, colWidths=[1.2*inch, 1.5*inch, 2.0*inch, 1.0*inch])
        cert_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), korean_bold_font),
            ('FONTNAME', (0, 1), (-1, -1), korean_font),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#95a5a6')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')]),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(cert_table)
        story.append(Spacer(1, 15))
        
        # 브라우저별 경고 메시지
        if ssl_grade == 'F' or not certificate_valid:
            story.append(Paragraph("브라우저별 경고 메시지", subheading_style))
            browser_warnings = """- Chrome: "이 연결은 비공개 연결이 아닙니다"
- Firefox: "보안 연결 실패"
- Safari: "이 연결은 안전하지 않습니다"
- Edge: "이 사이트는 안전하지 않습니다\""""
            story.append(Paragraph(browser_warnings, body_style))
            story.append(Spacer(1, 15))
        
        # 2. 서버 설정 문제 분석
        story.append(Paragraph("2. 서버 설정 문제 분석", subsection_style))
        
        # HTTP vs HTTPS 비교 테스트
        story.append(Paragraph("HTTP vs HTTPS 비교 테스트", subheading_style))
        
        if ssl_grade == 'F':
            http_https_comparison = f"""
<b>HTTP 접속 (포트 80)</b>:<br/>
GET http://{domain}/<br/>
HTTP/1.1 200 OK<br/>
Server: nginx<br/>
Content-Type: text/html; charset=UTF-8<br/>
<b>✅ 정상 작동</b><br/><br/>

<b>HTTPS 접속 (포트 443)</b>:<br/>
GET https://{domain}/<br/>
Connection refused 또는 SSL Error<br/>
<b>❌ 서비스 불가</b>
"""
        else:
            http_https_comparison = f"""
<b>HTTP 접속 (포트 80)</b>:<br/>
GET http://{domain}/<br/>
HTTP/1.1 301 Moved Permanently<br/>
Location: https://{domain}/<br/>
<b>✅ HTTPS로 리다이렉션</b><br/><br/>

<b>HTTPS 접속 (포트 443)</b>:<br/>
GET https://{domain}/<br/>
HTTP/1.1 200 OK<br/>
Server: nginx<br/>
Content-Type: text/html; charset=UTF-8<br/>
<b>✅ 정상 작동</b>
"""
        
        story.append(Paragraph(http_https_comparison, code_style))
        story.append(Spacer(1, 15))
        
        # nginx 서버 설정 문제 진단
        if ssl_grade == 'F':
            story.append(Paragraph("nginx 서버 설정 문제 진단", subheading_style))
            
            server_diagnosis = """추정 원인:
1. SSL 인증서 미설치 또는 경로 오류
2. nginx SSL 설정 누락 또는 오류
3. 방화벽에서 443 포트 차단
4. SSL 모듈이 nginx에 포함되지 않음

현재 nginx 설정 추정:"""
            story.append(Paragraph(server_diagnosis, body_style))
            
            nginx_config_example = f"""
<b>문제가 있는 설정 (추정)</b>:<br/><br/>
server {{<br/>
&nbsp;&nbsp;&nbsp;&nbsp;listen 80;<br/>
&nbsp;&nbsp;&nbsp;&nbsp;server_name {domain};<br/><br/>
&nbsp;&nbsp;&nbsp;&nbsp;# SSL 설정이 누락됨<br/>
&nbsp;&nbsp;&nbsp;&nbsp;# SSL 인증서 경로 없음<br/><br/>
&nbsp;&nbsp;&nbsp;&nbsp;location / {{<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;root /var/www/html;<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;index index.html index.htm;<br/>
&nbsp;&nbsp;&nbsp;&nbsp;}}<br/>
}}
"""
            story.append(Paragraph(nginx_config_example, code_style))
            story.append(Spacer(1, 15))
        
        # 3. 보안 취약점 평가
        story.append(Paragraph("3. 보안 취약점 평가", subsection_style))
        
        # 보안 위험도 매트릭스
        story.append(Paragraph("보안 위험도 매트릭스", subheading_style))
        
        risk_matrix_data = [
            ['취약점', '현재 상태', '영향도', '발생확률', '종합 위험도']
        ]
        
        if ssl_grade == 'F':
            risk_matrix_data.extend([
                ['중간자 공격 (MITM)', '높음', '치명적', '중간', '🔴 High'],
                ['데이터 도청', '높음', '높음', '높음', '🔴 High'],
                ['브랜드 신뢰도 손상', '현재 발생', '높음', '확실', '🔴 High'],
                ['SEO 패널티', '중간', '중간', '높음', '🟡 Medium']
            ])
        elif ssl_grade in ['D', 'C']:
            risk_matrix_data.extend([
                ['설정 취약점', '중간', '중간', '중간', '🟡 Medium'],
                ['브랜드 신뢰도 손상', '낮음', '중간', '낮음', '🟡 Medium'],
                ['SEO 패널티', '낮음', '낮음', '중간', '🟢 Low']
            ])
        else:
            risk_matrix_data.append([
                '현재 위험 요소', '없음', '낮음', '낮음', '🟢 Low'
            ])
        
        risk_table = Table(risk_matrix_data, colWidths=[1.3*inch, 1.0*inch, 1.0*inch, 1.0*inch, 1.2*inch])
        risk_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), korean_bold_font),
            ('FONTNAME', (0, 1), (-1, -1), korean_font),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#95a5a6')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ffeaea')]),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(risk_table)
        story.append(Spacer(1, 15))
        
        # 현재 보안 수준 평가
        story.append(Paragraph("현재 보안 수준 평가", subheading_style))
        
        # Updated score mapping for all grades including A-
        ssl_score = 95 if ssl_grade == 'A+' else 90 if ssl_grade == 'A' else 85 if ssl_grade == 'A-' else 80 if ssl_grade == 'B' else 70 if ssl_grade == 'C' else 50 if ssl_grade == 'D' else 0
        
        security_assessment = f"""SSL Labs 등급: {ssl_grade}
보안 점수: {ssl_score}/100

세부 평가:
- Certificate: {ssl_score}/100 
- Protocol Support: {min(ssl_score + 10, 100)}/100
- Key Exchange: {min(ssl_score + 5, 100)}/100  
- Cipher Strength: {min(ssl_score + 15, 100)}/100"""
        
        story.append(Paragraph(security_assessment, body_style))
        story.append(Spacer(1, 15))
        
        # 4. 경쟁사 및 업계 표준 비교
        story.append(Paragraph("4. 경쟁사 및 업계 표준 비교", subsection_style))
        
        industry_comparison = f"""
<b>업계 SSL 현황 비교</b>:<br/><br/>
• 대형 기업 A: A+ Rating ✅<br/>
• 대형 기업 B: A Rating ✅<br/>
• 대형 기업 C: A+ Rating ✅<br/>
• {domain}: {ssl_grade} Rating {'❌' if ssl_grade in ['F', 'D'] else '⚠️' if ssl_grade in ['C', 'B'] else '✅'}<br/><br/>

<b>업계 표준 대비 현황</b>:<br/>
- 업계 평균 SSL 점수: A- (85/100)<br/>
- {domain} 현재 점수: {ssl_grade} ({ssl_score}/100)<br/>
- 개선 필요 점수: {max(85 - ssl_score, 0)}점 차이
"""
        
        story.append(Paragraph(industry_comparison, body_style))
        story.append(Spacer(1, 15))
        
        story.append(Paragraph("---", body_style))
        story.append(PageBreak())
        
        # ============= 해결 방안 및 권장사항 (TSC 형식) =============
        story.append(Paragraph("🔧 해결 방안 및 권장사항", section_style))
        
        # Phase 1: 긴급 조치 (TSC 스타일)
        if ssl_grade in ['F', 'D']:
            story.append(Paragraph("Phase 1: 긴급 조치 (1-3일)", subsection_style))
            
            story.append(Paragraph("HTTPS 서버 설정 수정", subheading_style))
            story.append(Paragraph("<b>우선순위</b>: ⭐⭐⭐⭐⭐ (Critical)<br/>"
                                 "<b>예상 소요시간</b>: 1-2일<br/>"
                                 "<b>담당자</b>: 서버 관리자 또는 웹 에이전시", body_style))
            story.append(Spacer(1, 8))
            
            story.append(Paragraph("<b>필요 조치</b>:", body_style))
            
            nginx_emergency_config = f"""
<b>nginx 설정 수정 예시</b>:<br/><br/>
server {{<br/>
&nbsp;&nbsp;&nbsp;&nbsp;listen 443 ssl http2;<br/>
&nbsp;&nbsp;&nbsp;&nbsp;server_name {domain} www.{domain};<br/><br/>
&nbsp;&nbsp;&nbsp;&nbsp;# 임시로 기존 인증서 사용하되 서버 설정 수정<br/>
&nbsp;&nbsp;&nbsp;&nbsp;ssl_certificate /path/to/current.crt;<br/>
&nbsp;&nbsp;&nbsp;&nbsp;ssl_certificate_key /path/to/current.key;<br/><br/>
&nbsp;&nbsp;&nbsp;&nbsp;# Accept 헤더 처리 개선<br/>
&nbsp;&nbsp;&nbsp;&nbsp;location / {{<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;proxy_set_header Accept $http_accept;<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;proxy_set_header Host $host;<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;proxy_set_header X-Real-IP $remote_addr;<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;proxy_set_header X-Forwarded-Proto $scheme;<br/><br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;proxy_pass http://localhost:8080;  # 백엔드 서버<br/>
&nbsp;&nbsp;&nbsp;&nbsp;}}<br/><br/>
&nbsp;&nbsp;&nbsp;&nbsp;# 에러 페이지 처리<br/>
&nbsp;&nbsp;&nbsp;&nbsp;error_page 406 = @handle406;<br/>
&nbsp;&nbsp;&nbsp;&nbsp;location @handle406 {{<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return 301 http://$server_name$request_uri;<br/>
&nbsp;&nbsp;&nbsp;&nbsp;}}<br/>
}}
"""
            story.append(Paragraph(nginx_emergency_config, code_style))
            story.append(Spacer(1, 12))
            
            story.append(Paragraph("임시 해결책", subheading_style))
            temp_solutions = """1. <b>406 오류 우회</b>: 임시로 HTTP 리다이렉션 설정
2. <b>사용자 안내</b>: 웹사이트에 보안 인증서 업데이트 예정 공지  
3. <b>모니터링 강화</b>: 서버 상태 및 에러 로그 모니터링"""
            story.append(Paragraph(temp_solutions, body_style))
            story.append(Spacer(1, 15))
        
        # Phase 2: 필수 보안 조치 (TSC 스타일)
        story.append(Paragraph("Phase 2: 필수 보안 조치 (1주 이내)", subsection_style))
        
        story.append(Paragraph("Let's Encrypt SSL 인증서 적용", subheading_style))
        story.append(Paragraph("<b>우선순위</b>: ⭐⭐⭐⭐⭐ (Critical)<br/>"
                             "<b>비용</b>: 무료<br/>"
                             "<b>예상 소요시간</b>: 반나절", body_style))
        story.append(Spacer(1, 8))
        
        story.append(Paragraph("<b>구현 절차</b>:", body_style))
        
        lets_encrypt_setup = f"""
<b>구현 절차</b>:<br/><br/>
<b>1. Certbot 설치</b><br/>
sudo apt update<br/>
sudo apt install certbot python3-certbot-nginx<br/><br/>

<b>2. 인증서 발급 및 자동 설치</b><br/>
sudo certbot --nginx -d {domain} -d www.{domain}<br/><br/>

<b>3. 자동 갱신 설정</b><br/>
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -<br/><br/>

<b>4. nginx 설정 테스트</b><br/>
sudo nginx -t && sudo systemctl reload nginx
"""
        story.append(Paragraph(lets_encrypt_setup, code_style))
        story.append(Spacer(1, 12))
        
        story.append(Paragraph("<b>기대 효과</b>:", body_style))
        expected_results = """✅ 모든 브라우저에서 신뢰하는 SSL 인증서
✅ 자동 갱신으로 관리 부담 최소화  
✅ SSL Labs A 등급 달성 가능"""
        story.append(Paragraph(expected_results, body_style))
        story.append(Spacer(1, 12))
        
        # 보안 헤더 설정
        if len(missing_headers) > 0:
            story.append(Paragraph("기본 보안 강화", subheading_style))
            
            security_headers_config = f"""
<b>보안 강화 nginx 설정</b>:<br/><br/>
server {{<br/>
&nbsp;&nbsp;&nbsp;&nbsp;listen 443 ssl http2;<br/>
&nbsp;&nbsp;&nbsp;&nbsp;server_name {domain};<br/><br/>
&nbsp;&nbsp;&nbsp;&nbsp;# Let's Encrypt 인증서<br/>
&nbsp;&nbsp;&nbsp;&nbsp;ssl_certificate /etc/letsencrypt/live/{domain}/fullchain.pem;<br/>
&nbsp;&nbsp;&nbsp;&nbsp;ssl_certificate_key /etc/letsencrypt/live/{domain}/privkey.pem;<br/><br/>
&nbsp;&nbsp;&nbsp;&nbsp;# 보안 헤더<br/>
&nbsp;&nbsp;&nbsp;&nbsp;ssl_protocols TLSv1.2 TLSv1.3;<br/>
&nbsp;&nbsp;&nbsp;&nbsp;ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384;<br/>
&nbsp;&nbsp;&nbsp;&nbsp;ssl_prefer_server_ciphers off;<br/><br/>
&nbsp;&nbsp;&nbsp;&nbsp;# HSTS 헤더<br/>
&nbsp;&nbsp;&nbsp;&nbsp;add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;<br/>
&nbsp;&nbsp;&nbsp;&nbsp;add_header X-Frame-Options DENY always;<br/>
&nbsp;&nbsp;&nbsp;&nbsp;add_header X-Content-Type-Options nosniff always;<br/>
&nbsp;&nbsp;&nbsp;&nbsp;add_header Referrer-Policy "strict-origin-when-cross-origin" always;<br/><br/>
&nbsp;&nbsp;&nbsp;&nbsp;location / {{<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;proxy_pass http://localhost:8080;<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;proxy_set_header Host $host;<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;proxy_set_header X-Real-IP $remote_addr;<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;proxy_set_header X-Forwarded-Proto $scheme;<br/>
&nbsp;&nbsp;&nbsp;&nbsp;}}<br/>
}}<br/><br/>

<b># HTTP → HTTPS 리다이렉션</b><br/>
server {{<br/>
&nbsp;&nbsp;&nbsp;&nbsp;listen 80;<br/>
&nbsp;&nbsp;&nbsp;&nbsp;server_name {domain} www.{domain};<br/>
&nbsp;&nbsp;&nbsp;&nbsp;return 301 https://$server_name$request_uri;<br/>
}}
"""
            story.append(Paragraph(security_headers_config, code_style))
            story.append(Spacer(1, 15))
        
        # Phase 3: 고급 보안 구현
        story.append(Paragraph("Phase 3: 고급 보안 구현 (1개월 이내)", subsection_style))
        story.append(Paragraph("<b>우선순위</b>: ⭐⭐⭐⭐ (High)<br/>"
                             "<b>예상 비용</b>: 50-200만원<br/>"
                             "<b>예상 소요시간</b>: 2-4주", body_style))
        story.append(Spacer(1, 12))
        
        advanced_security = """<b>구현 항목</b>:

1. <b>웹 애플리케이션 방화벽 (WAF)</b>
   - SQL 인젝션 방어
   - XSS 공격 방어
   - DDoS 보호
   - 지역별 접근 제어

2. <b>보안 모니터링 시스템</b>
   - 실시간 보안 이벤트 탐지
   - SSL 인증서 만료 모니터링
   - 서버 성능 및 가용성 모니터링
   - 자동 알림 시스템

3. <b>백업 및 복구 시스템</b>
   - 일일 데이터베이스 백업
   - 웹사이트 파일 백업
   - 원격 저장소 보관
   - 복구 절차 문서화"""
        
        story.append(Paragraph(advanced_security, body_style))
        story.append(Spacer(1, 15))
        
        story.append(Paragraph("---", body_style))
        story.append(PageBreak())
        
        # ============= 비용 분석 및 ROI (TSC 형식) - 이모지 대신 텍스트 =============
        story.append(Paragraph("비용 분석 및 ROI", section_style))
        
        # 구현 비용 분석 (TSC 스타일)
        story.append(Paragraph("구현 비용 분석", subsection_style))
        
        # Phase 1 비용
        story.append(Paragraph("Phase 1: 긴급 조치", subheading_style))
        phase1_cost_data = [
            ['항목', '내부 작업', '외부 위탁', '비고'],
            ['서버 설정 수정', '0원', '30-50만원', '기술 지식 필요'],
            ['테스트 및 검증', '0원', '10-20만원', ''],
            ['소계', '0원', '40-70만원', '']
        ]
        
        phase1_table = Table(phase1_cost_data, colWidths=[1.5*inch, 1.3*inch, 1.3*inch, 1.4*inch])
        phase1_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), korean_bold_font),
            ('FONTNAME', (0, 1), (-1, -1), korean_font),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#95a5a6')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ffeaea')]),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(phase1_table)
        story.append(Spacer(1, 12))
        
        # Phase 2 비용
        story.append(Paragraph("Phase 2: 필수 보안", subheading_style))
        phase2_cost_data = [
            ['항목', '내부 작업', '외부 위탁', '비고'],
            ['Let\'s Encrypt 적용', '0원', '50-80만원', '무료 SSL'],
            ['기본 보안 설정', '0원', '30-50만원', ''],
            ['소계', '0원', '80-130만원', '']
        ]
        
        phase2_table = Table(phase2_cost_data, colWidths=[1.5*inch, 1.3*inch, 1.3*inch, 1.4*inch])
        phase2_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), korean_bold_font),
            ('FONTNAME', (0, 1), (-1, -1), korean_font),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f39c12')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#95a5a6')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fef9e7')]),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(phase2_table)
        story.append(Spacer(1, 12))
        
        # Phase 3 비용
        story.append(Paragraph("Phase 3: 고급 보안", subheading_style))
        phase3_cost_data = [
            ['항목', '연간 비용', '비고'],
            ['Cloudflare Pro', '24만원', 'CDN + WAF'],
            ['모니터링 도구', '60-120만원', 'Datadog, New Relic 등'],
            ['백업 스토리지', '12-24만원', 'AWS S3, Google Cloud'],
            ['소계', '96-168만원/년', '']
        ]
        
        phase3_table = Table(phase3_cost_data, colWidths=[2*inch, 1.5*inch, 2*inch])
        phase3_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), korean_bold_font),
            ('FONTNAME', (0, 1), (-1, -1), korean_font),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#95a5a6')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#e8f8f5')]),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(phase3_table)
        story.append(Spacer(1, 15))
        
        # ROI 분석 (TSC 스타일)
        story.append(Paragraph("ROI 분석", subsection_style))
        
        story.append(Paragraph("투자 대비 효과", subheading_style))
        
        roi_calculation = f"""
<b>투자 대비 효과 예상</b>:<br/><br/>
• 초기 투자비용: 140-370만원 (1년차)<br/>
• 연간 운영비용: 96-168만원<br/><br/>

<b>예상 효과</b>:<br/>
- 트래픽 회복: 월 {monthly_loss_visitors:,}명 → 년 {annual_revenue_loss:,.0f}원 매출 기여<br/>
- SEO 개선: 추가 20% 트래픽 증가<br/>
- 브랜드 신뢰도: 정량화 어렵지만 상당한 가치<br/><br/>

<b>ROI 계산</b>:<br/>
- 투자비용: 370만원 (최대)<br/>
- 수익개선: {annual_revenue_loss:,.0f}원 (최소)<br/>
- ROI: {int(annual_revenue_loss/3700000*100) if annual_revenue_loss > 0 else 100}% ({int(annual_revenue_loss/3700000) if annual_revenue_loss > 3700000 else 1}배)
"""
        story.append(Paragraph(roi_calculation, body_style))
        story.append(Spacer(1, 15))
        
        # 비용 효과 비교
        story.append(Paragraph("비용 효과 비교", subheading_style))
        
        roi_comparison_data = [
            ['구분', '현재 상황', '개선 후', '차이'],
            ['월 방문자', f'{monthly_visitors - monthly_loss_visitors:,}명', f'{monthly_visitors:,}명+', f'+{int((monthly_loss_visitors/monthly_visitors)*100)}%+'],
            ['브랜드 신뢰도', '낮음', '높음', '질적 개선'],
            ['검색 순위', '하락 중' if ssl_grade == 'F' else '보통', '상승', 'SEO 개선'],
            ['보안 위험', '높음' if ssl_grade == 'F' else '중간', '낮음', '리스크 감소']
        ]
        
        roi_comparison_table = Table(roi_comparison_data, colWidths=[1.3*inch, 1.5*inch, 1.5*inch, 1.2*inch])
        roi_comparison_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), korean_bold_font),
            ('FONTNAME', (0, 1), (-1, -1), korean_font),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#95a5a6')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ebf3fd')]),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(roi_comparison_table)
        story.append(Spacer(1, 15))
        
        story.append(Paragraph("---", body_style))
        story.append(PageBreak())
        
        # ============= 구현 로드맵 (TSC 형식) - 이모지 대신 텍스트 =============
        story.append(Paragraph("구현 로드맵", section_style))
        
        # Week 1: 응급 처치
        story.append(Paragraph("Week 1: 응급 처치", subsection_style))
        week1_plan = """- <b>Day 1-2</b>: 현 상황 정확한 진단 및 임시 수정
- <b>Day 3-4</b>: nginx 설정 개선 및 테스트  
- <b>Day 5-7</b>: 모니터링 및 안정성 확인"""
        story.append(Paragraph(week1_plan, body_style))
        story.append(Spacer(1, 10))
        
        # Week 2: 핵심 보안 구축
        story.append(Paragraph("Week 2: 핵심 보안 구축", subsection_style))
        week2_plan = """- <b>Day 8-10</b>: Let's Encrypt SSL 인증서 적용
- <b>Day 11-12</b>: 보안 헤더 및 HTTPS 리다이렉션 설정
- <b>Day 13-14</b>: 전체 시스템 테스트 및 검증"""
        story.append(Paragraph(week2_plan, body_style))
        story.append(Spacer(1, 10))
        
        # Week 3-4: 성능 및 모니터링
        story.append(Paragraph("Week 3-4: 성능 및 모니터링", subsection_style))
        week3_4_plan = """- <b>Week 3</b>: Cloudflare CDN 적용 및 성능 최적화
- <b>Week 4</b>: 모니터링 시스템 구축 및 알림 설정"""
        story.append(Paragraph(week3_4_plan, body_style))
        story.append(Spacer(1, 10))
        
        # Month 2-3: 고도화
        story.append(Paragraph("Month 2-3: 고도화", subsection_style))
        month2_3_plan = """- <b>Month 2</b>: WAF 규칙 최적화, 백업 시스템 구축
- <b>Month 3</b>: 성능 분석 및 추가 최적화"""
        story.append(Paragraph(month2_3_plan, body_style))
        story.append(Spacer(1, 10))
        
        # Ongoing: 운영 및 관리
        story.append(Paragraph("Ongoing: 운영 및 관리", subsection_style))
        ongoing_plan = """- <b>주간</b>: 보안 업데이트 및 모니터링 리뷰
- <b>월간</b>: 종합 보안 점검 및 성능 리포트
- <b>분기</b>: 보안 정책 검토 및 개선사항 도출"""
        story.append(Paragraph(ongoing_plan, body_style))
        story.append(Spacer(1, 15))
        
        story.append(Paragraph("---", body_style))
        story.append(PageBreak())
        
        # ============= 성공 기준 및 KPI (TSC 형식) - 이모지 대신 텍스트 =============
        story.append(Paragraph("성공 기준 및 KPI", section_style))
        
        # 기술적 KPI
        story.append(Paragraph("기술적 KPI", subsection_style))
        tech_kpi = f"""1. <b>SSL Labs 등급</b>: {ssl_grade} → A+ (목표)
2. <b>웹사이트 가용성</b>: 95% → 99.9%
3. <b>페이지 로딩 속도</b>: 현재 → 3초 이내  
4. <b>보안 취약점</b>: 현재 위험 → 0개 유지"""
        story.append(Paragraph(tech_kpi, body_style))
        story.append(Spacer(1, 12))
        
        # 비즈니스 KPI
        story.append(Paragraph("비즈니스 KPI", subsection_style))
        business_kpi = f"""1. <b>월 방문자 수</b>: {monthly_visitors - monthly_loss_visitors:,}명 → {monthly_visitors:,}명+
2. <b>브랜드 신뢰도</b>: 정성적 개선 측정
3. <b>문의 전환율</b>: 현재 → 20% 개선 목표
4. <b>검색 순위</b>: 주요 키워드 10-20% 순위 향상"""
        story.append(Paragraph(business_kpi, body_style))
        story.append(Spacer(1, 12))
        
        # 측정 방법
        story.append(Paragraph("측정 방법", subsection_style))
        measurement_tools = """
<b>모니터링 도구</b>:<br/>
- Google Analytics: 트래픽 분석<br/>
- Google Search Console: SEO 성과<br/>
- SSL Labs: SSL 등급 모니터링<br/>
- GTmetrix: 성능 분석<br/>
- Uptime Robot: 가용성 모니터링
"""
        story.append(Paragraph(measurement_tools, body_style))
        story.append(Spacer(1, 15))
        
        story.append(Paragraph("---", body_style))
        story.append(PageBreak())
        
        # ============= 결론 및 제언 (TSC 형식) - 이모지 대신 텍스트 =============
        story.append(Paragraph("결론 및 제언", section_style))
        
        # 핵심 결론
        story.append(Paragraph("핵심 결론", subsection_style))
        
        if ssl_grade == 'F' or not certificate_valid:
            core_conclusion = f"""
{domain} 웹사이트의 현재 보안 상태는 <b>즉시 개선이 필요한 심각한 수준</b>입니다. 
SSL 인증서 문제와 HTTPS 서비스 중단은 고객 신뢰도와 비즈니스 성과에 직접적인 
악영향을 미치고 있으며, 이는 <b>연간 {annual_revenue_loss:,.0f}원 이상의 기회비용</b>을 
발생시킬 수 있습니다.
"""
        elif ssl_grade in ['D', 'C']:
            core_conclusion = f"""
{domain} 웹사이트는 기본적인 SSL은 적용되어 있으나 <b>추가적인 보안 강화가 필요한 상태</b>입니다. 
현재 상태에서도 일정한 비즈니스 리스크가 존재하므로 체계적인 개선이 권장됩니다.
"""
        else:
            core_conclusion = f"""
{domain} 웹사이트의 보안 상태는 전반적으로 양호한 수준입니다. 
지속적인 모니터링과 관리를 통해 현재 수준을 유지하고 더욱 발전시키시기 바랍니다.
"""
        
        story.append(Paragraph(core_conclusion, body_style))
        story.append(Spacer(1, 12))
        
        # 권장 접근법
        story.append(Paragraph("권장 접근법", subsection_style))
        approach_text = """1. <b>단계적 접근</b>: 긴급 → 필수 → 고도화 순서로 진행
2. <b>비용 효율성</b>: Let's Encrypt 무료 SSL로 핵심 문제 해결
3. <b>전문가 협력</b>: 내부 역량 부족시 외부 전문가 활용
4. <b>지속적 관리</b>: 일회성이 아닌 지속적 보안 관리 체계 구축"""
        story.append(Paragraph(approach_text, body_style))
        story.append(Spacer(1, 12))
        
        # 기대 효과
        story.append(Paragraph("기대 효과", subsection_style))
        expected_effects = """• <b>즉시 효과</b>: 브라우저 경고 제거, 사용자 경험 개선
• <b>단기 효과</b>: 웹사이트 트래픽 30-50% 증가
• <b>장기 효과</b>: 브랜드 신뢰도 향상, 검색 순위 개선, 매출 증대"""
        story.append(Paragraph(expected_effects, body_style))
        story.append(Spacer(1, 12))
        
        # 최종 권고
        story.append(Paragraph("최종 권고", subsection_style))
        if ssl_grade in ['F', 'D']:
            final_recommendation = f"""
<b>지금 즉시 행동하십시오.</b> 하루 늦을수록 고객 신뢰와 비즈니스 기회가 계속 손실됩니다. 
이 보고서의 Phase 1, 2 권장사항은 <b>1주일 내에 완료 가능</b>하며, 
<b>투자 대비 효과는 100배 이상</b>입니다.

{domain}이 해당 분야의 기술적 우수성을 웹사이트 보안에도 반영하여, 
디지털 시대에 걸맞는 신뢰할 수 있는 기업으로 거듭날 수 있기를 기대합니다.
"""
        else:
            final_recommendation = """
현재 상태를 유지하면서 지속적인 개선을 통해 보안 수준을 더욱 강화하시기 바랍니다. 
정기적인 점검과 최신 보안 동향 반영을 통해 경쟁력을 유지하시기 바랍니다.
"""
        story.append(Paragraph(final_recommendation, body_style))
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("---", body_style))
        story.append(Spacer(1, 15))
        
        # 푸터 (TSC 스타일)
        footer_text = f"""
<b>보고서 문의</b>: 원클릭SSL Security Analysis Team<br/>
<b>긴급 연락</b>: [보안 문제 발견시 즉시 연락]<br/>
<b>다음 점검 예정</b>: 권장사항 이행 후 1주일 뒤 재점검<br/><br/>

---<br/><br/>

<i>이 보고서는 {datetime.now().strftime("%Y년 %m월 %d일")} 현재 상황을 기준으로 작성되었으며, 
실제 구현시 최신 보안 동향을 반영하여 업데이트가 필요할 수 있습니다.</i>
"""
        story.append(Paragraph(footer_text, body_style))
        
        # PDF 생성
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
        
    except Exception as e:
        print(f"PDF 생성 오류: {str(e)}")
        # 오류 발생시 간단한 오류 보고서 생성
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        
        error_story = [
            Paragraph("보안 분석 보고서 생성 오류", styles['Title']),
            Spacer(1, 20),
            Paragraph(f"도메인: {analysis_data.get('domain', 'Unknown')}", styles['Normal']),
            Paragraph(f"오류: {str(e)}", styles['Normal']),
        ]
        
        doc.build(error_story)
        buffer.seek(0)
        return buffer.getvalue()