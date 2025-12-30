from rest_framework import serializers
from .models import Subscription, Payment, WebhookEvent, ClientPayment


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payments."""
    trainer_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = [
            'id', 'amount', 'currency', 'paddle_transaction_id', 'paddle_invoice_id',
            'status', 'payment_method', 'receipt_url', 'trainer_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'trainer_name']
    
    def get_trainer_name(self, obj):
        if obj.subscription and obj.subscription.trainer:
            return obj.subscription.trainer.business_name
        elif obj.trainer:
            return obj.trainer.business_name
        return None


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for subscriptions."""
    trainer_name = serializers.CharField(source='trainer.business_name', read_only=True)
    total_payments = serializers.SerializerMethodField()
    is_active = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'trainer', 'trainer_name', 'paddle_subscription_id', 'paddle_customer_id',
            'plan', 'status', 'is_active', 'current_period_start', 'current_period_end',
            'cancel_at_period_end', 'cancelled_at', 'trial_end', 'total_payments',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'trainer_name', 'total_payments', 'is_active'
        ]
    
    def get_total_payments(self, obj):
        """Calculate total amount from all completed payments."""
        return float(sum(
            payment.amount for payment in obj.payments.filter(status='completed')
        ))


class WebhookEventSerializer(serializers.ModelSerializer):
    """Serializer for webhook events."""
    
    class Meta:
        model = WebhookEvent
        fields = [
            'id', 'event_id', 'event_type', 'payload', 'processed',
            'processed_at', 'error_message', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ClientPaymentSerializer(serializers.ModelSerializer):
    """Serializer for client payments (manual tracking)."""
    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    recorded_by_name = serializers.CharField(source='recorded_by.email', read_only=True)
    
    class Meta:
        model = ClientPayment
        fields = [
            'id', 'client', 'client_name', 'amount', 'currency', 'payment_method',
            'payment_date', 'reference_id', 'notes', 'recorded_by', 'recorded_by_name',
            'package', 'booking', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'recorded_by', 'created_at', 'updated_at']
    
    def validate_amount(self, value):
        """Validate amount is positive."""
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

