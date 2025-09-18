import type { SSLAnalysisResult } from './ssl-analyzer';

export interface SecurityIssue {
  type: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  title: string;
  description: string;
}

export interface BusinessImpact {
  revenue_loss_annual: number;
  seo_impact: number;
  user_trust_impact: number;
}

export interface AnalysisResponse {
  id: string;
  url: string;
  ssl_grade: string;
  security_score: number;
  issues: SecurityIssue[];
  business_impact: BusinessImpact;
  recommendations: string[];
  created_at: string;
  ssl_result: SSLAnalysisResult;
}

export function calculateSecurityScore(sslResult: SSLAnalysisResult): number {
  // SSL 상태에 따른 기본 점수
  const sslStatus = sslResult.ssl_status;

  if (sslStatus === 'no_ssl' || !sslResult.port_443_open) {
    return 0; // F grade: No SSL
  } else if (sslStatus === 'expired') {
    return 0; // F grade: Expired certificate
  } else if (sslStatus === 'connection_error') {
    return 0; // F grade: Connection error
  } else if (sslStatus === 'self_signed') {
    return 30; // D grade: Self-signed certificate
  } else if (sslStatus === 'verify_failed' || sslStatus === 'invalid') {
    return 30; // D grade: Invalid certificate
  } else if (sslStatus === 'valid') {
    // Valid certificate: 80 points base
    let score = 80;

    // Security headers bonus (only for valid certificates)
    const presentHeaders = sslResult.security_headers_present;
    const missingHeaders = sslResult.missing_security_headers;
    const totalHeaders = presentHeaders.length + missingHeaders.length;

    if (totalHeaders > 0) {
      const headersPercentage = (presentHeaders.length / totalHeaders) * 100;

      if (headersPercentage === 100) {
        score += 10; // All headers: +10
      } else if (headersPercentage >= 50) {
        score += 5;  // 50%+ headers: +5
      } else if (headersPercentage > 0) {
        score += 2;  // Some headers: +2
      }
      // No headers: 0 (no bonus)
    }

    return score;
  } else {
    return 0; // Unknown status: F grade
  }
}

export function extractIssues(sslResult: SSLAnalysisResult): SecurityIssue[] {
  const issues: SecurityIssue[] = [];
  const sslStatus = sslResult.ssl_status;

  // 1. SSL 서비스 완전 부재
  if (sslStatus === 'no_ssl' || !sslResult.port_443_open) {
    issues.push({
      type: 'ssl_service',
      severity: 'critical',
      title: 'HTTPS 서비스 완전 부재',
      description: '443 포트가 닫혀있어 HTTPS 서비스가 전혀 제공되지 않습니다.'
    });
    issues.push({
      type: 'data_encryption',
      severity: 'critical',
      title: '모든 데이터 평문 전송',
      description: '암호화 없이 모든 데이터가 평문으로 전송되어 도청 위험에 노출됩니다.'
    });
    issues.push({
      type: 'browser_warning',
      severity: 'high',
      title: '브라우저 보안 경고',
      description: '모든 브라우저에서 \'안전하지 않음\' 경고 메시지가 표시됩니다.'
    });
  }

  // 2. 만료된 인증서
  if (sslStatus === 'expired') {
    issues.push({
      type: 'certificate',
      severity: 'critical',
      title: 'SSL 인증서 만료',
      description: 'SSL 인증서가 만료되어 브라우저에서 보안 경고를 표시합니다.'
    });
  }

  // 3. 자체 서명 인증서
  if (sslStatus === 'self_signed') {
    issues.push({
      type: 'certificate',
      severity: 'high',
      title: '자체 서명 인증서',
      description: '신뢰할 수 있는 인증기관에서 발급하지 않은 인증서로, 브라우저에서 경고를 표시합니다.'
    });
  }

  // 4. 인증서 검증 실패
  if (sslStatus === 'verify_failed') {
    issues.push({
      type: 'certificate',
      severity: 'critical',
      title: 'SSL 인증서 검증 실패',
      description: '브라우저에서 SSL 인증서를 신뢰할 수 없습니다. 인증 기관이 유효하지 않거나 체인이 불완전합니다.'
    });
  }

  // 5. 보안 헤더 누락
  const missingHeaders = sslResult.missing_security_headers;
  for (const header of missingHeaders) {
    issues.push({
      type: 'security_header',
      severity: 'medium',
      title: `${header} 헤더 누락`,
      description: `${header} 보안 헤더가 설정되지 않았습니다.`
    });
  }

  // 6. 인증서 만료 임박 (정상 SSL인 경우에만 체크)
  if (sslStatus === 'valid') {
    const daysUntilExpiry = sslResult.days_until_expiry;
    if (0 < daysUntilExpiry && daysUntilExpiry < 30) {
      issues.push({
        type: 'certificate',
        severity: 'medium',
        title: 'SSL 인증서 만료 임박',
        description: `SSL 인증서가 ${daysUntilExpiry}일 후에 만료됩니다.`
      });
    }
  }

  return issues;
}

