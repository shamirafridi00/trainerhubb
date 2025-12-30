"""
Domain Verification Utilities
Handle DNS verification and SSL provisioning.
"""
import dns.resolver
import socket
import subprocess
from datetime import datetime, timedelta
from django.conf import settings


class DomainVerifier:
    """
    Verify domain DNS configuration.
    """
    
    def __init__(self, domain, verification_token):
        self.domain = domain
        self.verification_token = verification_token
        self.platform_domain = 'trainerhubb.app'  # Base platform domain
    
    def verify_cname(self):
        """
        Verify CNAME record points to platform.
        
        Expected: domain.com CNAME -> trainer-slug.trainerhubb.app
        
        Returns:
            tuple: (success: bool, message: str, details: dict)
        """
        try:
            # Resolve CNAME records
            answers = dns.resolver.resolve(self.domain, 'CNAME')
            
            for rdata in answers:
                cname_target = str(rdata.target).rstrip('.')
                
                # Check if points to our platform
                if self.platform_domain in cname_target:
                    return True, f"CNAME verified: {cname_target}", {
                        'cname_target': cname_target,
                        'method': 'cname'
                    }
            
            return False, f"CNAME does not point to {self.platform_domain}", {
                'found_cname': str(answers[0].target) if answers else None
            }
            
        except dns.resolver.NXDOMAIN:
            return False, "Domain does not exist", {'error': 'NXDOMAIN'}
        except dns.resolver.NoAnswer:
            return False, "No CNAME record found", {'error': 'NoAnswer'}
        except Exception as e:
            return False, f"DNS query failed: {str(e)}", {'error': str(e)}
    
    def verify_txt(self):
        """
        Verify TXT record contains verification token.
        
        Expected: _trainerhub-verify.domain.com TXT -> "trainerhub-verify=TOKEN"
        
        Returns:
            tuple: (success: bool, message: str, details: dict)
        """
        try:
            # Query TXT record
            txt_record = f"_trainerhub-verify.{self.domain}"
            answers = dns.resolver.resolve(txt_record, 'TXT')
            
            expected_value = f"trainerhub-verify={self.verification_token}"
            
            for rdata in answers:
                txt_value = rdata.to_text().strip('"')
                
                if txt_value == expected_value:
                    return True, "TXT record verified", {
                        'txt_record': txt_record,
                        'method': 'txt'
                    }
            
            return False, "TXT record does not match verification token", {
                'expected': expected_value,
                'found': [rdata.to_text() for rdata in answers]
            }
            
        except dns.resolver.NXDOMAIN:
            return False, "TXT record not found", {'error': 'NXDOMAIN'}
        except dns.resolver.NoAnswer:
            return False, "No TXT record found", {'error': 'NoAnswer'}
        except Exception as e:
            return False, f"TXT query failed: {str(e)}", {'error': str(e)}
    
    def verify_a_record(self):
        """
        Verify A record points to platform IP (optional check).
        
        Returns:
            tuple: (success: bool, message: str, details: dict)
        """
        try:
            # Get platform IP (you'll need to configure this)
            platform_ip = getattr(settings, 'PLATFORM_IP_ADDRESS', None)
            
            if not platform_ip:
                return False, "Platform IP not configured", {}
            
            # Resolve A records
            answers = dns.resolver.resolve(self.domain, 'A')
            
            for rdata in answers:
                if str(rdata) == platform_ip:
                    return True, f"A record verified: {platform_ip}", {
                        'ip_address': platform_ip,
                        'method': 'a_record'
                    }
            
            return False, f"A record does not point to {platform_ip}", {
                'found_ips': [str(rdata) for rdata in answers]
            }
            
        except Exception as e:
            return False, f"A record query failed: {str(e)}", {'error': str(e)}
    
    def verify_domain(self, method='cname'):
        """
        Verify domain using specified method.
        
        Args:
            method: 'cname', 'txt', or 'a_record'
            
        Returns:
            tuple: (success: bool, message: str, details: dict)
        """
        if method == 'cname':
            return self.verify_cname()
        elif method == 'txt':
            return self.verify_txt()
        elif method == 'a_record':
            return self.verify_a_record()
        else:
            return False, f"Unknown verification method: {method}", {}
    
    def test_http_connectivity(self):
        """
        Test if domain is accessible via HTTP.
        
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            import requests
            response = requests.get(f"http://{self.domain}", timeout=5)
            return True, f"HTTP accessible (status: {response.status_code})"
        except Exception as e:
            return False, f"HTTP not accessible: {str(e)}"


class SSLProvisioner:
    """
    SSL certificate provisioning (simulated for now).
    In production, integrate with Let's Encrypt or your SSL provider.
    """
    
    def __init__(self, domain):
        self.domain = domain
    
    def provision_certificate(self):
        """
        Provision SSL certificate for domain.
        
        In production, this would:
        1. Use certbot or acme.sh with Let's Encrypt
        2. Complete DNS-01 or HTTP-01 challenge
        3. Install certificate on web server
        4. Configure nginx/caddy to use cert
        
        Returns:
            tuple: (success: bool, message: str, details: dict)
        """
        # SIMULATION for development
        # In production, replace with actual Let's Encrypt integration
        
        try:
            # Simulate certificate provisioning
            expires_at = datetime.now() + timedelta(days=90)
            
            return True, "SSL certificate provisioned", {
                'provider': 'letsencrypt',
                'expires_at': expires_at.isoformat(),
                'issued_at': datetime.now().isoformat(),
                'simulation': True  # Remove in production
            }
            
        except Exception as e:
            return False, f"SSL provisioning failed: {str(e)}", {}
    
    def renew_certificate(self):
        """
        Renew SSL certificate.
        
        Returns:
            tuple: (success: bool, message: str, details: dict)
        """
        # In production, use certbot renew or similar
        return self.provision_certificate()
    
    def check_certificate_status(self):
        """
        Check SSL certificate status and expiry.
        
        Returns:
            dict: Certificate information
        """
        try:
            import ssl
            import socket
            
            context = ssl.create_default_context()
            with socket.create_connection((self.domain, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=self.domain) as ssock:
                    cert = ssock.getpeercert()
                    
                    return {
                        'valid': True,
                        'expires': cert.get('notAfter'),
                        'issuer': cert.get('issuer'),
                        'subject': cert.get('subject')
                    }
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }


def generate_verification_token():
    """
    Generate a unique verification token.
    
    Returns:
        str: Verification token
    """
    import secrets
    return secrets.token_urlsafe(32)

