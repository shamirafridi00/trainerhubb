from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('client', 'trainer', 'start_time', 'status', 'duration_minutes')
    list_filter = ('status', 'start_time', 'created_at')
    search_fields = ('client__first_name', 'client__last_name', 'trainer__business_name')
    readonly_fields = ('created_at', 'updated_at', 'duration_minutes')
    date_hierarchy = 'start_time'
    
    def duration_minutes(self, obj):
        return f"{obj.duration_minutes} min"
    duration_minutes.short_description = 'Duration'
