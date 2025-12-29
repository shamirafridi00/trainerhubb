from django.contrib import admin
from .models import Trainer


@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    """
    Custom user admin with email as primary field.
    """
    list_display = ('business_name', 'user', 'rating', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'rating', 'created_at')
    search_fields = ('business_name', 'user__email')
    ordering = ('-created_at',)
