from django.contrib import admin
from .models import DashboardMetrics


@admin.register(DashboardMetrics)
class DashboardMetricsAdmin(admin.ModelAdmin):
    """Admin interface for DashboardMetrics model."""
    list_display = (
        'get_trainer_name', 'date', 'bookings_count', 'completed_bookings',
        'cancelled_bookings', 'revenue', 'new_clients', 'active_clients',
        'completion_rate', 'created_at'
    )
    list_filter = ('date', 'created_at', 'trainer')
    search_fields = ('trainer__business_name', 'trainer__user__email')
    readonly_fields = ('created_at', 'completion_rate', 'cancellation_rate', 'average_revenue_per_booking')
    ordering = ('-date',)
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('trainer', 'date')
        }),
        ('Booking Metrics', {
            'fields': ('bookings_count', 'completed_bookings', 'cancelled_bookings')
        }),
        ('Business Metrics', {
            'fields': ('revenue', 'new_clients', 'active_clients', 'average_session_rating')
        }),
        ('Calculated Metrics', {
            'fields': ('completion_rate', 'cancellation_rate', 'average_revenue_per_booking'),
            'classes': ('collapse',)
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
    
    def completion_rate(self, obj):
        return f"{obj.completion_rate}%"
    completion_rate.short_description = 'Completion Rate'
    
    def cancellation_rate(self, obj):
        return f"{obj.cancellation_rate}%"
    cancellation_rate.short_description = 'Cancellation Rate'
    
    def average_revenue_per_booking(self, obj):
        return f"${obj.average_revenue_per_booking}"
    average_revenue_per_booking.short_description = 'Avg Revenue/Booking'

