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

        # 포트 추출 (URL에 포트가 명시된 경우)
        if ':' in parsed_url.netloc and not parsed_url.netloc.endswith(']:'):
            domain, port_str = parsed_url.netloc.rsplit(':', 1)
            try:
                port = int(port_str)
            except ValueError:
                domain = parsed_url.netloc
                port = 443  # 기본 HTTPS 포트
        else:
            domain = parsed_url.netloc or parsed_url.path
            # 스키마에 따른 기본 포트
            port = 443 if parsed_url.scheme == 'https' else 80

        # www가 있으면 www 없는 버전도 체크해서 더 나은 결과 사용
        domains_to_check = [domain]
        if domain.startswith('www.'):
            non_www_domain = domain[4:]  # www. 제거
            domains_to_check.append(non_www_domain)

        # 병렬로 동시에 분석
        tasks = [self._analyze_single_domain(check_domain, port, parsed_url.scheme) for check_domain in domains_to_check]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 더 좋은 결과 선택 (F가 아닌 것 우선, 같으면 더 높은 등급)
        best_result = self._select_best_result(results, domain)
        return best_result

    async def _analyze_single_domain(self, domain: str, port: int, scheme: str) -> Dict:
        """단일 도메인에 대한 SSL 분석을 수행합니다"""
        result = {
            'domain': domain,
            'port': port,
            'analyzed_at': datetime.now().isoformat(),
            'url_scheme': scheme
        }

        # HTTP 스키마인 경우 SSL 체크 불가
        if scheme == 'http' or port == 80:
            result.update({
                'ssl_grade': 'F',
                'certificate_valid': False,
                'ssl_status': 'no_ssl',
                'analysis_result': 'HTTP 프로토콜 사용 - SSL 없음'
            })
            return result

        try:
            # 1. 포트 연결 테스트 (가이드의 nc -z 명령 구현)
            port_status = await self._test_port_connection(domain, port)
            result.update(port_status)
            
            if not port_status.get('port_443_open', False):
                # 443 포트 연결 실패시 HTTP 리다이렉션 체크
                http_redirect_info = await self._check_http_redirect(domain)
                result.update(http_redirect_info)

                # 여전히 SSL 없음으로 판단
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
            domain_url = f"{scheme}://{domain}:{port}" if port not in [80, 443] else f"{scheme}://{domain}"
            headers_info = await self._analyze_security_headers(domain_url)
            result.update(headers_info)
            
            # 4. 전체 SSL 등급 계산 (가이드 기준)
            result['ssl_grade'] = self._calculate_ssl_grade_real(result)
            
        except Exception as e:
            result['error'] = str(e)
            result['ssl_grade'] = 'F'
            result['certificate_valid'] = False

        return result

    def _select_best_result(self, results: List, original_domain: str) -> Dict:
        """여러 결과 중 가장 좋은 결과를 선택합니다"""
        # 예외 처리된 결과 제외
        valid_results = [r for r in results if not isinstance(r, Exception)]

        if not valid_results:
            return {
                'domain': original_domain,
                'ssl_grade': 'F',
                'certificate_valid': False,
                'ssl_status': 'error',
                'analysis_result': '분석 중 오류 발생'
            }

        # 등급 순서 정의 (좋은 순서대로)
        grade_order = ['A+', 'A', 'B', 'C', 'D', 'F']

        def grade_score(grade):
            try:
                return grade_order.index(grade)
            except ValueError:
                return len(grade_order)  # F보다 나쁜 경우

        # 가장 좋은 등급 찾기
        best_result = min(valid_results, key=lambda x: grade_score(x.get('ssl_grade', 'F')))

        # 원래 도메인 정보 유지하되 최고 결과 사용
        best_result['original_domain'] = original_domain
        best_result['checked_domains'] = [r.get('domain') for r in valid_results]

        return best_result
    
    async def _test_port_connection(self, domain: str, port: int) -> Dict:
        """포트 연결 테스트 (가이드의 nc -z domain 443 구현) - 재시도 로직 포함"""
        max_retries = 3
        base_retry_delay = 1  # 기본 1초 간격

        # DNS resolution 확인
        try:
            resolved_ips = socket.gethostbyname_ex(domain)
            dns_info = {
                'hostname': resolved_ips[0],
                'aliases': resolved_ips[1],
                'ip_addresses': resolved_ips[2]
            }
        except Exception as e:
            dns_info = {'dns_error': str(e)}

        for attempt in range(max_retries):
            # 백오프 전략: 재시도마다 대기 시간 증가
            retry_delay = base_retry_delay * (attempt + 1)

            try:
                # SSL 직접 연결 시도 (더 신뢰성 있는 방법)
                import ssl as ssl_module
                context = ssl_module.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl_module.CERT_NONE

                with socket.create_connection((domain, port), timeout=5) as sock:
                    with context.wrap_socket(sock, server_hostname=domain) as ssock:
                        # SSL 연결 성공
                        result = {
                            'port_443_open': True,
                            'port_test_result': 'success',
                            'port_error_code': 0,
                            'attempts': attempt + 1,
                            'connection_method': 'ssl_direct'
                        }
                        result.update(dns_info)
                        return result

            except Exception as e:
                # 연결 실패시 재시도 (마지막 시도가 아닌 경우)
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    continue

        result = {
            'port_443_open': False,
            'port_test_result': 'error',
            'port_error': str(e),
            'attempts': max_retries,
            'connection_method': 'ssl_direct_failed'
        }
        result.update(dns_info)
        return result

    async def _check_http_redirect(self, domain: str) -> Dict:
        """HTTP 접속시 HTTPS로 리다이렉트되는지 확인"""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                # HTTP로 접속하여 리다이렉트 확인
                async with session.get(f'http://{domain}',
                                     allow_redirects=False,
                                     timeout=aiohttp.ClientTimeout(total=10)) as response:

                    # 3xx 리다이렉트 응답 확인
                    if response.status in [301, 302, 303, 307, 308]:
                        location = response.headers.get('Location', '')
                        if location.startswith('https://'):
                            return {
                                'http_redirect_to_https': True,
                                'redirect_location': location,
                                'redirect_note': 'HTTP에서 HTTPS로 리다이렉트됨'
                            }

                    return {
                        'http_redirect_to_https': False,
                        'redirect_note': 'HTTP 리다이렉트 없음'
                    }

        except Exception as e:
            return {
                'http_redirect_to_https': False,
                'redirect_error': str(e),
                'redirect_note': 'HTTP 접속 실패'
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
                # SSL 인증서 검증을 건너뛰고 헤더만 가져오기 (HTTPS 유지)
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                async with session.get(url, ssl=ssl_context, timeout=aiohttp.ClientTimeout(total=10)) as response:
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
    
