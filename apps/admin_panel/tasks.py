"""
Celery Tasks for Domain Management
Automatic DNS verification and SSL renewal.
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .domain_models import CustomDomain, DomainVerificationLog
from .domain_verification import DomainVerifier, SSLProvisioner


@shared_task
def auto_verify_pending_domains():
    """
    Automatically verify DNS for pending domains.
    Runs every 5 minutes.
    """
    pending_domains = CustomDomain.objects.filter(
        status__in=['pending', 'verifying']
    )
    
    results = {
        'checked': 0,
        'verified': 0,
        'failed': 0
    }
    
    for domain in pending_domains:
        results['checked'] += 1
        
        # Skip if recently attempted (wait at least 5 minutes)
        if domain.last_verification_attempt:
            time_since_last = timezone.now() - domain.last_verification_attempt
            if time_since_last < timedelta(minutes=5):
                continue
        
        # Perform verification
        verifier = DomainVerifier(domain.domain, domain.verification_token)
        success, message, details = verifier.verify_domain(domain.verification_method)
        
        # Update domain
        domain.last_verification_attempt = timezone.now()
        domain.verification_attempts += 1
        domain.save()
        
        # Log result
        log_status = 'success' if success else 'failed'
        DomainVerificationLog.objects.create(
            domain=domain,
            verification_type='dns',
            status=log_status,
            details=details,
            error_message=message if not success else ''
        )
        
        if success:
            domain.mark_verified()
            domain.status = 'provisioning_ssl'
            domain.save()
            results['verified'] += 1
            
            # Trigger SSL provisioning
            provision_ssl_for_domain.delay(domain.id)
        else:
            results['failed'] += 1
    
    return results


@shared_task
def provision_ssl_for_domain(domain_id):
    """
    Provision SSL certificate for a verified domain.
    
    Args:
        domain_id: ID of the CustomDomain
    """
    try:
        domain = CustomDomain.objects.get(id=domain_id)
        
        # Check if DNS is verified
        if not domain.is_verified:
            return {'error': 'Domain not verified'}
        
        # Provision SSL
        provisioner = SSLProvisioner(domain.domain)
        success, message, details = provisioner.provision_certificate()
        
        if success:
            domain.ssl_status = 'provisioned'
            domain.ssl_provisioned_at = timezone.now()
            
            # Set expiry
            if 'expires_at' in details:
                from dateutil import parser
                domain.ssl_expires_at = parser.parse(details['expires_at'])
            else:
                domain.ssl_expires_at = timezone.now() + timedelta(days=90)
            
            domain.mark_active()
            
            # Log success
            DomainVerificationLog.objects.create(
                domain=domain,
                verification_type='ssl',
                status='success',
                details=details
            )
            
            return {'status': 'success', 'domain': domain.domain}
        else:
            domain.ssl_status = 'failed'
            domain.save()
            
            # Log failure
            DomainVerificationLog.objects.create(
                domain=domain,
                verification_type='ssl',
                status='failed',
                error_message=message,
                details=details
            )
            
            return {'status': 'failed', 'error': message}
            
    except CustomDomain.DoesNotExist:
        return {'error': 'Domain not found'}


@shared_task
def renew_expiring_ssl_certificates():
    """
    Renew SSL certificates that are expiring soon.
    Runs daily.
    """
    # Domains expiring in next 30 days
    expiry_threshold = timezone.now() + timedelta(days=30)
    
    domains_to_renew = CustomDomain.objects.filter(
        ssl_status='provisioned',
        ssl_expires_at__lte=expiry_threshold,
        status='active'
    )
    
    results = {
        'checked': 0,
        'renewed': 0,
        'failed': 0
    }
    
    for domain in domains_to_renew:
        results['checked'] += 1
        
        provisioner = SSLProvisioner(domain.domain)
        success, message, details = provisioner.renew_certificate()
        
        if success:
            domain.ssl_provisioned_at = timezone.now()
            
            if 'expires_at' in details:
                from dateutil import parser
                domain.ssl_expires_at = parser.parse(details['expires_at'])
            else:
                domain.ssl_expires_at = timezone.now() + timedelta(days=90)
            
            domain.save()
            
            # Log success
            DomainVerificationLog.objects.create(
                domain=domain,
                verification_type='ssl',
                status='success',
                details={'action': 'renewal', **details}
            )
            
            results['renewed'] += 1
        else:
            # Log failure
            DomainVerificationLog.objects.create(
                domain=domain,
                verification_type='ssl',
                status='failed',
                error_message=message,
                details={'action': 'renewal', **details}
            )
            
            results['failed'] += 1
    
    return results

