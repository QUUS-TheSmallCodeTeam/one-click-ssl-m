import { createConnection, connect } from 'tls';
import { createConnection as createTcpConnection } from 'net';
import { URL } from 'url';

export interface SSLAnalysisResult {
  domain: string;
  port: number;
  analyzed_at: string;
  url_scheme?: string;
  port_443_open: boolean;
  port_test_result: string;
  port_error_code?: number;
  port_error?: string;
  certificate_valid: boolean;
  certificate_expired?: boolean;
  days_until_expiry: number;
  not_before?: string;
  not_after?: string;
  subject_cn?: string;
  issuer_cn?: string;
  is_self_signed: boolean;
  ssl_status: 'valid' | 'expired' | 'self_signed' | 'verify_failed' | 'invalid' | 'no_ssl' | 'connection_error' | 'not_yet_valid';
  analysis_result: string;
  subject_dict?: any;
  issuer_dict?: any;
  serial_number?: string;
  version?: number;
  certificate_error?: string;
  security_headers_present: string[];
  missing_security_headers: string[];
  hsts_enabled: boolean;
  hsts_max_age: number;
  hsts_include_subdomains: boolean;
  headers_score: number;
  security_headers_error?: string;
  ssl_grade: string;
  error?: string;
}

export class SSLAnalyzer {
  private readonly securityHeaders = [
    'Strict-Transport-Security',
    'Content-Security-Policy',
    'X-Frame-Options',
    'X-Content-Type-Options',
    'X-XSS-Protection',
    'Referrer-Policy'
  ];

  async analyze(url: string): Promise<SSLAnalysisResult> {
    const parsedUrl = new URL(url);
    const domain = parsedUrl.hostname;
    const port = 443;

    const result: Partial<SSLAnalysisResult> = {
      domain,
      port,
      analyzed_at: new Date().toISOString(),
      url_scheme: parsedUrl.protocol.replace(':', '')
    };

    try {
      // 1. Port connection test
      const portStatus = await this.testPortConnection(domain, port);
      Object.assign(result, portStatus);

      if (!portStatus.port_443_open) {
        return {
          ...result,
          ssl_grade: 'F',
          certificate_valid: false,
          ssl_status: 'no_ssl',
          analysis_result: 'SSL 인증서가 아예 없는 경우',
          days_until_expiry: 0,
          is_self_signed: false,
          security_headers_present: [],
          missing_security_headers: this.securityHeaders,
          hsts_enabled: false,
          hsts_max_age: 0,
          hsts_include_subdomains: false,
          headers_score: 0
        } as SSLAnalysisResult;
      }

      // 2. SSL certificate analysis
      const certInfo = await this.analyzeCertificate(domain, port);
      Object.assign(result, certInfo);

      // 3. Security headers analysis
      const headersInfo = await this.analyzeSecurityHeaders(url);
      Object.assign(result, headersInfo);

      // 4. Calculate SSL grade
      result.ssl_grade = this.calculateSSLGrade(result as SSLAnalysisResult);

    } catch (error) {
      result.error = String(error);
      result.ssl_grade = 'F';
      result.certificate_valid = false;
    }

    return result as SSLAnalysisResult;
  }

  private async testPortConnection(domain: string, port: number): Promise<Partial<SSLAnalysisResult>> {
    return new Promise((resolve) => {
      const socket = createTcpConnection({ port, host: domain, timeout: 5000 });

      socket.on('connect', () => {
        socket.destroy();
        resolve({
          port_443_open: true,
          port_test_result: 'success',
          port_error_code: 0
        });
      });

      socket.on('error', (error) => {
        resolve({
          port_443_open: false,
          port_test_result: 'error',
          port_error: String(error)
        });
      });

      socket.on('timeout', () => {
        socket.destroy();
        resolve({
          port_443_open: false,
          port_test_result: 'connection_refused',
          port_error_code: -1
        });
      });
    });
  }

