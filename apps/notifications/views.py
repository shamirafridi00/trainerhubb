from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from datetime import timedelta

from .models import Notification
from .serializers import NotificationSerializer
from apps.trainers.models import Trainer


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing notifications.
    Read-only - notifications are created by services/tasks.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['notification_type', 'status']
    search_fields = ['recipient', 'subject', 'message']
    ordering_fields = ['created_at', 'sent_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get only notifications for current trainer."""
        try:
            trainer = self.request.user.trainer_profile
            return Notification.objects.filter(trainer=trainer).select_related('trainer')
        except Trainer.DoesNotExist:
            return Notification.objects.none()
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get notification statistics.
        
        GET /api/notifications/stats/
        """
        try:
            trainer = request.user.trainer_profile
            notifications = Notification.objects.filter(trainer=trainer)
            
            total = notifications.count()
            sent = notifications.filter(status='sent').count()
            failed = notifications.filter(status='failed').count()
            pending = notifications.filter(status='pending').count()
            
            # By type
            email_count = notifications.filter(notification_type='email').count()
            sms_count = notifications.filter(notification_type='sms').count()
            push_count = notifications.filter(notification_type='push').count()
            
            # Recent activity (last 7 days)
            week_ago = timezone.now() - timedelta(days=7)
            recent_sent = notifications.filter(
                status='sent',
                sent_at__gte=week_ago
            ).count()
            
            # Success rate
            success_rate = (sent / total * 100) if total > 0 else 0
            
            return Response({
                'total': total,
                'sent': sent,
                'failed': failed,
                'pending': pending,
                'by_type': {
                    'email': email_count,
                    'sms': sms_count,
                    'push': push_count,
                },
                'recent_sent_7_days': recent_sent,
                'success_rate': round(success_rate, 2),
            })
        except Trainer.DoesNotExist:
            return Response({
                'total': 0,
                'sent': 0,
                'failed': 0,
                'pending': 0,
                'by_type': {'email': 0, 'sms': 0, 'push': 0},
                'recent_sent_7_days': 0,
                'success_rate': 0,
            })
    
    @action(detail=False, methods=['get'], url_path='recent')
    def recent(self, request):
        """
        Get recent notifications (last 7 days).
        
        GET /api/notifications/recent/
        """
        try:
            trainer = request.user.trainer_profile
            week_ago = timezone.now() - timedelta(days=7)
            
            notifications = Notification.objects.filter(
                trainer=trainer,
                created_at__gte=week_ago
            ).select_related('trainer').order_by('-created_at')
            
            serializer = self.get_serializer(notifications, many=True)
            return Response(serializer.data)
        except Trainer.DoesNotExist:
            return Response([])
    
    @action(detail=False, methods=['get'], url_path='failed')
    def failed(self, request):
        """
        Get failed notifications.
        
        GET /api/notifications/failed/
        """
        try:
            trainer = request.user.trainer_profile
            notifications = Notification.objects.filter(
                trainer=trainer,
                status='failed'
            ).select_related('trainer').order_by('-created_at')
            
            serializer = self.get_serializer(notifications, many=True)
            return Response(serializer.data)
        except Trainer.DoesNotExist:
            return Response([])

