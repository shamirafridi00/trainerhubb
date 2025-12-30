"""
Admin Panel Serializers
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.trainers.models import Trainer
from apps.clients.models import Client
from apps.bookings.models import Booking
from .models import AdminActionLog, PlatformSettings

User = get_user_model()


class TrainerAdminSerializer(serializers.ModelSerializer):
    """
    Detailed trainer information for admin panel.
    """
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    user_is_active = serializers.BooleanField(source='user.is_active', read_only=True)
    subscription_status = serializers.SerializerMethodField()
    subscription_plan = serializers.SerializerMethodField()
    total_clients = serializers.SerializerMethodField()
    total_bookings = serializers.SerializerMethodField()
    total_pages = serializers.SerializerMethodField()
    custom_domain = serializers.SerializerMethodField()
    
    class Meta:
        model = Trainer
        fields = [
            'id', 'user_id', 'user_email', 'user_is_active',
            'business_name', 'bio', 'expertise', 'location',
            'timezone', 'rating', 'total_sessions', 'is_verified',
            'subscription_status', 'subscription_plan',
            'total_clients', 'total_bookings', 'total_pages',
            'custom_domain', 'created_at', 'updated_at'
        ]
    
    def get_subscription_status(self, obj):
        """Get subscription status from payments app."""
        try:
            from apps.payments.models import Subscription
            subscription = Subscription.objects.filter(trainer=obj).first()
            return subscription.status if subscription else 'free'
        except:
            return 'free'
    
    def get_subscription_plan(self, obj):
        """Get subscription plan."""
        try:
            from apps.payments.models import Subscription
            subscription = Subscription.objects.filter(trainer=obj).first()
            return subscription.plan if subscription else 'free'
        except:
            return 'free'
    
    def get_total_clients(self, obj):
        """Count total clients."""
        return obj.clients.filter(is_active=True).count()
    
    def get_total_bookings(self, obj):
        """Count total bookings."""
        return obj.bookings.count()
    
    def get_total_pages(self, obj):
        """Count published pages."""
        try:
            return 1 if hasattr(obj, 'landing_page') and obj.landing_page.is_published else 0
        except:
            return 0
    
    def get_custom_domain(self, obj):
        """Get custom domain if exists."""
        try:
            from apps.payments.models import CustomDomain
            domain = CustomDomain.objects.filter(trainer=obj, status='active').first()
            return domain.domain if domain else None
        except:
            return None


class TrainerDetailAdminSerializer(TrainerAdminSerializer):
    """
    Extended trainer details including related data.
    """
    recent_clients = serializers.SerializerMethodField()
    recent_bookings = serializers.SerializerMethodField()
    payment_history = serializers.SerializerMethodField()
    
    class Meta(TrainerAdminSerializer.Meta):
        fields = TrainerAdminSerializer.Meta.fields + [
            'recent_clients', 'recent_bookings', 'payment_history'
        ]
    
    def get_recent_clients(self, obj):
        """Get 5 most recent clients."""
        clients = obj.clients.filter(is_active=True).order_by('-created_at')[:5]
        return [{
            'id': c.id,
            'name': c.get_full_name(),
            'email': c.email,
            'created_at': c.created_at
        } for c in clients]
    
    def get_recent_bookings(self, obj):
        """Get 5 most recent bookings."""
        bookings = obj.bookings.order_by('-created_at')[:5]
        return [{
            'id': b.id,
            'client_name': b.client.get_full_name(),
            'start_time': b.start_time,
            'status': b.status
        } for b in bookings]
    
    def get_payment_history(self, obj):
        """Get payment history from Paddle."""
        try:
            from apps.payments.models import Payment
            payments = Payment.objects.filter(
                subscription__trainer=obj
            ).order_by('-created_at')[:10]
            return [{
                'id': p.id,
                'amount': str(p.amount),
                'currency': p.currency,
                'status': p.status,
                'created_at': p.created_at
            } for p in payments]
        except:
            return []


class AdminActionLogSerializer(serializers.ModelSerializer):
    """
    Serializer for admin action logs.
    """
    admin_email = serializers.EmailField(source='admin_user.email', read_only=True)
    trainer_name = serializers.CharField(source='target_trainer.business_name', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = AdminActionLog
        fields = [
            'id', 'admin_email', 'action', 'action_display',
            'trainer_name', 'target_trainer', 'details',
            'ip_address', 'created_at'
        ]
        read_only_fields = fields


class PlatformStatsSerializer(serializers.Serializer):
    """
    Platform-wide statistics for admin dashboard.
    """
    total_trainers = serializers.IntegerField()
    active_trainers = serializers.IntegerField()
    total_clients = serializers.IntegerField()
    total_bookings = serializers.IntegerField()
    new_signups_this_month = serializers.IntegerField()
    total_revenue_this_month = serializers.DecimalField(max_digits=10, decimal_places=2)
    mrr = serializers.DecimalField(max_digits=10, decimal_places=2)
    churn_rate = serializers.FloatField()
    subscription_breakdown = serializers.DictField()


class TrainerAccountActionSerializer(serializers.Serializer):
    """
    Serializer for trainer account actions (suspend, activate, delete).
    """
    action = serializers.ChoiceField(choices=['suspend', 'activate', 'delete', 'verify'])
    reason = serializers.CharField(required=False, allow_blank=True)


class ImpersonateSerializer(serializers.Serializer):
    """
    Serializer for impersonation.
    """
    trainer_id = serializers.IntegerField()
    reason = serializers.CharField(required=False, allow_blank=True)


class RevenueTrendSerializer(serializers.Serializer):
    """
    Serializer for revenue trend data points.
    """
    date = serializers.CharField()
    revenue = serializers.FloatField()


class SignupTrendSerializer(serializers.Serializer):
    """
    Serializer for signup trend data points.
    """
    date = serializers.CharField()
    signups = serializers.IntegerField()


class ActiveUsersTrendSerializer(serializers.Serializer):
    """
    Serializer for active users trend data points.
    """
    date = serializers.CharField()
    active_users = serializers.IntegerField()


class GeographicDistributionSerializer(serializers.Serializer):
    """
    Serializer for geographic distribution data.
    """
    location = serializers.CharField()
    count = serializers.IntegerField()


class BookingTrendSerializer(serializers.Serializer):
    """
    Serializer for booking trend data points.
    """
    date = serializers.CharField()
    bookings = serializers.IntegerField()


class ClientGrowthTrendSerializer(serializers.Serializer):
    """
    Serializer for client growth trend data points.
    """
    date = serializers.CharField()
    new_clients = serializers.IntegerField()


class TopPerformingTrainerSerializer(serializers.Serializer):
    """
    Serializer for top performing trainers.
    """
    trainer_id = serializers.IntegerField()
    business_name = serializers.CharField()
    email = serializers.EmailField()
    total_revenue = serializers.FloatField()
    total_bookings = serializers.IntegerField()
    location = serializers.CharField()


class AnalyticsDashboardSerializer(serializers.Serializer):
    """
    Complete analytics dashboard data.
    """
    revenue_trends = RevenueTrendSerializer(many=True)
    signup_trends = SignupTrendSerializer(many=True)
    active_users_trends = ActiveUsersTrendSerializer(many=True)
    geographic_distribution = GeographicDistributionSerializer(many=True)
    booking_trends = BookingTrendSerializer(many=True)
    client_growth_trends = ClientGrowthTrendSerializer(many=True)
    revenue_by_plan = serializers.ListField(child=serializers.DictField())
    top_performing_trainers = TopPerformingTrainerSerializer(many=True)

