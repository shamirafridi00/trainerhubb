from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Client, ClientNote
from .serializers import ClientSerializer, ClientDetailSerializer, ClientNoteSerializer
from apps.trainers.models import Trainer
from apps.payments.models import ClientPayment
from apps.payments.serializers import ClientPaymentSerializer


class ClientViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing trainer's clients.
    """
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['fitness_level', 'is_active']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    ordering_fields = ['created_at', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get only clients for current trainer with optimized queries."""
        try:
            trainer = self.request.user.trainer_profile
            return Client.objects.filter(trainer=trainer).select_related(
                'trainer__user'
            ).prefetch_related(
                'client_notes',
                'payments'
            )
        except Trainer.DoesNotExist:
            return Client.objects.none()
    
    def get_serializer_class(self):
        """Use detailed serializer for retrieve action."""
        if self.action == 'retrieve':
            return ClientDetailSerializer
        return ClientSerializer
    
    def perform_create(self, serializer):
        """Create client for current trainer."""
        trainer = self.request.user.trainer_profile
        serializer.save(trainer=trainer)
    
    @action(detail=True, methods=['post'], url_path='add-note')
    def add_note(self, request, pk=None):
        """
        Add a note to a client.
        
        POST /api/clients/{id}/add-note/
        {
            "content": "Client is making great progress!"
        }
        """
        client = self.get_object()
        content = request.data.get('content')
        
        if not content:
            return Response(
                {'error': 'Content is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        note = ClientNote.objects.create(
            client=client,
            content=content,
            created_by=request.user
        )
        serializer = ClientNoteSerializer(note)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def notes(self, request, pk=None):
        """
        Get all notes for a client.
        
        GET /api/clients/{id}/notes/
        """
        client = self.get_object()
        notes = client.client_notes.all()
        serializer = ClientNoteSerializer(notes, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def bookings(self, request, pk=None):
        """
        Get all bookings for a client.
        
        GET /api/clients/{id}/bookings/
        
        Note: Will be fully implemented in Epic 4
        """
        client = self.get_object()
        # Placeholder - will be implemented in Epic 4 when Booking model exists
        return Response({
            'client_id': client.id,
            'bookings': [],
            'message': 'Bookings will be available in Epic 4'
        })
    
    @action(detail=True, methods=['get', 'post'], url_path='payments')
    def payments(self, request, pk=None):
        """
        Get or create payments for a client.
        
        GET /api/clients/{id}/payments/ - Get payment history
        POST /api/clients/{id}/payments/ - Record new payment
        """
        client = self.get_object()
        
        if request.method == 'GET':
            payments = ClientPayment.objects.filter(client=client).select_related(
                'recorded_by', 'package', 'booking'
            ).order_by('-payment_date', '-created_at')
            serializer = ClientPaymentSerializer(payments, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = ClientPaymentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(client=client, recorded_by=request.user)
                
                # Update client payment status
                from django.db.models import Sum
                total_paid = ClientPayment.objects.filter(client=client).aggregate(Sum('amount'))['amount__sum'] or 0
                latest_payment = ClientPayment.objects.filter(client=client).order_by('-payment_date').first()
                
                client.total_paid = total_paid
                client.last_payment_date = latest_payment.payment_date if latest_payment else None
                client.payment_status = 'paid' if total_paid > 0 else 'unpaid'
                client.save()
                
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
