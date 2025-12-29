from django.contrib import admin
from .models import AvailabilitySlot, TrainerBreak


@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(admin.ModelAdmin):
    list_display = ('trainer', 'get_day_display', 'start_time', 'end_time', 'is_active')
    list_filter = ('day_of_week', 'is_active', 'created_at')
    search_fields = ('trainer__business_name', 'trainer__user__email')
    ordering = ('trainer', 'day_of_week', 'start_time')
    
    def get_day_display(self, obj):
        return obj.get_day_of_week_display()
    get_day_display.short_description = 'Day'


@admin.register(TrainerBreak)
class TrainerBreakAdmin(admin.ModelAdmin):
    list_display = ('trainer', 'start_date', 'end_date', 'reason')
    list_filter = ('start_date', 'created_at')
    search_fields = ('trainer__business_name', 'trainer__user__email', 'reason')
    ordering = ('-start_date',)
