import React from 'react';
import { Document, Page, Text, View, StyleSheet, pdf, Font } from '@react-pdf/renderer';
import type { AnalysisResponse } from './business-logic';

// Register Korean fonts (you would need to add font files)
// Font.register({
//   family: 'NotoSansKR',
//   src: './fonts/NotoSansKR-Regular.ttf'
// });

// TSC 보고서 스타일
const styles = StyleSheet.create({
  page: {
    flexDirection: 'column',
    backgroundColor: '#FFFFFF',
    padding: 30,
    fontSize: 10,
    fontFamily: 'Helvetica' // Use built-in font for now
  },
  title: {
    fontSize: 18,
    marginBottom: 20,
    textAlign: 'center',
    fontWeight: 'bold',
    color: '#1a1a1a'
  },
  sectionTitle: {
    fontSize: 14,
    marginBottom: 10,
    marginTop: 15,
    fontWeight: 'bold',
    color: '#2c3e50'
  },
  subsectionTitle: {
    fontSize: 12,
    marginBottom: 8,
    marginTop: 12,
    fontWeight: 'bold',
    color: '#34495e'
  },
  body: {
    fontSize: 10,
    lineHeight: 1.5,
    marginBottom: 6,
    color: '#333333'
  },
  emphasis: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#e74c3c'
  },
  codeBlock: {
    fontSize: 9,
    backgroundColor: '#f8f9fa',
    padding: 10,
    marginTop: 8,
    marginBottom: 8,
    border: '0.5px solid #dee2e6',
    color: '#2c3e50',
    fontFamily: 'Courier'
  },
  table: {
    display: 'flex',
    width: '100%',
    marginTop: 10,
    marginBottom: 10
  },
  tableRow: {
    flexDirection: 'row',
    borderBottomWidth: 0.5,
    borderBottomColor: '#95a5a6'
  },
  tableHeader: {
    backgroundColor: '#3498db',
    color: '#ffffff',
    fontWeight: 'bold'
  },
  tableCell: {
    flex: 1,
    padding: 6,
    fontSize: 8,
    textAlign: 'center'
  },
  separator: {
    marginTop: 15,
    marginBottom: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#cccccc'
  },
  gradeF: {
    color: '#e74c3c',
    fontWeight: 'bold'
  },
  gradeD: {
    color: '#f39c12',
    fontWeight: 'bold'
  },
  gradeC: {
    color: '#f1c40f',
    fontWeight: 'bold'
  },
  gradeB: {
    color: '#3498db',
    fontWeight: 'bold'
  },
  gradeA: {
    color: '#27ae60',
    fontWeight: 'bold'
  }
});

interface PDFDocumentProps {
  analysisData: AnalysisResponse;
}

