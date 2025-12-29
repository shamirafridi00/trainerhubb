from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications."""
    trainer_name = serializers.CharField(source='trainer.business_name', read_only=True)
    type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'trainer', 'trainer_name', 'notification_type', 'type_display',
            'recipient', 'subject', 'message', 'status', 'status_display',
            'sent_at', 'failed_reason', 'created_at'
        ]
        read_only_fields = [
            'id', 'trainer', 'trainer_name', 'type_display', 'status_display',
            'sent_at', 'failed_reason', 'created_at'
        ]

