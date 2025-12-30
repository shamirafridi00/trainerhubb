"""
Payment Views
Handles Paddle webhooks and subscription management endpoints.
"""
import json
import logging
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
import csv
from io import StringIO

from .models import Subscription, Payment, WebhookEvent, ClientPayment
from .serializers import SubscriptionSerializer, PaymentSerializer, ClientPaymentSerializer
from .utils import get_revenue_summary, get_recent_payments
from .paddle_webhooks import PaddleWebhookHandler

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def paddle_webhook(request):
    """
    Paddle webhook endpoint.
    Receives and processes Paddle webhook events.
    
    POST /api/payments/paddle-webhook/
    """
    try:
        # Parse JSON payload
        payload = json.loads(request.body)
        
        # Get signature from headers
        signature = request.headers.get('Paddle-Signature')
        
        # Process webhook
        handler = PaddleWebhookHandler(payload, signature)
        success, message = handler.process()
        
        if success:
            logger.info(f"Webhook processed successfully: {message}")
            return JsonResponse({'status': 'success', 'message': message})
        else:
            logger.error(f"Webhook processing failed: {message}")
            return JsonResponse(
                {'status': 'error', 'message': message},
                status=400
            )
            
    except json.JSONDecodeError:
        logger.error("Invalid JSON in webhook payload")
        return JsonResponse(
            {'status': 'error', 'message': 'Invalid JSON'},
            status=400
        )
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}", exc_info=True)
        return JsonResponse(
            {'status': 'error', 'message': str(e)},
            status=500
        )


class SubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Subscription management endpoints.
    Trainers can view their subscription details.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionSerializer
    
    def get_queryset(self):
        """Filter to current user's subscription."""
        if hasattr(self.request.user, 'trainer_profile'):
            return Subscription.objects.filter(
                trainer=self.request.user.trainer_profile
            )
        return Subscription.objects.none()
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """
        Get current user's subscription.
        
        GET /api/payments/subscriptions/current/
        """
        if not hasattr(request.user, 'trainer_profile'):
            return Response(
                {'error': 'User is not a trainer'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            subscription = Subscription.objects.get(
                trainer=request.user.trainer_profile
            )
            serializer = self.get_serializer(subscription)
            return Response(serializer.data)
        except Subscription.DoesNotExist:
            # Create free tier subscription if doesn't exist
            subscription = Subscription.objects.create(
                trainer=request.user.trainer_profile,
                plan='free',
                status='active'
            )
            serializer = self.get_serializer(subscription)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def features(self, request):
        """
        Get feature limits for current subscription.
        
        GET /api/payments/subscriptions/features/
        """
        if not hasattr(request.user, 'trainer_profile'):
            return Response(
                {'error': 'User is not a trainer'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            subscription = Subscription.objects.get(
                trainer=request.user.trainer_profile
            )
        except Subscription.DoesNotExist:
            # Default to free tier
            subscription = Subscription(plan='free')
        
        features = {
            'plan': subscription.plan,
            'status': subscription.status,
            'is_active': subscription.is_active(),
            'limits': {
                'max_clients': subscription.can_access_feature('max_clients'),
                'max_pages': subscription.can_access_feature('max_pages'),
                'custom_domain': subscription.can_access_feature('custom_domain'),
                'white_label': subscription.can_access_feature('white_label'),
                'workflows': subscription.can_access_feature('workflows'),
            }
        }
        
        return Response(features)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel subscription at period end.
        
        POST /api/payments/subscriptions/{id}/cancel/
        """
        subscription = self.get_object()
        
        # Check ownership
        if subscription.trainer != request.user.trainer_profile:
            return Response(
                {'error': 'Not authorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # TODO: Call Paddle API to cancel subscription
        # For now, just mark it locally
        subscription.cancel_at_period_end = True
        subscription.save()
        
        logger.info(f"Subscription {subscription.id} cancelled by user {request.user.id}")
        
        return Response({
            'message': 'Subscription will cancel at period end',
            'cancel_at': subscription.current_period_end
        })
    
    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """
        Pause subscription.
        
        POST /api/payments/subscriptions/{id}/pause/
        """
        subscription = self.get_object()
        
        # Check ownership
        if subscription.trainer != request.user.trainer_profile:
            return Response(
                {'error': 'Not authorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # TODO: Call Paddle API to pause subscription
        subscription.status = 'paused'
        subscription.save()
        
        logger.info(f"Subscription {subscription.id} paused by user {request.user.id}")
        
        return Response({'message': 'Subscription paused'})
    
    @action(detail=True, methods=['post'])
    def resume(self, request, pk=None):
        """
        Resume paused subscription.
        
        POST /api/payments/subscriptions/{id}/resume/
        """
        subscription = self.get_object()
        
        # Check ownership
        if subscription.trainer != request.user.trainer_profile:
            return Response(
                {'error': 'Not authorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # TODO: Call Paddle API to resume subscription
        subscription.status = 'active'
        subscription.cancel_at_period_end = False
        subscription.save()
        
        logger.info(f"Subscription {subscription.id} resumed by user {request.user.id}")
        
        return Response({'message': 'Subscription resumed'})


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Payment history endpoints.
    Trainers can view their payment history.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer
    
    def get_queryset(self):
        """Filter to current user's payments."""
        if hasattr(self.request.user, 'trainer_profile'):
            return Payment.objects.filter(
                trainer=self.request.user.trainer_profile
            ).order_by('-created_at')
        return Payment.objects.none()


class ClientPaymentViewSet(viewsets.ModelViewSet):
    """
    Client payment tracking endpoints.
    Trainers can record and manage client payments manually.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ClientPaymentSerializer
    
    def get_queryset(self):
        """Filter to current trainer's client payments."""
        if hasattr(self.request.user, 'trainer_profile'):
            trainer = self.request.user.trainer_profile
            # Get payments for all trainer's clients
            from apps.clients.models import Client
            client_ids = Client.objects.filter(trainer=trainer).values_list('id', flat=True)
            return ClientPayment.objects.filter(client_id__in=client_ids).select_related(
                'client', 'recorded_by', 'package', 'booking'
            ).order_by('-payment_date', '-created_at')
        return ClientPayment.objects.none()
    
    def perform_create(self, serializer):
        """Set recorded_by to current user."""
        serializer.save(recorded_by=self.request.user)
        
        # Update client payment status
        client = serializer.instance.client
        self._update_client_payment_status(client)
    
    def perform_update(self, serializer):
        """Update client payment status after payment update."""
        old_payment = self.get_object()
        serializer.save()
        
        # Recalculate client payment status
        client = serializer.instance.client
        self._update_client_payment_status(client)
    
    def perform_destroy(self, instance):
        """Update client payment status after payment deletion."""
        client = instance.client
        super().perform_destroy(instance)
        self._update_client_payment_status(client)
    
    def _update_client_payment_status(self, client):
        """Update client's total_paid and payment_status."""
        from django.db.models import Sum
        from django.utils import timezone
        
        payments = ClientPayment.objects.filter(client=client)
        total_paid = payments.aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Get latest payment date
        latest_payment = payments.order_by('-payment_date').first()
        last_payment_date = latest_payment.payment_date if latest_payment else None
        
        # Determine payment status (simplified - can be enhanced)
        # This is a placeholder - actual logic would compare against expected payments
        payment_status = 'paid' if total_paid > 0 else 'unpaid'
        
        client.total_paid = total_paid
        client.last_payment_date = last_payment_date
        client.payment_status = payment_status
        client.save()
    
    @action(detail=False, methods=['get'])
    def revenue_summary(self, request):
        """
        Get revenue summary for current trainer.
        
        GET /api/payments/client-payments/revenue-summary/
        """
        if not hasattr(request.user, 'trainer_profile'):
            return Response(
                {'error': 'User is not a trainer'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        trainer = request.user.trainer_profile
        summary = get_revenue_summary(trainer)
        
        return Response(summary)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        Get recent payments for current trainer.
        
        GET /api/payments/client-payments/recent/
        """
        if not hasattr(request.user, 'trainer_profile'):
            return Response(
                {'error': 'User is not a trainer'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        trainer = request.user.trainer_profile
        limit = int(request.query_params.get('limit', 10))
        recent_payments = get_recent_payments(trainer, limit)
        
        serializer = ClientPaymentSerializer(recent_payments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='unpaid')
    def unpaid_clients(self, request):
        """
        Get list of clients with unpaid status.
        
        GET /api/payments/client-payments/unpaid/
        """
        if not hasattr(request.user, 'trainer_profile'):
            return Response(
                {'error': 'User is not a trainer'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        trainer = request.user.trainer_profile
        from apps.clients.models import Client
        
        unpaid_clients = Client.objects.filter(
            trainer=trainer,
            payment_status__in=['unpaid', 'partial']
        ).select_related('trainer')
        
        # Calculate outstanding amounts (simplified)
        clients_data = []
        for client in unpaid_clients:
            clients_data.append({
                'id': client.id,
                'name': client.get_full_name(),
                'email': client.email,
                'total_paid': float(client.total_paid),
                'payment_status': client.payment_status,
                'last_payment_date': client.last_payment_date,
            })
        
        return Response(clients_data)
    
    @action(detail=False, methods=['get'], url_path='export')
    def export_payments(self, request):
        """
        Export payment history to CSV.
        
        GET /api/payments/client-payments/export/
        Query params:
            - start_date: Start date (YYYY-MM-DD)
            - end_date: End date (YYYY-MM-DD)
        """
        if not hasattr(request.user, 'trainer_profile'):
            return Response(
                {'error': 'User is not a trainer'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        trainer = request.user.trainer_profile
        from apps.clients.models import Client
        from django.utils.dateparse import parse_date
        
        client_ids = Client.objects.filter(trainer=trainer).values_list('id', flat=True)
        payments = ClientPayment.objects.filter(client_id__in=client_ids).select_related('client')
        
        # Filter by date range if provided
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date:
            payments = payments.filter(payment_date__gte=parse_date(start_date))
        if end_date:
            payments = payments.filter(payment_date__lte=parse_date(end_date))
        
        payments = payments.order_by('-payment_date', '-created_at')
        
        # Create CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'Date', 'Client', 'Email', 'Amount', 'Currency', 'Payment Method',
            'Reference ID', 'Notes', 'Recorded By', 'Created At'
        ])
        
        # Data rows
        for payment in payments:
            writer.writerow([
                payment.payment_date.strftime('%Y-%m-%d'),
                payment.client.get_full_name(),
                payment.client.email,
                payment.amount,
                payment.currency,
                payment.get_payment_method_display(),
                payment.reference_id or '',
                payment.notes or '',
                payment.recorded_by.email if payment.recorded_by else '',
                payment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            ])
        
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="payments_export.csv"'
        return response
