from django.contrib import admin
from .models import Subscription, Payment, WebhookEvent, ClientPayment


class PaymentInline(admin.TabularInline):
    """Inline admin for payments."""
    model = Payment
    extra = 0
    fields = ['amount', 'currency', 'paddle_transaction_id', 'status', 'created_at']
    readonly_fields = ['created_at']
    fk_name = 'subscription'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Admin interface for Subscription model."""
    list_display = ('get_trainer_name', 'plan', 'paddle_subscription_id', 'status', 'current_period_end', 'created_at')
    list_filter = ('plan', 'status', 'created_at')
    search_fields = ('trainer__business_name', 'trainer__user__email', 'paddle_subscription_id', 'paddle_customer_id')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    inlines = [PaymentInline]
    
    fieldsets = (
        ('Subscription Information', {
            'fields': ('trainer', 'paddle_subscription_id', 'paddle_customer_id', 'plan', 'status')
        }),
        ('Billing Period', {
            'fields': ('current_period_start', 'current_period_end', 'cancel_at_period_end', 'cancelled_at', 'trial_end')
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
    search_fields = ('trainer__business_name', 'paddle_transaction_id', 'paddle_invoice_id')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('subscription', 'trainer', 'amount', 'currency', 'paddle_transaction_id', 'paddle_invoice_id')
        }),
        ('Details', {
            'fields': ('status', 'payment_method', 'receipt_url')
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        queryset = super().get_queryset(request)
        return queryset.select_related('subscription', 'subscription__trainer', 'trainer')
    
    def get_trainer_name(self, obj):
        if obj.subscription and obj.subscription.trainer:
            return obj.subscription.trainer.business_name
        elif obj.trainer:
            return obj.trainer.business_name
        return 'N/A'
    get_trainer_name.short_description = 'Trainer'


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    """Admin interface for webhook events."""
    list_display = ['event_id', 'event_type', 'processed', 'processed_at', 'created_at']
    list_filter = ['event_type', 'processed', 'created_at']
    search_fields = ['event_id', 'event_type']
    readonly_fields = ['event_id', 'event_type', 'payload', 'processed', 'processed_at', 'error_message', 'created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Event Information', {
            'fields': ('event_id', 'event_type', 'processed', 'processed_at')
        }),
        ('Payload', {
            'fields': ('payload',),
            'classes': ('collapse',)
        }),
        ('Error', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )
    
    def has_add_permission(self, request):
        """Webhook events are created automatically."""
        return False


@admin.register(ClientPayment)
class ClientPaymentAdmin(admin.ModelAdmin):
    """Admin interface for ClientPayment model."""
    list_display = ('get_client_name', 'amount', 'currency', 'payment_method', 'payment_date', 'recorded_by', 'created_at')
    list_filter = ('payment_method', 'currency', 'payment_date', 'created_at')
    search_fields = ('client__first_name', 'client__last_name', 'client__email', 'reference_id', 'notes')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-payment_date', '-created_at')
    date_hierarchy = 'payment_date'
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('client', 'amount', 'currency', 'payment_method', 'payment_date')
        }),
        ('Details', {
            'fields': ('reference_id', 'notes', 'package', 'booking')
        }),
        ('Recorded By', {
            'fields': ('recorded_by',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        queryset = super().get_queryset(request)
        return queryset.select_related('client', 'client__trainer', 'recorded_by', 'package', 'booking')
    
    def get_client_name(self, obj):
        return obj.client.get_full_name()
    get_client_name.short_description = 'Client'
    get_client_name.admin_order_field = 'client__first_name'
