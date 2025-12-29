from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Admin interface for Booking model."""
    list_display = ('client', 'trainer', 'start_time', 'end_time', 'status', 'duration_minutes', 'created_at')
    list_filter = ('status', 'start_time', 'trainer', 'created_at')
    search_fields = ('client__first_name', 'client__last_name', 'trainer__business_name', 'notes')
    readonly_fields = ('created_at', 'updated_at', 'duration_minutes')
    date_hierarchy = 'start_time'
    ordering = ('-start_time',)
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('trainer', 'client', 'start_time', 'end_time', 'status')
        }),
        ('Details', {
            'fields': ('notes', 'cancellation_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'duration_minutes'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        queryset = super().get_queryset(request)
        return queryset.select_related('client', 'trainer')
    
    def duration_minutes(self, obj):
        """Display duration in minutes."""
        return f"{obj.duration_minutes} min"
    duration_minutes.short_description = 'Duration'
