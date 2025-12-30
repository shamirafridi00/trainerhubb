"""
Admin Panel Django Admin Configuration
Enhanced with better displays, filters, and actions.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import AdminActionLog, PlatformSettings
from .domain_models import CustomDomain, DomainVerificationLog


@admin.register(AdminActionLog)
class AdminActionLogAdmin(admin.ModelAdmin):
    """
    Enhanced Django admin for viewing action logs with better displays.
    """
    list_display = [
        'id', 'action_badge', 'admin_user', 'target_trainer_link', 
        'created_at', 'ip_address'
    ]
    list_filter = ['action', 'created_at', 'admin_user']
    search_fields = [
        'admin_user__email', 
        'target_trainer__business_name',
        'ip_address',
        'details'
    ]
    readonly_fields = [
        'admin_user', 'action', 'target_trainer', 'details', 
        'ip_address', 'user_agent', 'created_at'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Action Details', {
            'fields': ('admin_user', 'action', 'target_trainer')
        }),
        ('Additional Information', {
            'fields': ('details',),
            'classes': ('collapse',)
        }),
        ('Request Information', {
            'fields': ('ip_address', 'user_agent', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def action_badge(self, obj):
        """Display action with color-coded badge."""
        colors = {
            'impersonate': '#007bff',
            'suspend': '#dc3545',
            'activate': '#28a745',
            'delete_trainer': '#dc3545',
            'view_trainer': '#6c757d',
        }
        color = colors.get(obj.action, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_action_display()
        )
    action_badge.short_description = 'Action'
    action_badge.admin_order_field = 'action'
    
    def target_trainer_link(self, obj):
        """Display trainer as clickable link."""
        if obj.target_trainer:
            url = reverse('admin:trainers_trainer_change', args=[obj.target_trainer.pk])
            return format_html('<a href="{}">{}</a>', url, obj.target_trainer.business_name)
        return '-'
    target_trainer_link.short_description = 'Target Trainer'
    
    def has_add_permission(self, request):
        # Logs are created programmatically only
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Keep audit trail intact
        return False
    
    class Media:
        css = {
            'all': ('admin/css/admin_custom.css',)
        }
    
    def changelist_view(self, request, extra_context=None):
        """Add custom context for changelist."""
        extra_context = extra_context or {}
        extra_context['title'] = 'Admin Action Logs - Audit Trail'
        return super().changelist_view(request, extra_context)


@admin.register(PlatformSettings)
class PlatformSettingsAdmin(admin.ModelAdmin):
    """
    Enhanced Django admin for platform settings.
    """
    list_display = ['key', 'value_preview', 'description', 'updated_by', 'updated_at']
    list_filter = ['updated_at', 'updated_by']
    search_fields = ['key', 'description', 'value']
    readonly_fields = ['updated_by', 'updated_at']
    
    fieldsets = (
        ('Setting Information', {
            'fields': ('key', 'value', 'description')
        }),
        ('Metadata', {
            'fields': ('updated_by', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def value_preview(self, obj):
        """Show truncated value preview."""
        value_str = str(obj.value)
        if len(value_str) > 50:
            return value_str[:50] + '...'
        return value_str
    value_preview.short_description = 'Value'
    
    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(CustomDomain)
class CustomDomainAdmin(admin.ModelAdmin):
    """
    Enhanced admin for custom domains.
    """
    list_display = [
        'domain', 'trainer_link', 'status_badge', 'dns_verified_at', 
        'ssl_status_badge', 'created_at'
    ]
    list_filter = ['status', 'ssl_status', 'verification_method', 'created_at']
    search_fields = ['domain', 'trainer__business_name', 'trainer__user__email']
    readonly_fields = [
        'dns_verified_at', 'ssl_provisioned_at', 'ssl_expires_at', 
        'created_at', 'updated_at'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Domain Information', {
            'fields': ('trainer', 'domain', 'status')
        }),
        ('DNS Verification', {
            'fields': (
                'verification_method', 'verification_token', 
                'dns_verified_at', 'verification_attempts'
            )
        }),
        ('SSL Certificate', {
            'fields': (
                'ssl_status', 'ssl_provider', 'ssl_provisioned_at', 
                'ssl_expires_at'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        """Display status with color-coded badge."""
        colors = {
            'pending': '#ffc107',
            'verifying': '#17a2b8',
            'verified': '#28a745',
            'active': '#28a745',
            'failed': '#dc3545',
            'rejected': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def ssl_status_badge(self, obj):
        """Display SSL status with color-coded badge."""
        colors = {
            'pending': '#ffc107',
            'provisioning': '#17a2b8',
            'provisioned': '#28a745',
            'expired': '#dc3545',
            'failed': '#dc3545',
        }
        color = colors.get(obj.ssl_status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_ssl_status_display()
        )
    ssl_status_badge.short_description = 'SSL Status'
    ssl_status_badge.admin_order_field = 'ssl_status'
    
    def trainer_link(self, obj):
        """Display trainer as clickable link."""
        if obj.trainer:
            url = reverse('admin:trainers_trainer_change', args=[obj.trainer.pk])
            return format_html('<a href="{}">{}</a>', url, obj.trainer.business_name)
        return '-'
    trainer_link.short_description = 'Trainer'


@admin.register(DomainVerificationLog)
class DomainVerificationLogAdmin(admin.ModelAdmin):
    """
    Admin for domain verification logs.
    """
    list_display = ['domain', 'verification_type', 'status_badge', 'created_at']
    list_filter = ['verification_type', 'status', 'created_at']
    search_fields = ['domain__domain', 'details', 'error_message']
    readonly_fields = ['domain', 'verification_type', 'status', 'details', 'error_message', 'created_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Verification Information', {
            'fields': ('domain', 'verification_type', 'status')
        }),
        ('Details', {
            'fields': ('details', 'error_message'),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        """Display status with badge."""
        if obj.status == 'success':
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 8px; '
                'border-radius: 3px; font-size: 11px;">✓ Success</span>'
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">✗ Failed</span>'
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def has_add_permission(self, request):
        # Logs are created programmatically only
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Keep audit trail intact
        return False
