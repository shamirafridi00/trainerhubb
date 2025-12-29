from rest_framework import serializers
from .models import Subscription, Payment


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payments."""
    trainer_name = serializers.CharField(source='subscription.trainer.business_name', read_only=True)
    
    class Meta:
        model = Payment
        fields = ['id', 'amount', 'currency', 'paddle_transaction_id', 'status', 'trainer_name', 'created_at']
        read_only_fields = ['id', 'created_at', 'trainer_name']


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for subscriptions."""
    payments = PaymentSerializer(many=True, read_only=True)
    trainer_name = serializers.CharField(source='trainer.business_name', read_only=True)
    total_payments = serializers.SerializerMethodField()
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'trainer', 'trainer_name', 'paddle_subscription_id', 'status', 
            'next_billing_date', 'total_payments', 'payments', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'trainer_name', 'total_payments']
    
    def get_total_payments(self, obj):
        """Calculate total amount from all completed payments."""
        return sum(
            payment.amount for payment in obj.payments.filter(status='completed')
        )


class CreateSubscriptionSerializer(serializers.Serializer):
    """Serializer for creating subscriptions."""
    paddle_subscription_id = serializers.CharField(max_length=255)
    status = serializers.CharField(default='active')
    next_billing_date = serializers.DateField(required=False, allow_null=True)
    
    def validate_status(self, value):
        """Validate status is valid."""
        valid_statuses = ['active', 'paused', 'cancelled', 'expired']
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        return value

