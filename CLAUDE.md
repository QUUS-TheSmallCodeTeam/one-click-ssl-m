# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

원클릭SSL is a Korean web security analysis service that performs comprehensive SSL/TLS analysis and generates professional security reports in PDF format. The service is built as a full-stack application with a Next.js frontend and FastAPI backend, designed for deployment on Hugging Face Spaces.

## Development Commands

### Frontend (Next.js)
```bash
cd securecheck-pro/frontend
npm install                    # Install dependencies
npm run dev                    # Start development server (port 3000)
npm run build                  # Build for production
npm run lint                   # Run ESLint
```

### Backend (FastAPI)
```bash
cd securecheck-pro/backend
pip install -r requirements.txt   # Install Python dependencies
python main.py                    # Start development server (port 8000)
# OR
uvicorn main:app --reload        # Alternative start command
```

### Full Stack Development
Both servers need to be running simultaneously:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

## Architecture Overview

### Core Components

**Backend (FastAPI)**
- `main.py` - Main API server with CORS configuration for frontend communication
- `ssl_analyzer.py` - Core SSL/TLS analysis engine implementing real certificate validation
- `report_generator_tsc.py` - Professional PDF report generation with Korean support
- Memory-based result storage (analysis_results dict) for demo purposes

**Frontend (Next.js 13+)**
- App Router architecture (`src/app/`)
- `SecurityAnalyzer.tsx` - Main analysis interface component
- `SecurityReport.tsx` - Results display and PDF download
- TypeScript with Tailwind CSS styling

**Reference Implementation**
- `/ssl-checker/` - Contains reference SSL checker logic and implementation patterns
- Can be used as a reference for SSL analysis algorithms and validation approaches

### Key API Endpoints

- `POST /api/v1/analyze` - Main security analysis endpoint
- `GET /api/v1/reports/{report_id}/download` - PDF report download
- `GET /` - Serves static frontend files

### Analysis Flow

1. **URL Input** → Frontend sends request to `/api/v1/analyze`
2. **SSL Analysis** → Backend uses `SSLAnalyzer` class to:
   - Test port 443 connectivity
   - Extract and validate SSL certificates
   - Check security headers
   - Calculate security scores and grades
3. **Report Generation** → Creates structured analysis data for PDF generation
4. **PDF Download** → TSC-style professional reports with Korean fonts

### Security Analysis Engine

The `SSLAnalyzer` class implements a comprehensive analysis methodology:

- **Port Testing**: Socket-based 443 port connectivity check
- **Certificate Analysis**: Real SSL certificate extraction and validation
- **Security Headers**: Checks 6 critical security headers
- **Grading System**: A+ to F grading based on multiple factors
- **Business Impact**: Calculates revenue loss and SEO impact

### Report Generation

Professional PDF reports include:
- Executive Summary (business impact focus)
- Technical Analysis (detailed security findings)
- Business Impact Analysis (ROI calculations)
- Implementation Roadmap (step-by-step fixes)

## Development Notes

### Known Architecture Decisions

- **Memory Storage**: Uses in-memory dict for analysis results (suitable for demo/HF Spaces)
- **CORS Policy**: Allows all origins (`"*"`) for Hugging Face deployment compatibility
- **Static File Serving**: FastAPI serves Next.js build output for single-container deployment
- **Korean Language**: All user-facing content is in Korean, targeting domestic market

### Important File Dependencies

- PDF generation requires `reportlab` with Korean font support
- SSL analysis uses Python's built-in `ssl` library with custom verification logic
- Frontend uses modern Next.js 15.5.2 with React 19.1.0
- No external databases - all data is ephemeral

### Deployment Configuration

The application is configured for Hugging Face Spaces deployment:
- Single container serves both frontend and backend
- Port 7860 (HF Spaces standard)
- CORS configured for cross-origin requests
- Static file mounting for production builds

### Common Development Tasks

**Adding New Security Checks**: Extend `SSLAnalyzer.security_headers` list and update analysis logic in `_analyze_security_headers()`

**Modifying PDF Reports**: Edit `report_generator_tsc.py` - contains full report template with Korean business language

**Frontend UI Changes**: Components are in `securecheck-pro/frontend/src/components/`

**API Modifications**: Main API logic is in `main.py` with helper functions for scoring and business impact calculations

## Git Configuration

The project uses a hierarchical `.gitignore` structure:
- Root `.gitignore`: Contains `.claude/settings.local.json`
- `securecheck-pro/.gitignore`: Contains application-specific ignores (node_modules, build outputs, etc.)