export function calculateBusinessImpact(securityScore: number, sslResult: SSLAnalysisResult, issues: SecurityIssue[]): BusinessImpact {
  // Business Metrics
  const monthlyVisitors = 10000;
  const conversionRate = 0.02; // 2%
  const orderConversionRate = 0.10; // 10%
  const averageOrderValue = 50_000_000; // KRW

  // Calculate base annual revenue
  const monthlyRevenue = monthlyVisitors * conversionRate * orderConversionRate * averageOrderValue;
  const baseRevenue = monthlyRevenue * 12;

  // Get SSL grade
  let sslGrade = sslResult.ssl_grade;

  // Security Loss Rates by Grade
  const lossRates: Record<string, { loss: number; seo: number; trust: number }> = {
    'F': { loss: 0.50, seo: 40, trust: 90 },  // 50% loss, 40% SEO drop, 90% trust loss
    'D': { loss: 0.30, seo: 30, trust: 70 },  // 30% loss, 30% SEO drop, 70% trust loss
    'C': { loss: 0.20, seo: 25, trust: 50 },  // 20% loss, 25% SEO drop, 50% trust loss
    'B': { loss: 0.10, seo: 15, trust: 30 },  // 10% loss, 15% SEO drop, 30% trust loss
    'A': { loss: 0.05, seo: 5, trust: 10 },   // 5% loss, 5% SEO drop, 10% trust loss
    'A+': { loss: 0.02, seo: 0, trust: 5 }    // 2% loss, 0% SEO drop, 5% trust loss
  };

  // Handle A- grade
  if (sslGrade === 'A-') {
    sslGrade = 'A'; // Treat A- as A for business impact
  }

  const rates = lossRates[sslGrade] || lossRates['F'];

  // Calculate impacts
  const revenueLoss = Math.floor(baseRevenue * rates.loss);
  const seoImpact = rates.seo;
  const userTrustImpact = rates.trust;

  return {
    revenue_loss_annual: revenueLoss,
    seo_impact: seoImpact,
    user_trust_impact: userTrustImpact
  };
}

export function generateRecommendations(sslResult: SSLAnalysisResult, issues: SecurityIssue[]): string[] {
  const recommendations: string[] = [];
  const sslStatus = sslResult.ssl_status;

  if (sslStatus === 'no_ssl' || !sslResult.port_443_open) {
    // 주요 권장사항
    recommendations.push('긴급: SSL 인증서 설치 및 HTTPS 서비스 활성화 (오늘 실행)');
    recommendations.push('필수: Let\'s Encrypt 무료 SSL 적용 (투자 0원)');
    recommendations.push('권장: HTTP → HTTPS 자동 리다이렉션 설정 (이번 주)');
    recommendations.push('장기: 보안 모니터링 체계 구축 (1개월)');
  } else if (sslStatus === 'expired') {
    recommendations.push('새로운 SSL 인증서를 즉시 발급하세요.');
    recommendations.push('Let\'s Encrypt 자동 갱신 시스템을 설정하세요.');
  } else if (sslStatus === 'self_signed') {
    recommendations.push('신뢰할 수 있는 인증기관(CA)에서 SSL 인증서를 발급받으세요.');
    recommendations.push('Let\'s Encrypt를 이용하여 무료로 인증서를 발급받을 수 있습니다.');
  } else if (sslStatus === 'valid') {
    // 정상 SSL인 경우 세부 개선사항
    const missingHeaders = sslResult.missing_security_headers;
    if (missingHeaders.length > 0) {
      recommendations.push('누락된 보안 헤더들을 웹서버 설정에 추가하세요.');
    }

    const sslGrade = sslResult.ssl_grade;
    if (['B', 'C', 'D'].includes(sslGrade)) {
      recommendations.push('SSL 등급 A 이상 달성을 위해 TLS 1.3 지원 및 보안 설정을 강화하세요.');
    }

    const daysUntilExpiry = sslResult.days_until_expiry;
    if (0 < daysUntilExpiry && daysUntilExpiry < 30) {
      recommendations.push('인증서 만료가 임박했습니다. 자동 갱신 시스템을 확인하세요.');
    }

    if (missingHeaders.length === 0 && ['A+', 'A', 'A-'].includes(sslGrade)) {
      recommendations.push('현재 보안 설정이 우수합니다. 지속적인 모니터링을 권장합니다.');
    }
  } else {
    recommendations.push('서버 연결 문제를 해결한 후 SSL 인증서를 설치하세요.');
  }

  return recommendations;
}