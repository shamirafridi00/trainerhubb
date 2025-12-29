from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Admin interface for Booking model."""
    list_display = ('get_client_name', 'get_trainer_name', 'start_time', 'end_time', 'status', 'duration_display', 'created_at')
    list_filter = ('status', 'start_time', 'trainer', 'created_at')
    search_fields = ('client__first_name', 'client__last_name', 'trainer__business_name', 'notes')
    ordering = ('-start_time',)
    date_hierarchy = 'start_time'
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('trainer', 'client', 'start_time', 'end_time', 'status')
        }),
        ('Details', {
            'fields': ('notes', 'cancellation_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_client_name(self, obj):
        return obj.client.get_full_name()
    get_client_name.short_description = 'Client'
    get_client_name.admin_order_field = 'client__first_name'
    
    def get_trainer_name(self, obj):
        return obj.trainer.business_name
    get_trainer_name.short_description = 'Trainer'
    get_trainer_name.admin_order_field = 'trainer__business_name'
    
    def duration_display(self, obj):
        return f"{obj.duration_minutes} min"
    duration_display.short_description = 'Duration'
    
    def save_model(self, request, obj, form, change):
        """Override to handle validation errors gracefully."""
        try:
            super().save_model(request, obj, form, change)
        except Exception as e:
            self.message_user(request, f"Error saving booking: {str(e)}", level='ERROR')
