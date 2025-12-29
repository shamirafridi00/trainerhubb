from rest_framework import serializers
from .models import DashboardMetrics


class DashboardMetricsSerializer(serializers.ModelSerializer):
    """Serializer for dashboard metrics."""
    trainer_name = serializers.CharField(source='trainer.business_name', read_only=True)
    completion_rate = serializers.SerializerMethodField()
    cancellation_rate = serializers.SerializerMethodField()
    average_revenue_per_booking = serializers.SerializerMethodField()
    
    class Meta:
        model = DashboardMetrics
        fields = [
            'id', 'trainer', 'trainer_name', 'date', 'bookings_count',
            'completed_bookings', 'cancelled_bookings', 'revenue',
            'new_clients', 'active_clients', 'average_session_rating',
            'completion_rate', 'cancellation_rate', 'average_revenue_per_booking',
            'created_at'
        ]
        read_only_fields = [
            'id', 'trainer', 'trainer_name', 'created_at',
            'completion_rate', 'cancellation_rate', 'average_revenue_per_booking'
        ]
    
    def get_completion_rate(self, obj):
        """Get completion rate as percentage."""
        return obj.completion_rate
    
    def get_cancellation_rate(self, obj):
        """Get cancellation rate as percentage."""
        return obj.cancellation_rate
    
    def get_average_revenue_per_booking(self, obj):
        """Get average revenue per booking."""
        return obj.average_revenue_per_booking

