'use client';

interface AnalysisResult {
  id: string;
  url: string;
  ssl_grade: string;
  security_score: number;
  issues: Array<{
    type: string;
    severity: 'low' | 'medium' | 'high' | 'critical';
    title: string;
    description: string;
  }>;
  business_impact: {
    revenue_loss_annual: number;
    seo_impact: number;
    user_trust_impact: number;
  };
  recommendations: string[];
  created_at: string;
}

interface SecurityReportProps {
  data: AnalysisResult;
}


const getScoreColor = (score: number) => {
  if (score >= 90) return 'text-green-600';
  if (score >= 70) return 'text-yellow-600';
  if (score >= 50) return 'text-orange-600';
  return 'text-red-600';
};

export function SecurityReport({ data }: SecurityReportProps) {
  const handleDownloadPDF = async () => {
    // 현재 활성 요소를 저장하여 나중에 복원
    const activeElement = document.activeElement as HTMLElement;

    try {
      // Get saved analysis data from localStorage
      const savedData = localStorage.getItem('latestAnalysisData');
      if (!savedData) {
        alert('분석 데이터를 찾을 수 없습니다. 먼저 웹사이트를 분석해주세요.');
        return;
      }

      const analysisData = JSON.parse(savedData);

      // Try to use html2pdf.js, fallback to HTML download if it fails
      try {
        // Dynamically import html2pdf.js
        // @ts-expect-error - html2pdf.js has no TypeScript definitions
        const html2pdf = (await import('html2pdf.js')).default;

        // Create a temporary container for PDF generation in a more isolated way
        const tempContainer = document.createElement('div');
        tempContainer.innerHTML = generatePDFContent(analysisData);
        tempContainer.style.cssText = `
          position: absolute !important;
          left: -9999px !important;
          top: -9999px !important;
          z-index: -9999 !important;
          visibility: hidden !important;
          pointer-events: none !important;
        `;

        // Append to body but with more isolation
        document.body.appendChild(tempContainer);

        // Configure html2pdf with page breaks
        const opt = {
          margin: 0.5,
          filename: `security-report-${analysisData.url.replace(/https?:\/\//, '')}.pdf`,
          image: { type: 'jpeg', quality: 0.92 },
          html2canvas: {
            scale: 1.5,
            useCORS: true,
            allowTaint: true,
            backgroundColor: '#ffffff'
          },
          jsPDF: {
            unit: 'in',
            format: 'a4',
            orientation: 'portrait',
            compress: true
          },
          pagebreak: {
            mode: ['css', 'legacy'],
            before: '.page-break-before',
            after: '.page-break-after',
            avoid: '.page-break-avoid'
          }
        };

        // Generate and download PDF
        await html2pdf().set(opt).from(tempContainer).save();

        // Immediate cleanup
        if (document.body.contains(tempContainer)) {
          document.body.removeChild(tempContainer);
        }

        alert('📄 보안 분석 보고서가 PDF로 다운로드되었습니다!');
      } catch (html2pdfError) {
        console.warn('html2pdf.js failed, falling back to HTML download:', html2pdfError);

        // Fallback: Download as HTML file that can be printed to PDF
        const pdfContent = generatePDFContent(analysisData);
        const blob = new Blob([pdfContent], { type: 'text/html' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `security-report-${analysisData.url.replace(/https?:\/\//, '')}.html`;

        // Create temporary link with better isolation
        a.style.cssText = 'position: absolute; left: -9999px; visibility: hidden;';
        document.body.appendChild(a);
        a.click();

        // Immediate cleanup
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        alert('📄 보안 분석 보고서가 HTML 형식으로 다운로드되었습니다!\n\n브라우저에서 열어서 PDF로 인쇄하실 수 있습니다.');
      }
    } catch (error) {
      console.error('PDF 다운로드 오류:', error);
      alert(`PDF 다운로드 중 오류가 발생했습니다: ${error instanceof Error ? error.message : '알 수 없는 오류'}`);
    } finally {
      // 원래 활성 요소로 focus 복원 (비동기 작업 후)
      setTimeout(() => {
        if (activeElement && activeElement.focus) {
          activeElement.focus();
        }
      }, 100);
    }
  };


  const generatePDFContent = (data: AnalysisResult): string => {
    const domain = data.url.replace(/https?:\/\//, '').replace(/\/$/, '');
    const analysisDate = new Date(data.created_at).toLocaleDateString('ko-KR');
    
    return `<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${domain.toUpperCase()} 웹사이트 보안 분석 보고서</title>
    <style>
        @page { size: A4; margin: 1in; }
        body { 
            font-family: 'Noto Sans KR', 'Malgun Gothic', Arial, sans-serif; 
            font-size: 11px; line-height: 1.6; color: #333; margin: 0; padding: 0; 
        }
        h1 { font-size: 22px; font-weight: bold; color: #1a365d; margin-bottom: 10px; }
        h2 { font-size: 16px; font-weight: bold; color: #2b77ad; margin: 15px 0 8px 0; 
             padding-left: 12px; border-left: 4px solid #2b77ad; }
        h3 { font-size: 14px; font-weight: bold; color: #4a5568; margin: 12px 0 8px 0; }
        h4 { font-size: 12px; font-weight: bold; color: #718096; margin: 10px 0 6px 0; }
        .report-header { background: #667eea; 
                         color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .report-meta { display: flex; justify-content: space-between; align-items: flex-end; 
                       flex-wrap: wrap; gap: 15px; }
        .report-meta p { margin: 0; font-size: 10px; opacity: 0.9; }
        .security-grade { display: inline-block; padding: 8px 16px; border-radius: 6px; 
                          font-weight: bold; font-size: 14px; color: white; text-align: center; 
                          min-width: 50px; }
        .grade-aplus, .grade-a { background: #48bb78; }
        .grade-b { background: #f6e05e; color: #1a202c; }
        .grade-c { background: #f6ad55; }
        .grade-d, .grade-f { background: #e53e3e; }
        .executive-summary { background: #f7fafc; padding: 15px; border-radius: 10px; 
                            margin-bottom: 15px; }
        .metrics-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; 
                       margin: 10px 0; }
        .metric-card { background: white; padding: 8px 15px; border-radius: 6px; text-align: center; 
                      border: 2px solid #e2e8f0; }
        .metric-card.critical { border-color: #e53e3e; background: #fed7d7; }
        .metric-card.warning { border-color: #f6e05e; background: #fefcbf; }
        .metric-card.normal { border-color: #48bb78; background: #c6f6d5; }
        .metric-number { font-size: 16px; font-weight: bold; color: #e53e3e; margin-bottom: 5px; 
                        display: block; }
        .metric-card.normal .metric-number { color: #38a169; }
        .metric-label { font-size: 10px; font-weight: bold; color: #4a5568; margin-bottom: 3px; 
                       display: block; }
        .issue-item { background: #fff; border: 1px solid #ddd; border-radius: 5px; 
                     padding: 10px; margin: 6px 0; }
        .issue-critical { border-left: 4px solid #e74c3c; }
        .issue-high { border-left: 4px solid #f39c12; }
        .issue-medium { border-left: 4px solid #f1c40f; }
        .issue-low { border-left: 4px solid #27ae60; }
        .severity { display: inline-block; padding: 4px 8px; border-radius: 4px; 
                   font-size: 12px; font-weight: bold; margin-right: 10px; }
        .severity-critical { background: #e74c3c; color: white; }
        .severity-high { background: #f39c12; color: white; }
        .severity-medium { background: #f1c40f; color: #333; }
        .severity-low { background: #27ae60; color: white; }
        .recommendation { background: #e8f4fd; border: 1px solid #3498db; border-radius: 5px; 
                         padding: 8px 15px; margin: 6px 0; }
        .business-impact { background: #fff5f5; border: 1px solid #e74c3c; border-radius: 5px; 
                          padding: 15px; margin: 12px 0; }
        .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; 
                 text-align: center; color: #666; font-size: 14px; }
        .page-break-before { page-break-before: always; }
        .page-break-after { page-break-after: always; }
        .page-break-avoid { page-break-inside: avoid; }
        @media print { body { font-size: 10px; } .no-print { display: none !important; } }
    </style>
</head>
<body>
    <div class="report-header">
        <h1>${domain.toUpperCase()} 웹사이트 보안 및 서버 설정 문제 분석 보고서</h1>
        <div class="report-meta">
            <div>
                <p><strong>분석 대상:</strong> ${data.url}</p>
                <p><strong>분석 일시:</strong> ${analysisDate}</p>
            </div>
            <div>
                <p><strong>분석자:</strong> SecureCheck Pro Security Analysis Team</p>
                <p><strong>보고서 버전:</strong> 1.0</p>
            </div>
        </div>
    </div>

    <div class="executive-summary">
        <h2>📋 Executive Summary</h2>
        <p>${domain} 웹사이트에 대한 보안 분석 결과, <strong>중대한 SSL 인증서 및 서버 설정 문제</strong>가 발견되었습니다. 현재 HTTPS 연결이 정상 작동하지 않아 고객의 개인정보 보호와 브랜드 신뢰도에 부정적 영향을 미치고 있습니다.</p>
        
        <h3>🚨 주요 발견사항</h3>
        <div class="metrics-grid">
            <div class="metric-card ${data.ssl_grade === 'F' ? 'critical' : data.ssl_grade === 'D' ? 'warning' : 'normal'}">
                <span class="metric-label">SSL 등급</span>
                <span class="metric-number">${data.ssl_grade}</span>
            </div>
            <div class="metric-card ${data.security_score < 50 ? 'critical' : data.security_score < 80 ? 'warning' : 'normal'}">
                <span class="metric-label">보안 점수</span>
                <span class="metric-number">${data.security_score}/100</span>
            </div>
            <div class="metric-card critical">
                <span class="metric-label">발견된 문제</span>
                <span class="metric-number">${data.issues.length}개</span>
            </div>
            <div class="metric-card critical">
                <span class="metric-label">예상 연간 손실</span>
                <span class="metric-number">₩${data.business_impact.revenue_loss_annual.toLocaleString()}</span>
            </div>
        </div>

        <h3>💰 비즈니스 영향</h3>
        <ul>
            <li><strong>고객 신뢰도 하락:</strong> 브라우저 보안 경고로 인한 사용자 이탈 위험</li>
            <li><strong>SEO 불이익:</strong> Google 검색 순위 하락 가능성</li>
            <li><strong>전문성 의심:</strong> 기술 기업으로서의 신뢰도 손상</li>
            <li><strong>법적 리스크:</strong> 개인정보보호법 준수 미흡</li>
        </ul>

        <h3>🎯 권장 조치 (우선순위별)</h3>
        <ol>
            <li><strong>긴급:</strong> HTTPS 서버 설정 수정 (1일 이내)</li>
            <li><strong>필수:</strong> Let's Encrypt 무료 SSL 인증서 적용 (1주 이내)</li>
            <li><strong>권장:</strong> 보안 강화 및 모니터링 시스템 구축 (1개월 이내)</li>
        </ol>
    </div>

    <h2 class="page-break-before">🔍 상세 기술 분석</h2>
    
    <h3>1. SSL 인증서 상태 분석</h3>
    <h4>현재 인증서 정보</h4>
    <div style="background: #f7fafc; padding: 12px; border-radius: 4px; border: 1px solid #e2e8f0; font-family: monospace; font-size: 10px;">
        Domain: ${domain}<br/>
        Valid: ${data.ssl_grade !== 'F' ? 'Yes' : 'No'}<br/>
        SSL Grade: ${data.ssl_grade}<br/>
        Security Score: ${data.security_score}/100
    </div>

    <h4>📊 문제점 분석</h4>
    <table style="width: 100%; border-collapse: collapse; margin: 8px 0; font-size: 9px; background: white; border: 1px solid #e2e8f0; border-radius: 6px; overflow: hidden;">
        <thead>
            <tr style="background: #667eea; color: white;">
                <th style="padding: 6px; text-align: left; font-weight: bold;">항목</th>
                <th style="padding: 6px; text-align: left; font-weight: bold;">현재 상태</th>
                <th style="padding: 6px; text-align: left; font-weight: bold;">문제점</th>
                <th style="padding: 6px; text-align: left; font-weight: bold;">위험도</th>
            </tr>
        </thead>
        <tbody>
            <tr style="background: #f7fafc;">
                <td style="padding: 6px; border-bottom: 1px solid #f1f5f9;">인증서 타입</td>
                <td style="padding: 6px; border-bottom: 1px solid #f1f5f9;">${data.ssl_grade === 'F' ? '검증 실패' : '유효'}</td>
                <td style="padding: 6px; border-bottom: 1px solid #f1f5f9;">${data.ssl_grade === 'F' ? '브라우저 경고, 신뢰 불가' : '없음'}</td>
                <td style="padding: 6px; border-bottom: 1px solid #f1f5f9;">${data.ssl_grade === 'F' ? '🔴 높음' : '🟢 낮음'}</td>
            </tr>
            <tr>
                <td style="padding: 6px; border-bottom: 1px solid #f1f5f9;">SSL 등급</td>
                <td style="padding: 6px; border-bottom: 1px solid #f1f5f9;">${data.ssl_grade}</td>
                <td style="padding: 6px; border-bottom: 1px solid #f1f5f9;">${data.ssl_grade === 'F' ? 'SSL 미적용 또는 심각한 문제' : '양호'}</td>
                <td style="padding: 6px; border-bottom: 1px solid #f1f5f9;">${data.ssl_grade === 'F' ? '🔴 높음' : '🟢 낮음'}</td>
            </tr>
        </tbody>
    </table>

    ${data.issues.length > 0 ? `
    <h3>2. 보안 취약점 평가</h3>
    <h4>보안 위험도 매트릭스</h4>
    ${data.issues.map(issue => `
        <div class="issue-item issue-${issue.severity}">
            <span class="severity severity-${issue.severity}">
                ${issue.severity === 'critical' ? '치명적' :
                  issue.severity === 'high' ? '높음' :
                  issue.severity === 'medium' ? '중간' : '낮음'}
            </span>
            <strong>${issue.title}</strong>
            <p>${issue.description}</p>
        </div>
    `).join('')}
    ` : ''}

    <h2>💰 비즈니스 영향 분석</h2>
    <div class="business-impact">
        <h3>단기 영향 (1-3개월)</h3>
        <p><strong>예상 매출 손실:</strong> ₩${data.business_impact.revenue_loss_annual.toLocaleString()}/년</p>
        <p><strong>SEO 순위 하락:</strong> ${data.business_impact.seo_impact}%</p>
        <p><strong>고객 신뢰도 하락:</strong> ${data.business_impact.user_trust_impact}%</p>
    </div>

    ${data.recommendations.length > 0 ? `
    <h2>🔧 해결 방안 및 권장사항</h2>
    <h3>Phase 1: 긴급 조치 (1-3일)</h3>
    ${data.recommendations.map((recommendation, index) => `
        <div class="recommendation">
            <strong>${index + 1}.</strong> ${recommendation}
        </div>
    `).join('')}
    ` : ''}

    <h2>📞 실행 권장사항</h2>
    <h3>즉시 실행 (이번 주 내)</h3>
    <ol>
        <li><strong>경영진 승인:</strong> 보안 개선 프로젝트 승인</li>
        <li><strong>담당자 지정:</strong> 내부 담당자 또는 외부 전문가 선정</li>
        <li><strong>예산 확보:</strong> 보안 개선 예산 확보</li>
        <li><strong>일정 수립:</strong> 구체적인 실행 일정 확정</li>
    </ol>
    
    <div class="business-impact">
        <h3>최종 권고</h3>
        <p><strong>지금 즉시 행동하십시오.</strong> 하루 늦을수록 고객 신뢰와 비즈니스 기회가 계속 손실됩니다.</p>
    </div>

    <div class="footer">
        <p><strong>보고서 문의:</strong> SecureCheck Pro Security Analysis Team</p>
        <p><strong>분석 완료:</strong> ${new Date(data.created_at).toLocaleString('ko-KR')}</p>
        <p><em>이 보고서는 ${analysisDate} 현재 상황을 기준으로 작성되었습니다.</em></p>
        <p style="margin-top: 20px; font-size: 12px; color: #999;">
            이 HTML 파일을 브라우저에서 열고 Ctrl+P (또는 Cmd+P)를 눌러 PDF로 인쇄하실 수 있습니다.
        </p>
    </div>
</body>
</html>`;
  };


  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* 보고서 헤더 */}
      <div className="report-header bg-white rounded-lg shadow-lg p-8">
        <div className="text-center mb-6">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            {data.url.replace(/https?:\/\//, '').toUpperCase()} 웹사이트 보안 분석 보고서
          </h1>
          <div className="text-lg text-gray-600 space-y-1">
            <p><strong>분석 대상:</strong> {data.url}</p>
            <p><strong>분석 일시:</strong> {new Date(data.created_at).toLocaleString('ko-KR')}</p>
            <p><strong>분석자:</strong> Security Analysis Team</p>
            <p><strong>보고서 버전:</strong> 1.0</p>
          </div>
        </div>

        <div className="flex justify-center space-x-4 mb-8">
          <button
            onClick={handleDownloadPDF}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 font-medium"
          >
            📄 보고서 다운로드
          </button>
        </div>
      </div>

      {/* Executive Summary */}
      <div className="report-section">
        <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
          📋 Executive Summary
        </h2>
        <p className="text-lg text-gray-700 mb-6">
          {data.url.replace(/https?:\/\//, '')} 웹사이트에 대한 보안 분석 결과, <strong>중요한 보안 문제</strong>가 발견되었습니다.
        </p>

        <div className="grid md:grid-cols-2 gap-8">
          <div>
            <h3 className="text-xl font-semibold text-red-700 mb-4">🚨 주요 발견사항</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                <span className="font-medium">SSL 등급</span>
                <span className="text-xl font-bold text-blue-600">{data.ssl_grade}</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                <span className="font-medium">보안 점수</span>
                <span className={`text-xl font-bold ${getScoreColor(data.security_score)}`}>
                  {data.security_score}/100
                </span>
              </div>
              <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                <span className="font-medium">발견된 문제</span>
                <span className="text-xl font-bold text-red-600">{data.issues.length}개</span>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-xl font-semibold text-orange-700 mb-4">💰 비즈니스 영향</h3>
            <div className="space-y-3">
              <div className="p-3 bg-red-50 border border-red-200 rounded">
                <div className="text-sm font-medium text-red-800">예상 연간 매출 손실</div>
                <div className="text-xl font-bold text-red-600">
                  ₩{data.business_impact.revenue_loss_annual.toLocaleString()}
                </div>
              </div>
              <div className="p-3 bg-yellow-50 border border-yellow-200 rounded">
                <div className="text-sm font-medium text-yellow-800">SEO 영향</div>
                <div className="text-xl font-bold text-yellow-600">
                  -{data.business_impact.seo_impact}% 순위 하락
                </div>
              </div>
              <div className="p-3 bg-blue-50 border border-blue-200 rounded">
                <div className="text-sm font-medium text-blue-800">고객 신뢰도</div>
                <div className="text-xl font-bold text-blue-600">
                  -{data.business_impact.user_trust_impact}% 신뢰 손상
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 상세 기술 분석 */}
      {data.issues.length > 0 && (
        <div className="report-section">
          <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
            🔍 상세 기술 분석
          </h2>
          
          <div className="mb-6">
            <h3 className="text-xl font-semibold text-gray-800 mb-4">🛡️ 보안 위험도 매트릭스</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full bg-white border border-gray-300 rounded-lg">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-600 border-b">취약점</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-600 border-b">심각도</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-600 border-b">영향도</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-600 border-b">위험도</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {data.issues.map((issue, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-4 py-3">
                        <div className="font-medium text-gray-900">{issue.title}</div>
                        <div className="text-sm text-gray-600">{issue.description}</div>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                          issue.severity === 'critical' ? 'bg-red-100 text-red-800' :
                          issue.severity === 'high' ? 'bg-orange-100 text-orange-800' :
                          issue.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {issue.severity === 'critical' ? '치명적' :
                           issue.severity === 'high' ? '높음' :
                           issue.severity === 'medium' ? '중간' : '낮음'}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">
                        {issue.severity === 'critical' ? '치명적' :
                         issue.severity === 'high' ? '높음' :
                         issue.severity === 'medium' ? '중간' : '낮음'}
                      </td>
                      <td className="px-4 py-3">
                        <span className={`text-sm font-medium ${
                          issue.severity === 'critical' || issue.severity === 'high' ? 'text-red-600' : 
                          issue.severity === 'medium' ? 'text-yellow-600' : 'text-green-600'
                        }`}>
                          {issue.severity === 'critical' || issue.severity === 'high' ? '🔴 High' :
                           issue.severity === 'medium' ? '🟡 Medium' : '🟢 Low'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* 비즈니스 영향 평가 */}
      <div className="report-section">
        <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
          💰 비즈니스 영향 평가
        </h2>
        
        <div className="grid md:grid-cols-2 gap-8">
          <div>
            <h3 className="text-xl font-semibold text-gray-800 mb-4">단기 영향 (1-3개월)</h3>
            <div className="space-y-4">
              <div className="bg-red-50 border-l-4 border-red-400 p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <div className="text-red-400 text-lg">📉</div>
                  </div>
                  <div className="ml-3">
                    <h4 className="text-sm font-medium text-red-800">웹사이트 트래픽 손실</h4>
                    <p className="mt-1 text-sm text-red-700">
                      보안 경고로 인한 이탈: 30-50%
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="bg-orange-50 border-l-4 border-orange-400 p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <div className="text-orange-400 text-lg">💸</div>
                  </div>
                  <div className="ml-3">
                    <h4 className="text-sm font-medium text-orange-800">예상 매출 손실</h4>
                    <p className="mt-1 text-sm text-orange-700 font-bold">
                      ₩{data.business_impact.revenue_loss_annual.toLocaleString()}/년
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-xl font-semibold text-gray-800 mb-4">중장기 영향 (6개월 이상)</h3>
            <div className="space-y-4">
              <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <div className="text-yellow-400 text-lg">🔍</div>
                  </div>
                  <div className="ml-3">
                    <h4 className="text-sm font-medium text-yellow-800">SEO 및 검색 순위 하락</h4>
                    <p className="mt-1 text-sm text-yellow-700 font-bold">
                      -{data.business_impact.seo_impact}% 순위 하락
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="bg-blue-50 border-l-4 border-blue-400 p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <div className="text-blue-400 text-lg">🏢</div>
                  </div>
                  <div className="ml-3">
                    <h4 className="text-sm font-medium text-blue-800">브랜드 이미지 손상</h4>
                    <p className="mt-1 text-sm text-blue-700 font-bold">
                      -{data.business_impact.user_trust_impact}% 신뢰 손상
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 해결 방안 및 권장사항 */}
      {data.recommendations.length > 0 && (
        <div className="report-section">
          <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
            🔧 해결 방안 및 권장사항
          </h2>
          
          <div className="mb-6">
            <h3 className="text-xl font-semibold text-gray-800 mb-4">Phase 1: 긴급 조치 (1-3일)</h3>
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
              <div className="flex items-center mb-2">
                <span className="text-red-600 text-lg mr-2">🚨</span>
                <span className="font-medium text-red-800">우선순위: ⭐⭐⭐⭐⭐ (Critical)</span>
              </div>
            </div>
            
            <div className="space-y-4">
              {data.recommendations.map((recommendation, index) => (
                <div key={index} className="flex items-start space-x-4 p-4 bg-white border border-gray-200 rounded-lg">
                  <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-medium">
                    {index + 1}
                  </div>
                  <div className="flex-1">
                    <p className="text-gray-800 font-medium">{recommendation}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* 실행 권장사항 */}
      <div className="report-section">
        <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
          📞 실행 권장사항
        </h2>
        
        <div className="grid md:grid-cols-2 gap-8">
          <div>
            <h3 className="text-xl font-semibold text-gray-800 mb-4">즉시 실행 (이번 주 내)</h3>
            <div className="space-y-3">
              <div className="flex items-start space-x-3">
                <span className="flex-shrink-0 w-6 h-6 bg-red-100 text-red-600 rounded-full flex items-center justify-center text-sm font-medium">1</span>
                <p className="text-gray-700"><strong>경영진 승인:</strong> 보안 개선 프로젝트 승인</p>
              </div>
              <div className="flex items-start space-x-3">
                <span className="flex-shrink-0 w-6 h-6 bg-red-100 text-red-600 rounded-full flex items-center justify-center text-sm font-medium">2</span>
                <p className="text-gray-700"><strong>담당자 지정:</strong> 내부 담당자 또는 외부 전문가 선정</p>
              </div>
              <div className="flex items-start space-x-3">
                <span className="flex-shrink-0 w-6 h-6 bg-red-100 text-red-600 rounded-full flex items-center justify-center text-sm font-medium">3</span>
                <p className="text-gray-700"><strong>예산 확보:</strong> 보안 개선 예산 확보</p>
              </div>
              <div className="flex items-start space-x-3">
                <span className="flex-shrink-0 w-6 h-6 bg-red-100 text-red-600 rounded-full flex items-center justify-center text-sm font-medium">4</span>
                <p className="text-gray-700"><strong>일정 수립:</strong> 구체적인 실행 일정 확정</p>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-xl font-semibold text-red-700 mb-4">최종 권고</h3>
            <div className="bg-red-50 border border-red-200 rounded-lg p-6">
              <p className="text-red-800 font-medium text-lg">
                <strong>지금 즉시 행동하십시오.</strong> 하루 늦을수록 고객 신뢰와 비즈니스 기회가 계속 손실됩니다.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* 보고서 푸터 */}
      <div className="report-section text-center bg-gray-50">
        <div className="space-y-2 text-sm text-gray-600">
          <p><strong>보고서 문의:</strong> Security Analysis Team</p>
          <p><strong>분석 완료:</strong> {new Date(data.created_at).toLocaleString('ko-KR')}</p>
          <p className="italic">
            *이 보고서는 {new Date(data.created_at).toLocaleDateString('ko-KR')} 현재 상황을 기준으로 작성되었습니다.*
          </p>
        </div>
      </div>
    </div>
  );
}