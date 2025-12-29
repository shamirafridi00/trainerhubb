from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, timedelta
from django.utils import timezone

from .models import AvailabilitySlot, TrainerBreak
from .serializers import AvailabilitySlotSerializer, TrainerBreakSerializer, AvailableSlotsSerializer
from .utils import get_available_slots
from apps.trainers.models import Trainer


class AvailabilitySlotViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing trainer availability slots.
    """
    serializer_class = AvailabilitySlotSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get only availability slots for current trainer."""
        try:
            trainer = self.request.user.trainer_profile
            return AvailabilitySlot.objects.filter(trainer=trainer)
        except Trainer.DoesNotExist:
            return AvailabilitySlot.objects.none()
    
    def perform_create(self, serializer):
        """Create availability slot for current trainer."""
        trainer = self.request.user.trainer_profile
        serializer.save(trainer=trainer)
    
    @action(detail=False, methods=['get'])
    def available_slots(self, request):
        """
        Get available slots for a trainer within date range.
        
        GET /api/availability-slots/available-slots/?trainer_id=1&start_date=2025-01-01&end_date=2025-01-31
        
        Query params:
            trainer_id: ID of trainer (required)
            start_date: Start date in YYYY-MM-DD format (required)
            end_date: End date in YYYY-MM-DD format (required)
            duration: Slot duration in minutes (optional, default 60)
        """
        trainer_id = request.query_params.get('trainer_id')
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        duration = int(request.query_params.get('duration', 60))
        
        # Validate required parameters
        if not all([trainer_id, start_date_str, end_date_str]):
            return Response(
                {'error': 'trainer_id, start_date, and end_date are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        available = get_available_slots(int(trainer_id), start_date, end_date, duration)
        
        return Response({
            'trainer_id': trainer_id,
            'start_date': start_date_str,
            'end_date': end_date_str,
            'available_slots': available
        })


class TrainerBreakViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing trainer breaks/vacation.
    """
    serializer_class = TrainerBreakSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get only breaks for current trainer."""
        try:
            trainer = self.request.user.trainer_profile
            return TrainerBreak.objects.filter(trainer=trainer)
        except Trainer.DoesNotExist:
            return TrainerBreak.objects.none()
    
    def perform_create(self, serializer):
        """Create break for current trainer."""
        trainer = self.request.user.trainer_profile
        serializer.save(trainer=trainer)
