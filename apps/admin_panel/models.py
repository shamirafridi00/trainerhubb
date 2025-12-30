"""
Admin Panel Models
Track admin actions, impersonation logs, and system settings.
"""
from django.db import models
from django.conf import settings
from apps.trainers.models import Trainer

# Import domain models
from .domain_models import CustomDomain, DomainVerificationLog


class AdminActionLog(models.Model):
    """
    Log of all admin actions for audit trail.
    """
    ACTION_CHOICES = [
        ('view_trainer', 'View Trainer'),
        ('impersonate', 'Impersonate Trainer'),
        ('suspend', 'Suspend Trainer'),
        ('activate', 'Activate Trainer'),
        ('upgrade_plan', 'Upgrade Plan'),
        ('downgrade_plan', 'Downgrade Plan'),
        ('approve_domain', 'Approve Domain'),
        ('reject_domain', 'Reject Domain'),
        ('delete_trainer', 'Delete Trainer'),
        ('manual_payment', 'Manual Payment Adjustment'),
    ]
    
    admin_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='admin_actions'
    )
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    target_trainer = models.ForeignKey(
        Trainer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='admin_actions_on'
    )
    details = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['admin_user', '-created_at']),
            models.Index(fields=['target_trainer', '-created_at']),
            models.Index(fields=['action', '-created_at']),
        ]
    
    def __str__(self):
        admin = self.admin_user.email if self.admin_user else 'Unknown'
        target = self.target_trainer.business_name if self.target_trainer else 'N/A'
        return f"{admin} - {self.get_action_display()} - {target}"


class PlatformSettings(models.Model):
    """
    Global platform settings managed by super admin.
    """
    key = models.CharField(max_length=100, unique=True)
    value = models.JSONField()
    description = models.TextField(blank=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Platform Setting'
        verbose_name_plural = 'Platform Settings'
    
    def __str__(self):
        return self.key
