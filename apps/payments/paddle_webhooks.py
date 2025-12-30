"""
Paddle Webhook Handler
Processes Paddle webhook events for subscription management.
"""
import hmac
import hashlib
import json
import logging
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from django.db import transaction

from .models import Subscription, Payment, WebhookEvent
from apps.trainers.models import Trainer

logger = logging.getLogger(__name__)


class PaddleWebhookHandler:
    """
    Handles Paddle webhook events.
    
    Supported Events:
    - subscription.created
    - subscription.updated
    - subscription.canceled
    - subscription.past_due
    - subscription.paused
    - subscription.resumed
    - transaction.completed
    - transaction.payment_failed
    """
    
    def __init__(self, payload, signature=None):
        self.payload = payload
        self.signature = signature
        self.event_type = payload.get('event_type')
        self.event_id = payload.get('event_id')
        self.data = payload.get('data', {})
    
    def verify_signature(self):
        """
        Verify Paddle webhook signature.
        
        Note: In production, implement proper signature verification
        using Paddle's public key or webhook secret.
        """
        # TODO: Implement signature verification
        # For now, return True for development
        return True
    
    def process(self):
        """
        Process the webhook event.
        Returns (success: bool, message: str)
        """
        # Log the event
        webhook_event = WebhookEvent.objects.create(
            event_id=self.event_id,
            event_type=self.event_type,
            payload=self.payload,
            processed=False
        )
        
        try:
            # Verify signature
            if not self.verify_signature():
                error_msg = "Invalid webhook signature"
                webhook_event.error_message = error_msg
                webhook_event.save()
                return False, error_msg
            
            # Route to appropriate handler
            handler_map = {
                'subscription.created': self.handle_subscription_created,
                'subscription.updated': self.handle_subscription_updated,
                'subscription.canceled': self.handle_subscription_canceled,
                'subscription.past_due': self.handle_subscription_past_due,
                'subscription.paused': self.handle_subscription_paused,
                'subscription.resumed': self.handle_subscription_resumed,
                'transaction.completed': self.handle_transaction_completed,
                'transaction.payment_failed': self.handle_transaction_failed,
            }
            
            handler = handler_map.get(self.event_type)
            if not handler:
                error_msg = f"Unhandled event type: {self.event_type}"
                logger.warning(error_msg)
                webhook_event.error_message = error_msg
                webhook_event.save()
                return False, error_msg
            
            # Execute handler
            with transaction.atomic():
                result = handler()
            
            # Mark as processed
            webhook_event.processed = True
            webhook_event.processed_at = timezone.now()
            webhook_event.save()
            
            return True, f"Successfully processed {self.event_type}"
            
        except Exception as e:
            error_msg = f"Error processing webhook: {str(e)}"
            logger.error(error_msg, exc_info=True)
            webhook_event.error_message = error_msg
            webhook_event.save()
            return False, error_msg
    
    def get_or_create_trainer(self, customer_id, customer_email=None):
        """
        Get or create trainer from Paddle customer ID.
        """
        # Try to find trainer by paddle_customer_id
        try:
            trainer = Trainer.objects.get(paddle_customer_id=customer_id)
            return trainer
        except Trainer.DoesNotExist:
            pass
        
        # Try to find by email if provided
        if customer_email:
            try:
                trainer = Trainer.objects.get(user__email=customer_email)
                trainer.paddle_customer_id = customer_id
                trainer.save()
                return trainer
            except Trainer.DoesNotExist:
                pass
        
        # If not found, log error
        logger.error(f"Trainer not found for Paddle customer {customer_id}")
        raise ValueError(f"Trainer not found for customer {customer_id}")
    
    def handle_subscription_created(self):
        """Handle subscription.created event."""
        subscription_id = self.data.get('id')
        customer_id = self.data.get('customer_id')
        status = self.data.get('status', 'active')
        
        # Get plan from items
        items = self.data.get('items', [])
        plan = 'free'  # default
        if items:
            price_id = items[0].get('price', {}).get('id', '')
            # Map Paddle price ID to plan
            # TODO: Configure these in settings
            if 'pro' in price_id.lower():
                plan = 'pro'
            elif 'business' in price_id.lower():
                plan = 'business'
        
        # Get trainer
        trainer = self.get_or_create_trainer(customer_id)
        
        # Create or update subscription
        subscription, created = Subscription.objects.update_or_create(
            paddle_subscription_id=subscription_id,
            defaults={
                'trainer': trainer,
                'paddle_customer_id': customer_id,
                'plan': plan,
                'status': status,
                'current_period_start': self.parse_datetime(self.data.get('current_billing_period', {}).get('starts_at')),
                'current_period_end': self.parse_datetime(self.data.get('current_billing_period', {}).get('ends_at')),
                'cancel_at_period_end': self.data.get('scheduled_change') is not None,
            }
        )
        
        logger.info(f"{'Created' if created else 'Updated'} subscription {subscription_id} for trainer {trainer.business_name}")
        return subscription
    
    def handle_subscription_updated(self):
        """Handle subscription.updated event."""
        subscription_id = self.data.get('id')
        status = self.data.get('status')
        
        try:
            subscription = Subscription.objects.get(paddle_subscription_id=subscription_id)
            subscription.status = status
            subscription.current_period_start = self.parse_datetime(self.data.get('current_billing_period', {}).get('starts_at'))
            subscription.current_period_end = self.parse_datetime(self.data.get('current_billing_period', {}).get('ends_at'))
            subscription.cancel_at_period_end = self.data.get('scheduled_change') is not None
            subscription.save()
            
            logger.info(f"Updated subscription {subscription_id} to status {status}")
            return subscription
        except Subscription.DoesNotExist:
            logger.error(f"Subscription {subscription_id} not found")
            raise
    
    def handle_subscription_canceled(self):
        """Handle subscription.canceled event."""
        subscription_id = self.data.get('id')
        
        try:
            subscription = Subscription.objects.get(paddle_subscription_id=subscription_id)
            subscription.status = 'cancelled'
            subscription.cancelled_at = timezone.now()
            subscription.save()
            
            logger.info(f"Cancelled subscription {subscription_id}")
            return subscription
        except Subscription.DoesNotExist:
            logger.error(f"Subscription {subscription_id} not found")
            raise
    
    def handle_subscription_past_due(self):
        """Handle subscription.past_due event."""
        subscription_id = self.data.get('id')
        
        try:
            subscription = Subscription.objects.get(paddle_subscription_id=subscription_id)
            subscription.status = 'past_due'
            subscription.save()
            
            logger.warning(f"Subscription {subscription_id} is past due")
            return subscription
        except Subscription.DoesNotExist:
            logger.error(f"Subscription {subscription_id} not found")
            raise
    
    def handle_subscription_paused(self):
        """Handle subscription.paused event."""
        subscription_id = self.data.get('id')
        
        try:
            subscription = Subscription.objects.get(paddle_subscription_id=subscription_id)
            subscription.status = 'paused'
            subscription.save()
            
            logger.info(f"Paused subscription {subscription_id}")
            return subscription
        except Subscription.DoesNotExist:
            logger.error(f"Subscription {subscription_id} not found")
            raise
    
    def handle_subscription_resumed(self):
        """Handle subscription.resumed event."""
        subscription_id = self.data.get('id')
        
        try:
            subscription = Subscription.objects.get(paddle_subscription_id=subscription_id)
            subscription.status = 'active'
            subscription.save()
            
            logger.info(f"Resumed subscription {subscription_id}")
            return subscription
        except Subscription.DoesNotExist:
            logger.error(f"Subscription {subscription_id} not found")
            raise
    
    def handle_transaction_completed(self):
        """Handle transaction.completed event."""
        transaction_id = self.data.get('id')
        subscription_id = self.data.get('subscription_id')
        customer_id = self.data.get('customer_id')
        
        # Get subscription if exists
        subscription = None
        if subscription_id:
            try:
                subscription = Subscription.objects.get(paddle_subscription_id=subscription_id)
            except Subscription.DoesNotExist:
                logger.warning(f"Subscription {subscription_id} not found for transaction {transaction_id}")
        
        # Get trainer
        trainer = self.get_or_create_trainer(customer_id)
        
        # Get amount details
        details = self.data.get('details', {})
        totals = details.get('totals', {})
        amount = float(totals.get('total', 0)) / 100  # Convert from cents
        currency = totals.get('currency_code', 'USD')
        
        # Create payment record
        payment, created = Payment.objects.update_or_create(
            paddle_transaction_id=transaction_id,
            defaults={
                'subscription': subscription,
                'trainer': trainer,
                'amount': amount,
                'currency': currency,
                'paddle_invoice_id': self.data.get('invoice_id'),
                'status': 'completed',
                'payment_method': details.get('payment_method', {}).get('type'),
                'receipt_url': self.data.get('receipt_url'),
            }
        )
        
        logger.info(f"{'Created' if created else 'Updated'} payment {transaction_id} for ${amount}")
        return payment
    
    def handle_transaction_failed(self):
        """Handle transaction.payment_failed event."""
        transaction_id = self.data.get('id')
        subscription_id = self.data.get('subscription_id')
        customer_id = self.data.get('customer_id')
        
        # Get subscription if exists
        subscription = None
        if subscription_id:
            try:
                subscription = Subscription.objects.get(paddle_subscription_id=subscription_id)
                # Update subscription status
                subscription.status = 'past_due'
                subscription.save()
            except Subscription.DoesNotExist:
                logger.warning(f"Subscription {subscription_id} not found for failed transaction {transaction_id}")
        
        # Get trainer
        trainer = self.get_or_create_trainer(customer_id)
        
        # Get amount details
        details = self.data.get('details', {})
        totals = details.get('totals', {})
        amount = float(totals.get('total', 0)) / 100
        currency = totals.get('currency_code', 'USD')
        
        # Create failed payment record
        payment, created = Payment.objects.update_or_create(
            paddle_transaction_id=transaction_id,
            defaults={
                'subscription': subscription,
                'trainer': trainer,
                'amount': amount,
                'currency': currency,
                'status': 'failed',
            }
        )
        
        logger.warning(f"Payment failed for transaction {transaction_id}")
        return payment
    
    @staticmethod
    def parse_datetime(datetime_str):
        """Parse ISO datetime string to Django datetime."""
        if not datetime_str:
            return None
        try:
            return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return None

