from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import timedelta, datetime

from .models import DashboardMetrics
from .serializers import DashboardMetricsSerializer
from apps.bookings.models import Booking
from apps.clients.models import Client
from apps.payments.models import Payment
from apps.trainers.models import Trainer


class AnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for analytics and dashboard."""
    serializer_class = DashboardMetricsSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['date']
    ordering_fields = ['date', 'created_at']
    ordering = ['-date']
    
    def get_queryset(self):
        """Get metrics for current trainer."""
        try:
            trainer = self.request.user.trainer_profile
            return DashboardMetrics.objects.filter(trainer=trainer).select_related('trainer')
        except Trainer.DoesNotExist:
            return DashboardMetrics.objects.none()
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """
        Get dashboard summary.
        
        GET /api/analytics/dashboard/
        """
        try:
            trainer = request.user.trainer_profile
        except Trainer.DoesNotExist:
            return Response(
                {'error': 'Trainer profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        now = timezone.now()
        today = now.date()
        this_month = today.replace(day=1)
        
        # Bookings
        bookings = Booking.objects.filter(trainer=trainer)
        total_bookings = bookings.count()
        completed_bookings = bookings.filter(status='completed').count()
        upcoming_bookings = bookings.filter(
            status__in=['pending', 'confirmed'],
            start_time__gte=now
        ).count()
        
        # Clients
        total_clients = Client.objects.filter(trainer=trainer).count()
        new_clients_count = Client.objects.filter(
            trainer=trainer,
            created_at__gte=this_month
        ).count()
        active_clients = Client.objects.filter(trainer=trainer, is_active=True).count()
        
        # Revenue
        payments = Payment.objects.filter(subscription__trainer=trainer, status='completed')
        total_revenue = payments.aggregate(Sum('amount'))['amount__sum'] or 0
        monthly_revenue = payments.filter(
            created_at__gte=this_month
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Calculate average booking value
        average_booking_value = 0
        if total_bookings > 0:
            average_booking_value = float(total_revenue) / total_bookings
        
        return Response({
            'total_bookings': total_bookings,
            'completed_bookings': completed_bookings,
            'upcoming_bookings': upcoming_bookings,
            'total_clients': total_clients,
            'active_clients': active_clients,
            'new_clients': new_clients_count,
            'total_revenue': float(total_revenue),
            'monthly_revenue': float(monthly_revenue),
            'average_booking_value': average_booking_value,
        })
    
    @action(detail=False, methods=['get'])
    def revenue(self, request):
        """
        Get revenue analytics.
        
        GET /api/analytics/revenue/?period=month
        Query params: period (week, month, year)
        """
        try:
            trainer = request.user.trainer_profile
        except Trainer.DoesNotExist:
            return Response(
                {'error': 'Trainer profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        period = request.query_params.get('period', 'month')
        now = timezone.now()
        
        if period == 'week':
            start_date = now - timedelta(days=7)
        elif period == 'month':
            start_date = now - timedelta(days=30)
        elif period == 'year':
            start_date = now - timedelta(days=365)
        else:
            start_date = now - timedelta(days=30)
        
        payments = Payment.objects.filter(
            subscription__trainer=trainer,
            status='completed',
            created_at__gte=start_date
        )
        
        total_revenue = payments.aggregate(Sum('amount'))['amount__sum'] or 0
        payment_count = payments.count()
        average_payment = float(total_revenue) / payment_count if payment_count > 0 else 0
        
        return Response({
            'period': period,
            'total_revenue': float(total_revenue),
            'payment_count': payment_count,
            'average_payment': average_payment,
            'start_date': start_date.date().isoformat(),
            'end_date': now.date().isoformat(),
        })
    
    @action(detail=False, methods=['get'], url_path='bookings-stats')
    def bookings_stats(self, request):
        """
        Get booking statistics.
        
        GET /api/analytics/bookings-stats/
        """
        try:
            trainer = request.user.trainer_profile
        except Trainer.DoesNotExist:
            return Response(
                {'error': 'Trainer profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        bookings = Booking.objects.filter(trainer=trainer)
        total = bookings.count()
        
        # Status breakdown
        status_breakdown = {}
        for status_choice in Booking.STATUS_CHOICES:
            count = bookings.filter(status=status_choice[0]).count()
            status_breakdown[status_choice[0]] = count
        
        # Calculate rates
        completion_rate = 0
        cancellation_rate = 0
        if total > 0:
            completed = bookings.filter(status='completed').count()
            cancelled = bookings.filter(status='cancelled').count()
            completion_rate = round((completed / total) * 100, 2)
            cancellation_rate = round((cancelled / total) * 100, 2)
        
        return Response({
            'total': total,
            'by_status': status_breakdown,
            'completion_rate': completion_rate,
            'cancellation_rate': cancellation_rate,
        })
    
    @action(detail=False, methods=['get'], url_path='client-stats')
    def client_stats(self, request):
        """
        Get client statistics.
        
        GET /api/analytics/client-stats/
        """
        try:
            trainer = request.user.trainer_profile
        except Trainer.DoesNotExist:
            return Response(
                {'error': 'Trainer profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        clients = Client.objects.filter(trainer=trainer)
        total_clients = clients.count()
        active_clients = clients.filter(is_active=True).count()
        inactive_clients = clients.filter(is_active=False).count()
        
        # Fitness level breakdown
        fitness_level_breakdown = {}
        for level_choice in Client.FITNESS_LEVEL_CHOICES:
            count = clients.filter(fitness_level=level_choice[0]).count()
            fitness_level_breakdown[level_choice[0]] = count
        
        return Response({
            'total_clients': total_clients,
            'active_clients': active_clients,
            'inactive_clients': inactive_clients,
            'by_fitness_level': fitness_level_breakdown,
        })
    
    @action(detail=False, methods=['get'], url_path='metrics-summary')
    def metrics_summary(self, request):
        """
        Get summary of metrics for date range.
        
        GET /api/analytics/metrics-summary/?start_date=2025-01-01&end_date=2025-01-31
        """
        try:
            trainer = request.user.trainer_profile
        except Trainer.DoesNotExist:
            return Response(
                {'error': 'Trainer profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        
        # Default to last 30 days if not provided
        if not start_date_str:
            start_date = timezone.now().date() - timedelta(days=30)
        else:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        
        if not end_date_str:
            end_date = timezone.now().date()
        else:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        
        metrics = DashboardMetrics.objects.filter(
            trainer=trainer,
            date__gte=start_date,
            date__lte=end_date
        )
        
        # Aggregate metrics
        total_bookings = metrics.aggregate(Sum('bookings_count'))['bookings_count__sum'] or 0
        total_completed = metrics.aggregate(Sum('completed_bookings'))['completed_bookings__sum'] or 0
        total_cancelled = metrics.aggregate(Sum('cancelled_bookings'))['cancelled_bookings__sum'] or 0
        total_revenue = metrics.aggregate(Sum('revenue'))['revenue__sum'] or 0
        total_new_clients = metrics.aggregate(Sum('new_clients'))['new_clients__sum'] or 0
        
        # Calculate averages
        avg_rating = metrics.aggregate(Avg('average_session_rating'))['average_session_rating__avg'] or 0
        
        return Response({
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'total_bookings': total_bookings,
            'total_completed_bookings': total_completed,
            'total_cancelled_bookings': total_cancelled,
            'total_revenue': float(total_revenue),
            'total_new_clients': total_new_clients,
            'average_session_rating': round(float(avg_rating), 2),
            'completion_rate': round((total_completed / total_bookings * 100), 2) if total_bookings > 0 else 0,
            'cancellation_rate': round((total_cancelled / total_bookings * 100), 2) if total_bookings > 0 else 0,
        })

