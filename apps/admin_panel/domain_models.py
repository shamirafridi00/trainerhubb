"""
Domain Management Models
Handle custom domain requests, verification, and SSL provisioning.
"""
from django.db import models
from django.utils import timezone
from apps.trainers.models import Trainer


class CustomDomain(models.Model):
    """
    Custom domain configuration for trainers.
    Handles DNS verification and SSL provisioning.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Verification'),
        ('verifying', 'Verifying DNS'),
        ('verified', 'DNS Verified'),
        ('provisioning_ssl', 'Provisioning SSL'),
        ('active', 'Active'),
        ('failed', 'Verification Failed'),
        ('suspended', 'Suspended'),
    ]
    
    trainer = models.OneToOneField(
        Trainer,
        on_delete=models.CASCADE,
        related_name='custom_domain'
    )
    domain = models.CharField(max_length=255, unique=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Verification
    verification_token = models.CharField(max_length=100, unique=True)
    verification_method = models.CharField(
        max_length=20,
        choices=[('cname', 'CNAME Record'), ('txt', 'TXT Record')],
        default='cname'
    )
    dns_verified_at = models.DateTimeField(null=True, blank=True)
    last_verification_attempt = models.DateTimeField(null=True, blank=True)
    verification_attempts = models.IntegerField(default=0)
    
    # SSL
    ssl_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('provisioning', 'Provisioning'),
            ('provisioned', 'Provisioned'),
            ('failed', 'Failed'),
            ('expired', 'Expired')
        ],
        default='pending'
    )
    ssl_provisioned_at = models.DateTimeField(null=True, blank=True)
    ssl_expires_at = models.DateTimeField(null=True, blank=True)
    ssl_provider = models.CharField(max_length=50, default='letsencrypt')
    
    # Admin Actions
    approved_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_domains'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    activated_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['domain']),
            models.Index(fields=['status']),
            models.Index(fields=['trainer', 'status']),
        ]
    
    def __str__(self):
        return f"{self.domain} ({self.get_status_display()})"
    
    @property
    def is_active(self):
        """Check if domain is active."""
        return self.status == 'active'
    
    @property
    def is_verified(self):
        """Check if DNS is verified."""
        return self.dns_verified_at is not None
    
    @property
    def ssl_is_valid(self):
        """Check if SSL is valid and not expired."""
        if self.ssl_status != 'provisioned':
            return False
        if not self.ssl_expires_at:
            return False
        return self.ssl_expires_at > timezone.now()
    
    @property
    def needs_ssl_renewal(self):
        """Check if SSL needs renewal (within 30 days of expiry)."""
        if not self.ssl_expires_at:
            return False
        days_until_expiry = (self.ssl_expires_at - timezone.now()).days
        return days_until_expiry <= 30
    
    def mark_verified(self):
        """Mark DNS as verified."""
        self.dns_verified_at = timezone.now()
        self.status = 'verified'
        self.save()
    
    def mark_active(self):
        """Mark domain as active."""
        self.status = 'active'
        self.activated_at = timezone.now()
        self.save()
    
    def mark_failed(self, reason=''):
        """Mark domain verification as failed."""
        self.status = 'failed'
        self.rejection_reason = reason
        self.save()


class DomainVerificationLog(models.Model):
    """
    Log of domain verification attempts.
    """
    domain = models.ForeignKey(
        CustomDomain,
        on_delete=models.CASCADE,
        related_name='verification_logs'
    )
    verification_type = models.CharField(
        max_length=20,
        choices=[('dns', 'DNS Check'), ('ssl', 'SSL Provisioning')]
    )
    status = models.CharField(
        max_length=20,
        choices=[('success', 'Success'), ('failed', 'Failed')]
    )
    details = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['domain', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.domain.domain} - {self.verification_type} - {self.status}"

