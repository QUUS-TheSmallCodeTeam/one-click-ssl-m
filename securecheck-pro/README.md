# 원클릭SSL

웹사이트 URL을 입력하면 종합 보안 분석 보고서가 자동으로 생성되는 웹 애플리케이션입니다.

## 기술 스택

- **Frontend**: Next.js 14, React, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python, Playwright
- **Database**: PostgreSQL
- **Cache**: Redis
- **Deployment**: Docker

## 프로젝트 구조

```
securecheck-pro/
├── frontend/          # Next.js 프론트엔드
├── backend/           # FastAPI 백엔드
├── shared/            # 공통 타입 정의 및 유틸리티
├── docker-compose.yml # 개발 환경 설정
└── README.md
```

## 빠른 시작

```bash
# 개발 환경 실행
docker-compose up -dev

# 또는 개별 실행
cd frontend && npm run dev
cd backend && uvicorn main:app --reload
```

## 주요 기능

1. **URL 입력** → SSL/보안 분석 실행
2. **실시간 분석** → 브라우저 자동화로 실제 보안 상태 확인  
3. **보고서 생성** → PDF 보고서 자동 생성
4. **비즈니스 영향 분석** → ROI 계산 및 개선 제안

## API 엔드포인트

- `POST /api/v1/analyze` - 웹사이트 보안 분석 실행
- `GET /api/v1/reports/{report_id}` - 보고서 조회
- `GET /api/v1/reports/{report_id}/download` - PDF 다운로드