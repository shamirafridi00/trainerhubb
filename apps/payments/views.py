from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone
import json
import hmac
import hashlib
from datetime import datetime

from .models import Subscription, Payment
from .serializers import SubscriptionSerializer, PaymentSerializer, CreateSubscriptionSerializer
from .paddle_service import paddle_service
from apps.trainers.models import Trainer


class SubscriptionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing subscriptions."""
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get subscription for current trainer."""
        try:
            trainer = self.request.user.trainer_profile
            return Subscription.objects.filter(trainer=trainer).select_related('trainer')
        except Trainer.DoesNotExist:
            return Subscription.objects.none()
    
    def get_serializer_class(self):
        """Use different serializer for create action."""
        if self.action == 'create':
            return CreateSubscriptionSerializer
        return SubscriptionSerializer
    
    def perform_create(self, serializer):
        """Create subscription for current trainer."""
        trainer = self.request.user.trainer_profile
        serializer.save(trainer=trainer)
    
    @action(detail=False, methods=['post'], url_path='create-checkout')
    def create_checkout(self, request):
        """
        Create Paddle checkout link.
        
        POST /api/subscriptions/create-checkout/
        {
            "product_id": "pro_123",  // optional, uses default from settings
            "return_url": "https://example.com/success"
        }
        """
        product_id = request.data.get('product_id')
        return_url = request.data.get('return_url', 'https://yourdomain.com/subscription/success')
        
        try:
            trainer = request.user.trainer_profile
            checkout = paddle_service.create_checkout(
                trainer.id, product_id, return_url
            )
            
            if 'error' in checkout:
                return Response(
                    {'error': checkout['error']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(checkout)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel subscription.
        
        POST /api/subscriptions/{id}/cancel/
        """
        subscription = self.get_object()
        
        try:
            result = paddle_service.cancel_subscription(subscription.paddle_subscription_id)
            
            if 'error' in result:
                return Response(
                    {'error': result['error']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            subscription.status = 'cancelled'
            subscription.save()
            serializer = self.get_serializer(subscription)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """
        Pause subscription.
        
        POST /api/subscriptions/{id}/pause/
        """
        subscription = self.get_object()
        
        try:
            result = paddle_service.pause_subscription(subscription.paddle_subscription_id)
            
            if 'error' in result:
                return Response(
                    {'error': result['error']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            subscription.status = 'paused'
            subscription.save()
            serializer = self.get_serializer(subscription)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def resume(self, request, pk=None):
        """
        Resume paused subscription.
        
        POST /api/subscriptions/{id}/resume/
        """
        subscription = self.get_object()
        
        try:
            result = paddle_service.resume_subscription(subscription.paddle_subscription_id)
            
            if 'error' in result:
                return Response(
                    {'error': result['error']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            subscription.status = 'active'
            subscription.save()
            serializer = self.get_serializer(subscription)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], url_path='sync-from-paddle')
    def sync_from_paddle(self, request, pk=None):
        """
        Sync subscription data from Paddle.
        
        POST /api/subscriptions/{id}/sync-from-paddle/
        """
        subscription = self.get_object()
        
        try:
            updated_subscription = paddle_service.sync_subscription_from_paddle(
                subscription.paddle_subscription_id,
                subscription.trainer
            )
            serializer = self.get_serializer(updated_subscription)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing payments."""
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get payments for current trainer."""
        try:
            trainer = self.request.user.trainer_profile
            return Payment.objects.filter(
                subscription__trainer=trainer
            ).select_related('subscription', 'subscription__trainer').order_by('-created_at')
        except Trainer.DoesNotExist:
            return Payment.objects.none()


def verify_paddle_signature(payload, signature):
    """
    Verify Paddle webhook signature.
    
    Args:
        payload: Raw request body (bytes)
        signature: Signature from Paddle-Signature header
    
    Returns:
        bool: True if signature is valid
    """
    if not settings.PADDLE_WEBHOOK_SECRET:
        # If no secret configured, skip verification (development only)
        return True
    
    try:
        # Paddle uses HMAC SHA256
        expected_signature = hmac.new(
            settings.PADDLE_WEBHOOK_SECRET.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
    except Exception:
        return False


@csrf_exempt
def paddle_webhook(request):
    """
    Handle Paddle webhooks.
    
    POST /api/payments/webhooks/paddle/
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        # Get signature from header
        signature = request.headers.get('Paddle-Signature', '')
        
        # Get raw body for signature verification
        raw_body = request.body
        
        # Verify signature if webhook secret is configured
        if settings.PADDLE_WEBHOOK_SECRET:
            if not verify_paddle_signature(raw_body, signature):
                return JsonResponse({'error': 'Invalid signature'}, status=401)
        
        # Parse JSON payload
        data = json.loads(raw_body.decode('utf-8'))
        event_type = data.get('event_type') or data.get('type')
        
        # Handle different event types
        if event_type in ['subscription.created', 'subscription_created']:
            _handle_subscription_created(data)
        elif event_type in ['subscription.updated', 'subscription_updated']:
            _handle_subscription_updated(data)
        elif event_type in ['subscription.canceled', 'subscription.cancelled', 'subscription_canceled']:
            _handle_subscription_cancelled(data)
        elif event_type in ['transaction.completed', 'transaction_completed', 'transaction.paid']:
            _handle_transaction_completed(data)
        elif event_type in ['transaction.payment_failed', 'transaction_payment_failed']:
            _handle_transaction_failed(data)
        else:
            # Log unhandled event types
            print(f"Unhandled webhook event: {event_type}")
        
        return JsonResponse({'status': 'processed'})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def _handle_subscription_created(data):
    """Handle subscription.created webhook."""
    try:
        subscription_data = data.get('data', {})
        paddle_subscription_id = subscription_data.get('id')
        
        # Try to get trainer from custom_data or customer_id
        custom_data = subscription_data.get('custom_data', {})
        trainer_id = custom_data.get('trainer_id')
        
        if not trainer_id:
            # Try to extract from customer_id if it's in format trainer_123
            customer_id = subscription_data.get('customer_id', '')
            if customer_id.startswith('trainer_'):
                trainer_id = customer_id.replace('trainer_', '')
        
        if trainer_id:
            try:
                trainer = Trainer.objects.get(id=trainer_id)
                
                # Get status and next billing date
                status_map = {
                    'active': 'active',
                    'paused': 'paused',
                    'canceled': 'cancelled',
                    'cancelled': 'cancelled',
                    'expired': 'expired',
                }
                paddle_status = subscription_data.get('status', 'active')
                local_status = status_map.get(paddle_status.lower(), 'active')
                
                next_billing_date = None
                if subscription_data.get('next_billed_at'):
                    try:
                        next_billing_date = datetime.fromisoformat(
                            subscription_data['next_billed_at'].replace('Z', '+00:00')
                        ).date()
                    except (ValueError, AttributeError):
                        pass
                
                Subscription.objects.update_or_create(
                    trainer=trainer,
                    defaults={
                        'paddle_subscription_id': paddle_subscription_id,
                        'status': local_status,
                        'next_billing_date': next_billing_date,
                    }
                )
            except Trainer.DoesNotExist:
                print(f"Trainer not found for subscription: {paddle_subscription_id}")
    except Exception as e:
        print(f"Error handling subscription.created: {str(e)}")


def _handle_subscription_updated(data):
    """Handle subscription.updated webhook."""
    try:
        subscription_data = data.get('data', {})
        paddle_subscription_id = subscription_data.get('id')
        
        status_map = {
            'active': 'active',
            'paused': 'paused',
            'canceled': 'cancelled',
            'cancelled': 'cancelled',
            'expired': 'expired',
        }
        paddle_status = subscription_data.get('status', 'active')
        local_status = status_map.get(paddle_status.lower(), 'active')
        
        next_billing_date = None
        if subscription_data.get('next_billed_at'):
            try:
                next_billing_date = datetime.fromisoformat(
                    subscription_data['next_billed_at'].replace('Z', '+00:00')
                ).date()
            except (ValueError, AttributeError):
                pass
        
        try:
            subscription = Subscription.objects.get(
                paddle_subscription_id=paddle_subscription_id
            )
            subscription.status = local_status
            if next_billing_date:
                subscription.next_billing_date = next_billing_date
            subscription.save()
        except Subscription.DoesNotExist:
            # Try to create if doesn't exist (might have been missed)
            _handle_subscription_created(data)
    except Exception as e:
        print(f"Error handling subscription.updated: {str(e)}")


def _handle_subscription_cancelled(data):
    """Handle subscription.cancelled webhook."""
    try:
        subscription_data = data.get('data', {})
        paddle_subscription_id = subscription_data.get('id')
        
        try:
            subscription = Subscription.objects.get(
                paddle_subscription_id=paddle_subscription_id
            )
            subscription.status = 'cancelled'
            subscription.save()
        except Subscription.DoesNotExist:
            print(f"Subscription not found: {paddle_subscription_id}")
    except Exception as e:
        print(f"Error handling subscription.cancelled: {str(e)}")


def _handle_transaction_completed(data):
    """Handle transaction.completed webhook."""
    try:
        transaction_data = data.get('data', {})
        paddle_transaction_id = transaction_data.get('id')
        subscription_id = transaction_data.get('subscription_id')
        
        # Extract amount and currency
        amount = None
        currency = 'USD'
        
        # Try different possible locations for amount
        if 'details' in transaction_data:
            amount = transaction_data['details'].get('totals', {}).get('total')
            currency = transaction_data['details'].get('currency_code', 'USD')
        elif 'totals' in transaction_data:
            amount = transaction_data['totals'].get('total')
            currency = transaction_data.get('currency_code', 'USD')
        elif 'amount' in transaction_data:
            amount = transaction_data['amount']
            currency = transaction_data.get('currency_code', 'USD')
        
        if not amount or not subscription_id:
            print(f"Incomplete transaction data: {transaction_data}")
            return
        
        try:
            subscription = Subscription.objects.get(
                paddle_subscription_id=subscription_id
            )
            
            # Check if payment already exists
            payment, created = Payment.objects.get_or_create(
                paddle_transaction_id=paddle_transaction_id,
                defaults={
                    'subscription': subscription,
                    'amount': amount,
                    'currency': currency,
                    'status': 'completed',
                }
            )
            
            if not created:
                # Update existing payment
                payment.status = 'completed'
                payment.amount = amount
                payment.currency = currency
                payment.save()
            
            # Send payment receipt notification asynchronously
            from apps.notifications.tasks import send_payment_receipt
            send_payment_receipt.delay(payment.id)
            
        except Subscription.DoesNotExist:
            print(f"Subscription not found for transaction: {paddle_transaction_id}")
    except Exception as e:
        print(f"Error handling transaction.completed: {str(e)}")


def _handle_transaction_failed(data):
    """Handle transaction.payment_failed webhook."""
    try:
        transaction_data = data.get('data', {})
        paddle_transaction_id = transaction_data.get('id')
        subscription_id = transaction_data.get('subscription_id')
        
        # Extract amount
        amount = None
        if 'details' in transaction_data:
            amount = transaction_data['details'].get('totals', {}).get('total')
        elif 'totals' in transaction_data:
            amount = transaction_data['totals'].get('total')
        elif 'amount' in transaction_data:
            amount = transaction_data['amount']
        
        if not subscription_id:
            print(f"No subscription_id in failed transaction: {transaction_data}")
            return
        
        try:
            subscription = Subscription.objects.get(
                paddle_subscription_id=subscription_id
            )
            
            Payment.objects.update_or_create(
                paddle_transaction_id=paddle_transaction_id,
                defaults={
                    'subscription': subscription,
                    'amount': amount or 0,
                    'currency': transaction_data.get('currency_code', 'USD'),
                    'status': 'failed',
                }
            )
        except Subscription.DoesNotExist:
            print(f"Subscription not found for failed transaction: {paddle_transaction_id}")
    except Exception as e:
        print(f"Error handling transaction.failed: {str(e)}")