  private async analyzeCertificate(domain: string, port: number): Promise<Partial<SSLAnalysisResult>> {
    return new Promise((resolve) => {
      let cert: any = null;
      let sslVerificationError: string | null = null;

      // First attempt: normal verification
      const tlsSocket = connect({
        host: domain,
        port,
        servername: domain,
        timeout: 10000
      });

      tlsSocket.on('secureConnect', () => {
        cert = tlsSocket.getPeerCertificate(true);
        tlsSocket.destroy();
        this.processCertificate(cert, resolve);
      });

      tlsSocket.on('error', (error) => {
        sslVerificationError = String(error);

        // Second attempt: without verification
        const tlsSocketNoVerify = connect({
          host: domain,
          port,
          servername: domain,
          rejectUnauthorized: false,
          timeout: 10000
        });

        tlsSocketNoVerify.on('secureConnect', () => {
          cert = tlsSocketNoVerify.getPeerCertificate(true);
          tlsSocketNoVerify.destroy();
          this.processCertificate(cert, resolve, sslVerificationError);
        });

        tlsSocketNoVerify.on('error', (err) => {
          resolve(this.handleCertificateError(err, sslVerificationError));
        });
      });
    });
  }

  private processCertificate(cert: any, resolve: Function, sslVerificationError?: string | null) {
    try {
      if (!cert || !cert.valid_from) {
        throw new Error(`Unable to retrieve certificate info: ${sslVerificationError}`);
      }

      const notBefore = new Date(cert.valid_from);
      const notAfter = new Date(cert.valid_to);
      const now = new Date();

      const isValid = notBefore <= now && now <= notAfter;
      const daysUntilExpiry = Math.floor((notAfter.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));

      const subjectCn = cert.subject?.CN || '';
      const issuerCn = cert.issuer?.CN || '';

      // Check if self-signed
      const isSelfSigned = JSON.stringify(cert.subject) === JSON.stringify(cert.issuer);

      let sslStatus: SSLAnalysisResult['ssl_status'];
      let analysisResult: string;

      if (!isValid) {
        if (now > notAfter) {
          sslStatus = 'expired';
          analysisResult = 'SSL 인증서가 만료된 경우';
        } else {
          sslStatus = 'not_yet_valid';
          analysisResult = 'SSL 인증서가 아직 유효하지 않은 경우';
        }
      } else if (isSelfSigned) {
        sslStatus = 'self_signed';
        analysisResult = '자체 서명 인증서인 경우';
      } else {
        sslStatus = 'valid';
        analysisResult = '정상적인 SSL 인증서';
      }

      resolve({
        certificate_valid: isValid,
        certificate_expired: now > notAfter,
        days_until_expiry: daysUntilExpiry,
        not_before: cert.valid_from,
        not_after: cert.valid_to,
        subject_cn: subjectCn,
        issuer_cn: issuerCn,
        is_self_signed: isSelfSigned,
        ssl_status: sslStatus,
        analysis_result: analysisResult,
        subject_dict: cert.subject,
        issuer_dict: cert.issuer,
        serial_number: cert.serialNumber || '',
        version: cert.version || 0
      });

    } catch (error) {
      resolve(this.handleCertificateError(error, sslVerificationError));
    }
  }

  private handleCertificateError(error: any, sslVerificationError?: string | null): Partial<SSLAnalysisResult> {
    const errorStr = String(error).toLowerCase();

    let sslStatus: SSLAnalysisResult['ssl_status'];
    let analysisResult: string;

    if (errorStr.includes('certificate verify failed')) {
      sslStatus = 'verify_failed';
      analysisResult = '인증서 검증 실패';
    } else if (errorStr.includes('certificate has expired')) {
      sslStatus = 'expired';
      analysisResult = 'SSL 인증서가 만료된 경우';
    } else if (errorStr.includes('self signed certificate')) {
      sslStatus = 'self_signed';
      analysisResult = '자체 서명 인증서인 경우';
    } else {
      sslStatus = 'connection_error';
      analysisResult = 'SSL 연결 오류';
    }

    return {
      certificate_valid: false,
      certificate_error: String(error),
      ssl_status: sslStatus,
      analysis_result: analysisResult,
      days_until_expiry: 0,
      is_self_signed: false
    };
  }

