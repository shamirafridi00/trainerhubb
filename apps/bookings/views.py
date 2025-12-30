from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone

from .models import Booking
from .serializers import BookingSerializer, BookingCreateSerializer, BookingDetailSerializer
from apps.trainers.models import Trainer
from apps.packages.models import Service


class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing bookings.
    """
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'client']
    search_fields = ['client__first_name', 'client__last_name', 'notes']
    ordering_fields = ['start_time', 'created_at']
    ordering = ['-start_time']
    
    def get_queryset(self):
        """Get only bookings for current trainer with optimized queries."""
        try:
            trainer = self.request.user.trainer_profile
            return Booking.objects.filter(trainer=trainer).select_related(
                'client',
                'trainer',
                'service'
            ).prefetch_related(
                'payments'
            )
        except Trainer.DoesNotExist:
            return Booking.objects.none()
    
    def get_serializer_class(self):
        """Use different serializers based on action."""
        if self.action == 'create':
            return BookingCreateSerializer
        elif self.action == 'retrieve':
            return BookingDetailSerializer
        return BookingSerializer
    
    def perform_create(self, serializer):
        """Validate and create booking."""
        trainer = self.request.user.trainer_profile
        serializer.save(trainer=trainer)
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """
        Confirm a pending booking.
        
        POST /api/bookings/{id}/confirm/
        """
        booking = self.get_object()
        
        if booking.status != 'pending':
            return Response(
                {'error': f'Booking is {booking.status}, cannot confirm'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = 'confirmed'
        booking.save()
        
        # Send confirmation notifications asynchronously
        from apps.notifications.tasks import send_booking_confirmation
        send_booking_confirmation.delay(booking.id)
        
        serializer = self.get_serializer(booking)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel a booking.
        
        POST /api/bookings/{id}/cancel/
        {
            "reason": "Client requested cancellation"
        }
        """
        booking = self.get_object()
        
        if booking.status in ['completed', 'cancelled', 'no-show']:
            return Response(
                {'error': f'Cannot cancel a {booking.status} booking'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reason = request.data.get('reason', '')
        booking.status = 'cancelled'
        booking.cancellation_reason = reason
        booking.save()
        
        serializer = self.get_serializer(booking)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='mark-completed')
    def mark_completed(self, request, pk=None):
        """
        Mark a booking as completed.
        
        POST /api/bookings/{id}/mark-completed/
        """
        booking = self.get_object()
        
        if booking.status != 'confirmed':
            return Response(
                {'error': 'Only confirmed bookings can be marked as completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = 'completed'
        booking.save()
        
        serializer = self.get_serializer(booking)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """
        Get upcoming bookings.
        
        GET /api/bookings/upcoming/
        """
        bookings = self.get_queryset().filter(
            status__in=['pending', 'confirmed'],
            start_time__gte=timezone.now()
        )
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def past(self, request):
        """
        Get past bookings.
        
        GET /api/bookings/past/
        """
        bookings = self.get_queryset().filter(
            end_time__lt=timezone.now()
        )
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)