const SecurityAnalysisDocument: React.FC<PDFDocumentProps> = ({ analysisData }) => {
  const domain = new URL(analysisData.url).hostname;
  const analysisDate = new Date(analysisData.created_at).toLocaleDateString('ko-KR');
  const sslResult = analysisData.ssl_result;

  const getGradeStyle = (grade: string) => {
    switch (grade) {
      case 'F': return styles.gradeF;
      case 'D': return styles.gradeD;
      case 'C': return styles.gradeC;
      case 'B': return styles.gradeB;
      default: return styles.gradeA;
    }
  };

  return (
    <Document>
      <Page size="A4" style={styles.page}>
        {/* 제목 */}
        <Text style={styles.title}>
          {domain} 웹사이트 보안 및 서버 설정 문제 분석 보고서
        </Text>

        {/* 기본 정보 */}
        <View style={{ marginBottom: 20 }}>
          <Text style={styles.body}>분석 대상: {domain}</Text>
          <Text style={styles.body}>분석 일시: {analysisDate}</Text>
          <Text style={styles.body}>분석자: 원클릭SSL Security Analysis Team</Text>
          <Text style={styles.body}>보고서 버전: 1.0</Text>
        </View>

        <View style={styles.separator} />

        {/* Executive Summary */}
        <Text style={styles.sectionTitle}>Executive Summary</Text>

        <Text style={styles.body}>
          {analysisData.ssl_grade === 'F' || !sslResult.certificate_valid
            ? `${domain} 웹사이트에 대한 보안 분석 결과, 중대한 SSL 인증서 및 서버 설정 문제가 발견되었습니다. 현재 HTTPS 연결이 정상 작동하지 않아 고객의 개인정보 보호와 브랜드 신뢰도에 부정적 영향을 미치고 있습니다.`
            : analysisData.ssl_grade === 'A+'
            ? `${domain} 웹사이트는 업계 최고 수준의 SSL 보안을 구현하고 있습니다. 현재 수준을 유지하며 지속적인 모니터링이 권장됩니다.`
            : `${domain} 웹사이트는 기본적인 SSL 보안이 적용되어 있으나 추가 보안 강화를 통한 경쟁력 향상이 가능한 상태입니다.`}
        </Text>

        {/* 주요 발견사항 */}
        <Text style={styles.subsectionTitle}>주요 발견사항</Text>
        {analysisData.issues.slice(0, 3).map((issue, index) => (
          <Text key={index} style={styles.body}>
            • {issue.severity === 'critical' ? '❌' : '⚠️'} {issue.title}
          </Text>
        ))}

        {/* 보안 등급 및 점수 */}
        <Text style={styles.subsectionTitle}>보안 평가</Text>
        <View style={{ flexDirection: 'row', marginBottom: 10 }}>
          <Text style={styles.body}>SSL 등급: </Text>
          <Text style={[styles.body, getGradeStyle(analysisData.ssl_grade)]}>
            {analysisData.ssl_grade}
          </Text>
        </View>
        <Text style={styles.body}>보안 점수: {analysisData.security_score}/100</Text>

        <View style={styles.separator} />

        {/* 상세 기술 분석 */}
        <Text style={styles.sectionTitle}>상세 기술 분석</Text>

        <Text style={styles.subsectionTitle}>1. SSL 인증서 상태 분석</Text>
        <View style={styles.codeBlock}>
          <Text>Domain: {domain}</Text>
          <Text>Valid: {sslResult.certificate_valid ? 'Yes' : 'No'}</Text>
          <Text>Days Until Expiry: {sslResult.days_until_expiry}일</Text>
          <Text>SSL Grade: {sslResult.ssl_grade}</Text>
          <Text>SSL Status: {sslResult.ssl_status}</Text>
        </View>

        <Text style={styles.subsectionTitle}>2. 보안 헤더 분석</Text>
        <Text style={styles.body}>
          설정된 헤더 ({sslResult.security_headers_present.length}개): {sslResult.security_headers_present.join(', ') || '없음'}
        </Text>
        <Text style={styles.body}>
          누락된 헤더 ({sslResult.missing_security_headers.length}개): {sslResult.missing_security_headers.join(', ') || '없음'}
        </Text>

        <View style={styles.separator} />

        {/* 비즈니스 영향 */}
        <Text style={styles.sectionTitle}>비즈니스 영향</Text>
        <Text style={styles.body}>예상 연간 수익 손실: {analysisData.business_impact.revenue_loss_annual.toLocaleString()}원</Text>
        <Text style={styles.body}>SEO 영향: {analysisData.business_impact.seo_impact}% 순위 하락</Text>
        <Text style={styles.body}>사용자 신뢰도 영향: {analysisData.business_impact.user_trust_impact}% 감소</Text>

        <View style={styles.separator} />

        {/* 권장 조치사항 */}
        <Text style={styles.sectionTitle}>권장 조치사항</Text>
        {analysisData.recommendations.map((recommendation, index) => (
          <Text key={index} style={styles.body}>
            {index + 1}. {recommendation}
          </Text>
        ))}

        <View style={styles.separator} />

        {/* 결론 */}
        <Text style={styles.sectionTitle}>결론</Text>
        <Text style={styles.body}>
          {analysisData.ssl_grade === 'F'
            ? `${domain} 웹사이트의 현재 보안 상태는 즉시 개선이 필요한 심각한 수준입니다. SSL 인증서 문제와 HTTPS 서비스 중단은 고객 신뢰도와 비즈니스 성과에 직접적인 악영향을 미치고 있으며, 이는 연간 ${analysisData.business_impact.revenue_loss_annual.toLocaleString()}원 이상의 기회비용을 발생시킬 수 있습니다.`
            : `${domain} 웹사이트의 보안 상태는 전반적으로 ${analysisData.ssl_grade === 'A+' ? '최고' : '양호한'} 수준입니다. ${analysisData.ssl_grade === 'A+' ? '현재 수준을 유지하며' : '지속적인 개선을 통해'} 보안을 강화하시기 바랍니다.`}
        </Text>

        {/* 푸터 */}
        <View style={{ marginTop: 30 }}>
          <Text style={styles.body}>---</Text>
          <Text style={styles.body}>보고서 문의: 원클릭SSL Security Analysis Team</Text>
          <Text style={styles.body}>생성일: {new Date().toLocaleDateString('ko-KR')}</Text>
        </View>
      </Page>
    </Document>
  );
};

export async function generatePDFReport(analysisData: AnalysisResponse): Promise<Buffer> {
  try {
    const doc = <SecurityAnalysisDocument analysisData={analysisData} />;
    const pdfBuffer = await pdf(doc).toBuffer();
    return pdfBuffer;
  } catch (error) {
    console.error('PDF generation error:', error);
    throw new Error(`PDF 생성 중 오류가 발생했습니다: ${error}`);
  }
}