  private async analyzeSecurityHeaders(url: string): Promise<Partial<SSLAnalysisResult>> {
    try {
      const response = await fetch(url, {
        method: 'HEAD',
        // @ts-ignore
        timeout: 10000
      });

      const headers = Object.fromEntries(response.headers.entries());

      const presentHeaders: string[] = [];
      const missingHeaders: string[] = [];

      for (const header of this.securityHeaders) {
        if (Object.keys(headers).some(h => h.toLowerCase() === header.toLowerCase())) {
          presentHeaders.push(header);
        } else {
          missingHeaders.push(header);
        }
      }

      // HSTS analysis
      const hstsHeader = headers['strict-transport-security'] || '';
      let hstsMaxAge = 0;
      let hstsIncludeSubdomains = false;

      if (hstsHeader) {
        const parts = hstsHeader.split(';');
        for (const part of parts) {
          const trimmedPart = part.trim();
          if (trimmedPart.startsWith('max-age=')) {
            hstsMaxAge = parseInt(trimmedPart.split('=')[1]) || 0;
          } else if (trimmedPart === 'includeSubDomains') {
            hstsIncludeSubdomains = true;
          }
        }
      }

      return {
        security_headers_present: presentHeaders,
        missing_security_headers: missingHeaders,
        hsts_enabled: Boolean(hstsHeader),
        hsts_max_age: hstsMaxAge,
        hsts_include_subdomains: hstsIncludeSubdomains,
        headers_score: (presentHeaders.length / this.securityHeaders.length) * 100
      };

    } catch (error) {
      return {
        security_headers_error: String(error),
        missing_security_headers: this.securityHeaders,
        security_headers_present: [],
        hsts_enabled: false,
        hsts_max_age: 0,
        hsts_include_subdomains: false,
        headers_score: 0
      };
    }
  }

  private calculateSSLGrade(analysisResult: SSLAnalysisResult): string {
    // Step 1: Critical Issues Check (F Grade)
    if (!analysisResult.port_443_open) {
      return 'F'; // Website not accessible
    }

    const sslStatus = analysisResult.ssl_status;

    if (sslStatus === 'no_ssl') {
      return 'F'; // No HTTPS service
    } else if (sslStatus === 'expired') {
      return 'F'; // Expired SSL certificate
    } else if (sslStatus === 'connection_error') {
      return 'F'; // Connection error
    }

    // Step 2: Base Score Calculation
    let score: number;
    if (sslStatus === 'valid') {
      score = 80; // Valid certificate: 80 points (B grade)
    } else if (sslStatus === 'self_signed') {
      score = 30; // Self-signed certificate: 30 points (D grade)
    } else if (sslStatus === 'verify_failed' || sslStatus === 'invalid') {
      score = 30; // Invalid certificate: 30 points (D grade)
    } else {
      score = 0; // Error analyzing certificate: 0 points (F grade)
    }

    // Step 3: Security Headers Bonus (only for valid certificates)
    if (sslStatus === 'valid') {
      const presentHeaders = analysisResult.security_headers_present;
      const totalHeaders = this.securityHeaders.length;
      const headersPercentage = totalHeaders > 0 ? (presentHeaders.length / totalHeaders * 100) : 0;

      if (headersPercentage === 100) {
        score += 10; // All recommended headers: +10 points
      } else if (headersPercentage >= 50) {
        score += 5;  // 50%+ headers: +5 points
      } else if (headersPercentage > 0) {
        score += 2;  // Some headers: +2 points
      }
      // No headers: 0 points (no penalty)
    }

    // Step 4: Final Grade Assignment
    // Special handling for self-signed and invalid certificates
    if (sslStatus === 'self_signed' || sslStatus === 'verify_failed' || sslStatus === 'invalid') {
      return 'D'; // Always D grade for these statuses
    }

    // Grade based on score for valid certificates
    if (score >= 95) {
      return 'A+';
    } else if (score >= 90) {
      return 'A';
    } else if (score >= 80) {
      return 'B';
    } else if (score >= 70) {
      return 'C';
    } else if (score >= 50) {
      return 'D';
    } else {
      return 'F';
    }
  }
}