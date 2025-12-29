from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin interface for Notification model."""
    list_display = ('get_trainer_name', 'notification_type', 'recipient', 'subject_preview', 'status', 'created_at', 'sent_at')
    list_filter = ('notification_type', 'status', 'created_at', 'trainer')
    search_fields = ('trainer__business_name', 'recipient', 'subject', 'message')
    readonly_fields = ('created_at', 'sent_at', 'failed_reason')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Notification Details', {
            'fields': ('trainer', 'notification_type', 'recipient', 'subject', 'message')
        }),
        ('Status', {
            'fields': ('status', 'sent_at', 'failed_reason')
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        queryset = super().get_queryset(request)
        return queryset.select_related('trainer', 'trainer__user')
    
    def get_trainer_name(self, obj):
        return obj.trainer.business_name
    get_trainer_name.short_description = 'Trainer'
    get_trainer_name.admin_order_field = 'trainer__business_name'
    
    def subject_preview(self, obj):
        return obj.subject[:50] + '...' if len(obj.subject) > 50 else obj.subject
    subject_preview.short_description = 'Subject'

