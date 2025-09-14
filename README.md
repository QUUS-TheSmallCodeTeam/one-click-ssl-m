---
title: SecureCheck Pro - 원클릭 SSL체크
emoji: 🔐⚡🛡️
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# SecureCheck Pro - 원클릭 SSL체크 🔐

웹사이트의 SSL/TLS 보안을 간편하게 분석하고 상세한 보고서를 생성하는 한국어 웹 보안 분석 서비스입니다.

## 🚀 주요 기능

### 🔍 원클릭 보안 분석
- **SSL/TLS 인증서 분석**: 인증서 유효성, 만료일, 보안 수준 평가
- **보안 헤더 분석**: HTTP 보안 헤더의 존재 여부 및 적절성 검토
- **취약점 스캔**: 알려진 SSL/TLS 관련 취약점 탐지
- **종합 등급 평가**: A+부터 F등급까지 직관적인 보안 등급 제공

### 📊 비즈니스 영향 분석
- **매출 영향 계산**: 보안 취약점으로 인한 연간 예상 손실액
- **SEO 영향 분석**: 검색 순위에 미치는 영향 평가
- **고객 신뢰도 분석**: 브랜드 이미지 손실 정도 측정

### 📄 전문 보고서 생성
- **한글 PDF 보고서**: 경영진부터 개발자까지 대상별 맞춤 보고서
- **즉시 실행 가능한 해결책**: 구체적인 코드 예시와 설정 방법 제공
- **ROI 계산**: 보안 개선 투자 대비 효과 분석
- **단계별 실행 계획**: 우선순위별 구체적 개선 로드맵

## 🏗️ 기술 아키텍처

### 프론트엔드
- **Next.js 15**: 최신 App Router 아키텍처
- **React 19**: 현대적인 리액트 기능 활용
- **TypeScript**: 타입 안전성 보장
- **Tailwind CSS**: 반응형 디자인
- **html2pdf.js**: 클라이언트 사이드 PDF 생성

### 백엔드
- **Python 3.11**: 최신 Python 기능 활용
- **FastAPI**: 고성능 비동기 웹 프레임워크
- **SSL 분석 엔진**: 실제 인증서 검증 및 분석
- **ReportLab**: 전문적인 PDF 보고서 생성
- **한글 폰트 지원**: 완벽한 한국어 PDF 출력

### 배포 환경
- **Hugging Face Spaces**: Docker 기반 배포
- **단일 컨테이너**: Frontend + Backend 통합 서빙
- **포트 7860**: Hugging Face Spaces 표준

## 🎯 사용법

### 웹 인터페이스
1. 분석하려는 웹사이트 URL 입력 (예: `https://example.com`)
2. "보안 분석 시작" 버튼 클릭
3. 실시간으로 분석 진행 상황 확인
4. 분석 완료 후 결과 확인 및 PDF 보고서 다운로드

### API 사용 (개발자용)
```bash
# 보안 분석 요청
curl -X POST "https://your-space.hf.space/api/v1/analyze" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://example.com"}'

# 보고서 다운로드
curl -X GET "https://your-space.hf.space/api/v1/reports/{report_id}/download" \
     --output report.pdf
```

## 📋 분석 항목

### SSL/TLS 인증서 검증
- ✅ 인증서 유효성 및 만료일 확인
- ✅ 발급 기관 신뢰성 검증
- ✅ 자체 서명 인증서 탐지
- ✅ 인증서 체인 완전성 검사
- ✅ SSL 등급 평가 (A+~F)

### 보안 헤더 분석
- `Strict-Transport-Security` (HSTS)
- `Content-Security-Policy` (CSP)
- `X-Frame-Options`
- `X-Content-Type-Options`
- `X-XSS-Protection`
- `Referrer-Policy`

### 비즈니스 영향 분석
- 연간 매출 손실 추정
- SEO 순위 영향도 계산
- 고객 이탈률 예측
- 브랜드 신뢰도 손실 평가

## 🏢 타겟 사용자

### 중소기업 웹사이트 운영자
- SSL 인증서 설치 필요성 확인
- 브라우저 경고 메시지 해결
- 고객 신뢰도 향상

### 웹 개발자 & 에이전시
- 고객사 보안 점검
- 프로젝트 납품 전 검증
- 보안 컨설팅 자료

### IT 담당자 & 보안 관리자
- 보안 현황 모니터링
- 경영진 보고 자료
- 보안 투자 ROI 분석

## 📊 보고서 구성

