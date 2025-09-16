import ssl
import socket
import asyncio
import aiohttp
import certifi
from datetime import datetime
from urllib.parse import urlparse
from typing import Dict, List, Optional
import subprocess
import json
import re

class SSLAnalyzer:
    """SSL/TLS 보안 분석 클래스 - SSL_Certificate_Analysis_Guide.md 기반 구현"""
    
    def __init__(self):
        self.security_headers = [
            'Strict-Transport-Security',
            'Content-Security-Policy', 
            'X-Frame-Options',
            'X-Content-Type-Options',
            'X-XSS-Protection',
            'Referrer-Policy'
        ]
    
    async def analyze(self, url: str) -> Dict:
        """웹사이트의 전체 SSL 보안 분석을 수행합니다 - SSL_Certificate_Analysis_Guide.md 방법론 적용"""
        parsed_url = urlparse(url)
        domain = parsed_url.netloc or parsed_url.path
        port = 443  # HTTPS 포트 고정
        
        result = {
            'domain': domain,
            'port': port,
            'analyzed_at': datetime.now().isoformat(),
            'url_scheme': parsed_url.scheme
        }
        
        try:
            # 1. 포트 연결 테스트 (가이드의 nc -z 명령 구현)
            port_status = await self._test_port_connection(domain, port)
            result.update(port_status)
            
            if not port_status.get('port_443_open', False):
                # 443 포트가 닫혀있으면 SSL 없음
                result.update({
                    'ssl_grade': 'F',
                    'certificate_valid': False,
                    'ssl_status': 'no_ssl',
                    'analysis_result': 'SSL 인증서가 아예 없는 경우'
                })
                return result
            
            # 2. SSL 인증서 분석 (가이드의 openssl s_client 구현)
            cert_info = await self._analyze_certificate_real(domain, port)
            result.update(cert_info)
            
            # 3. 보안 헤더 분석  
            headers_info = await self._analyze_security_headers(url)
            result.update(headers_info)
            
            # 4. 전체 SSL 등급 계산 (가이드 기준)
            result['ssl_grade'] = self._calculate_ssl_grade_real(result)
            
        except Exception as e:
            result['error'] = str(e)
            result['ssl_grade'] = 'F'
            result['certificate_valid'] = False
            
        return result
    
    async def _test_port_connection(self, domain: str, port: int) -> Dict:
        """포트 연결 테스트 (가이드의 nc -z domain 443 구현)"""
        try:
            # 소켓 연결 테스트 (nc -z와 동일한 기능)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)  # 5초 타임아웃
            result = sock.connect_ex((domain, port))
            sock.close()
            
            return {
                'port_443_open': result == 0,
                'port_test_result': 'success' if result == 0 else 'connection_refused',
                'port_error_code': result
            }
            
        except Exception as e:
            return {
                'port_443_open': False,
                'port_test_result': 'error',
                'port_error': str(e)
            }
    
    async def _analyze_certificate_real(self, domain: str, port: int) -> Dict:
        """실제 SSL 인증서 분석 (가이드의 openssl s_client 구현)"""
        cert = None
        ssl_verification_error = None
        
        # 첫 번째 시도: 정상 검증으로 인증서 정보 가져오기
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
        except ssl.SSLError as e:
            ssl_verification_error = str(e)
            # 두 번째 시도: 검증 비활성화로 인증서 정보 가져오기
            try:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                with socket.create_connection((domain, port), timeout=10) as sock:
                    with context.wrap_socket(sock, server_hostname=domain) as ssock:
                        cert = ssock.getpeercert()
            except Exception:
                pass
        
        try:
            if not cert or 'notBefore' not in cert:
                raise Exception(f"Unable to retrieve certificate info: {ssl_verification_error}")
                
            # 인증서 파싱
            import datetime as dt
            
            # 유효기간 파싱
            not_before_str = cert['notBefore']
            not_after_str = cert['notAfter'] 
            
            # 날짜 형식: 'Aug 18 00:00:00 2025 GMT'
            not_before = dt.datetime.strptime(not_before_str, '%b %d %H:%M:%S %Y %Z')
            not_after = dt.datetime.strptime(not_after_str, '%b %d %H:%M:%S %Y %Z')
            now = dt.datetime.now()
            
            # 인증서 유효성 검사
            is_valid = not_before <= now <= not_after
            days_until_expiry = (not_after - now).days
            
            # subject와 issuer 추출 (가이드의 핵심 체크 포인트)
            subject_dict = dict(x[0] for x in cert['subject'])
            issuer_dict = dict(x[0] for x in cert['issuer'])
            
            subject_cn = subject_dict.get('commonName', '')
            issuer_cn = issuer_dict.get('commonName', '')
            
            # 자체 서명 인증서 판별 (가이드의 핵심 로직)
            is_self_signed = (subject_dict == issuer_dict)
            
            # SSL 상태 분류 (가이드 기준)
            if not is_valid:
                if now > not_after:
                    ssl_status = 'expired'
                    analysis_result = 'SSL 인증서가 만료된 경우'
                else:
                    ssl_status = 'not_yet_valid'
                    analysis_result = 'SSL 인증서가 아직 유효하지 않은 경우'
            elif is_self_signed:
                ssl_status = 'self_signed'
                analysis_result = '자체 서명 인증서인 경우'
            else:
                ssl_status = 'valid'
                analysis_result = '정상적인 SSL 인증서'
            
            return {
                'certificate_valid': is_valid,
                'certificate_expired': now > not_after,
                'days_until_expiry': days_until_expiry,
                'not_before': not_before_str,
                'not_after': not_after_str,
                'subject_cn': subject_cn,
                'issuer_cn': issuer_cn,
                'is_self_signed': is_self_signed,
                'ssl_status': ssl_status,
                'analysis_result': analysis_result,
                'subject_dict': subject_dict,
                'issuer_dict': issuer_dict,
                'serial_number': cert.get('serialNumber', ''),
                'version': cert.get('version', 0)
            }
            
        except Exception as e:
            # SSL 연결 실패 (가이드의 다양한 오류 케이스)
            error_str = str(e).lower()
            
            if 'certificate verify failed' in error_str:
                ssl_status = 'verify_failed'
                analysis_result = '인증서 검증 실패'
            elif 'certificate has expired' in error_str:
                ssl_status = 'expired'
                analysis_result = 'SSL 인증서가 만료된 경우'
            elif 'self signed certificate' in error_str:
                ssl_status = 'self_signed'
                analysis_result = '자체 서명 인증서인 경우'
            else:
                ssl_status = 'connection_error'
                analysis_result = 'SSL 연결 오류'
                
            return {
                'certificate_valid': False,
                'certificate_error': str(e),
                'ssl_status': ssl_status,
                'analysis_result': analysis_result,
                'days_until_expiry': 0
            }
    
    
    async def _analyze_security_headers(self, url: str) -> Dict:
        """보안 헤더 분석"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, ssl=False, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    headers = dict(response.headers)
            
            present_headers = []
            missing_headers = []
            
            for header in self.security_headers:
                if header.lower() in [h.lower() for h in headers.keys()]:
                    present_headers.append(header)
                else:
                    missing_headers.append(header)
            
            # HSTS 특별 분석
            hsts_header = headers.get('Strict-Transport-Security', '')
            hsts_max_age = 0
            hsts_include_subdomains = False
            
            if hsts_header:
                parts = hsts_header.split(';')
                for part in parts:
                    part = part.strip()
                    if part.startswith('max-age='):
                        hsts_max_age = int(part.split('=')[1])
                    elif part == 'includeSubDomains':
                        hsts_include_subdomains = True
            
            return {
                'security_headers_present': present_headers,
                'missing_security_headers': missing_headers,
                'hsts_enabled': bool(hsts_header),
                'hsts_max_age': hsts_max_age,
                'hsts_include_subdomains': hsts_include_subdomains,
                'headers_score': len(present_headers) / len(self.security_headers) * 100
            }
            
        except Exception as e:
            return {
                'security_headers_error': str(e),
                'missing_security_headers': self.security_headers,
                'headers_score': 0
            }
    
    
    
    def _calculate_ssl_grade_real(self, analysis_result: Dict) -> str:
        """Updated SSL grade calculation matching new criteria"""

        # Step 1: Critical Issues Check (F Grade)
        if not analysis_result.get('port_443_open', False):
            return 'F'  # Website not accessible

        ssl_status = analysis_result.get('ssl_status', 'connection_error')

        if ssl_status == 'no_ssl':
            return 'F'  # No HTTPS service
        elif ssl_status == 'expired':
            return 'F'  # Expired SSL certificate
        elif ssl_status == 'connection_error':
            return 'F'  # Connection error

        # Step 2: Base Score Calculation
        if ssl_status == 'valid':
            score = 80  # Valid certificate: 80 points (B grade)
        elif ssl_status == 'self_signed':
            score = 30  # Self-signed certificate: 30 points (D grade)
        elif ssl_status in ['verify_failed', 'invalid']:
            score = 30  # Invalid certificate: 30 points (D grade)
        else:
            score = 0   # Error analyzing certificate: 0 points (F grade)

        # Step 3: Security Headers Bonus (only for valid certificates)
        if ssl_status == 'valid':
            present_headers = analysis_result.get('security_headers_present', [])
            total_headers = len(self.security_headers)
            headers_percentage = (len(present_headers) / total_headers * 100) if total_headers > 0 else 0

            if headers_percentage == 100:
                score += 10  # All recommended headers: +10 points
            elif headers_percentage >= 50:
                score += 5   # 50%+ headers: +5 points
            elif headers_percentage > 0:
                score += 2   # Some headers: +2 points
            # No headers: 0 points (no penalty)

        # Step 4: Final Grade Assignment
        # Special handling for self-signed and invalid certificates
        if ssl_status in ['self_signed', 'verify_failed', 'invalid']:
            return 'D'  # Always D grade for these statuses

        # Grade based on score for valid certificates
        if score >= 95:
            return 'A+'
        elif score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 50:
            return 'D'
        else:
            return 'F'
    
