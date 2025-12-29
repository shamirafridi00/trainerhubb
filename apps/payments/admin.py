from django.contrib import admin
from .models import Subscription, Payment


class PaymentInline(admin.TabularInline):
    """Inline admin for payments."""
    model = Payment
    extra = 0
    fields = ['amount', 'currency', 'paddle_transaction_id', 'status', 'created_at']
    readonly_fields = ['created_at']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Admin interface for Subscription model."""
    list_display = ('get_trainer_name', 'paddle_subscription_id', 'status', 'next_billing_date', 'created_at')
    list_filter = ('status', 'created_at', 'next_billing_date')
    search_fields = ('trainer__business_name', 'trainer__user__email', 'paddle_subscription_id')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    inlines = [PaymentInline]
    
    fieldsets = (
        ('Subscription Information', {
            'fields': ('trainer', 'paddle_subscription_id', 'status')
        }),
        ('Billing', {
            'fields': ('next_billing_date',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
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


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin interface for Payment model."""
    list_display = ('get_trainer_name', 'amount', 'currency', 'paddle_transaction_id', 'status', 'created_at')
    list_filter = ('status', 'currency', 'created_at')
    search_fields = ('subscription__trainer__business_name', 'paddle_transaction_id')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('subscription', 'amount', 'currency', 'paddle_transaction_id')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        queryset = super().get_queryset(request)
        return queryset.select_related('subscription', 'subscription__trainer')
    
    def get_trainer_name(self, obj):
        return obj.subscription.trainer.business_name
    get_trainer_name.short_description = 'Trainer'
    get_trainer_name.admin_order_field = 'subscription__trainer__business_name'