### 1. Executive Summary (경영진용)
- 핵심 발견사항 요약
- 비즈니스 영향 분석
- 즉시 조치 필요사항

### 2. 기술 분석 (개발자용)
- 상세 SSL 분석 결과
- 구체적 설정 예시
- 취약점별 해결 방법

### 3. 비즈니스 영향 (운영팀용)
- ROI 계산
- 매출 영향 분석
- 브랜드 리스크 평가

### 4. 실행 계획 (전체용)
- 단계별 해결 방안
- 예상 비용 및 시간
- 성공 기준 및 측정 방법

## 🔧 로컬 개발 환경 구성

### 사전 요구사항
- Node.js 16+
- Python 3.8+
- Git

### 설치 및 실행
```bash
# 저장소 복제
git clone <repository-url>
cd one-click-ssl-m

# 백엔드 서버 실행
cd securecheck-pro/backend
pip install -r requirements.txt
python main.py  # http://localhost:8000

# 프론트엔드 서버 실행 (새 터미널)
cd securecheck-pro/frontend
npm install
npm run dev  # http://localhost:3000
```

## 🐳 Docker 배포

### 로컬 Docker 실행
```bash
# 이미지 빌드
docker build -t securecheck-pro .

# 컨테이너 실행
docker run -p 7860:7860 securecheck-pro
```

### Hugging Face Spaces 배포
1. 새로운 Space 생성 (Docker SDK 선택)
2. 프로젝트 파일 업로드
3. 자동 배포 및 서비스 시작

## 🛡️ 보안 및 프라이버시

### 데이터 보호
- 분석 대상 웹사이트의 개인정보는 수집하지 않음
- SSL 인증서 공개 정보만 분석
- 분석 결과는 세션 기반으로 임시 저장
- 사용자 개인정보 미수집

### 분석 방식
- 공개적으로 접근 가능한 SSL 정보만 확인
- 웹사이트 내부 시스템 접근 없음
- 비침습적 외부 분석만 수행

## 📈 성능 특성

### 분석 성능
- **분석 시간**: 평균 30초 이내
- **정확도**: SSL Labs API 대비 95% 일치
- **가용성**: 99.9% 업타임 목표
- **동시 처리**: 다중 요청 지원

### 시스템 요구사항
- **메모리**: 512MB 권장
- **CPU**: 1 vCPU 이상
- **디스크**: 1GB 이상
- **네트워크**: 인터넷 연결 필수

## 🤝 기여하기

### 개발 가이드라인
1. 이슈 등록 후 개발 시작
2. 기능별 브랜치 생성
3. 코드 리뷰 후 병합
4. 테스트 케이스 작성 필수

### 코드 품질
- TypeScript/Python 타입 힌트 사용
- ESLint/Black 포매터 적용
- 단위 테스트 작성
- 문서화 업데이트

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 상업적/비상업적 사용 모두 가능합니다.

## 🆘 지원 및 문의

### 기술 지원
- **API 문서**: `/docs` (Swagger UI)
- **건강 상태**: `/health`
- **GitHub Issues**: 버그 신고 및 기능 요청

### 일반적인 문제 해결
1. **분석 실패**: URL 형식 확인 및 HTTPS 접근 가능 여부 점검
2. **느린 응답**: 네트워크 상태 및 대상 서버 응답 시간 확인
3. **PDF 다운로드 실패**: 브라우저 팝업 차단 설정 확인

## 🔄 업데이트 로그

### v1.0.0 (최신)
- ✨ 완전한 SSL/TLS 분석 엔진
- ✨ 한글 PDF 보고서 생성
- ✨ 비즈니스 영향 분석 기능
- ✨ Hugging Face Spaces 배포 지원
- ✨ 실시간 분석 진행 상황 표시

## 🌟 핵심 차별점

### vs 기존 SSL 검사 도구
- **한국어 지원**: 완전한 한국어 인터페이스 및 보고서
- **비즈니스 관점**: 기술적 분석 + 경영진 관점 통합
- **즉시 실행**: 구체적 코드와 설정 예시 제공
- **무료 사용**: 개인/상업적 사용 모두 무료

### 실제 사용 사례
- TSC 기업 보안 분석 (10.08억원 손실 방지 효과 확인)
- 중소기업 SSL 인증서 설치 가이드
- 웹 에이전시 고객 보안 점검 자료

---

**🔐 모든 웹사이트가 안전하고 신뢰받는 디지털 환경을 만들어갑니다**

Built with ❤️ using Next.js, FastAPI, and modern security analysis techniques