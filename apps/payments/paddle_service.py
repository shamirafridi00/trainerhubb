"""
Paddle API Service for payment processing.
Handles subscription management, checkout creation, and webhook processing.
"""
import requests
from django.conf import settings
from django.utils import timezone
from datetime import datetime
from .models import Subscription, Payment


class PaddleService:
    """Service for Paddle API interactions."""
    
    BASE_URL = 'https://api.paddle.com'
    
    def __init__(self):
        self.api_key = settings.PADDLE_API_KEY
        self.vendor_id = settings.PADDLE_VENDOR_ID
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def create_checkout(self, trainer_id, product_id=None, return_url=None):
        """
        Create Paddle checkout link for subscription.
        
        Args:
            trainer_id: ID of the trainer subscribing
            product_id: Paddle product ID (defaults to settings.PADDLE_PRODUCT_ID)
            return_url: URL to redirect after successful payment
        
        Returns:
            dict: Checkout response with checkout URL
        """
        if not product_id:
            product_id = settings.PADDLE_PRODUCT_ID
        
        url = f'{self.BASE_URL}/transactions'
        
        payload = {
            'items': [
                {
                    'price_id': product_id,
                    'quantity': 1
                }
            ],
            'customer_id': f'trainer_{trainer_id}',
            'custom_data': {
                'trainer_id': str(trainer_id)
            }
        }
        
        if return_url:
            payload['checkout'] = {
                'url': return_url
            }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e), 'status_code': getattr(e.response, 'status_code', None)}
    
    def get_subscription(self, subscription_id):
        """
        Get subscription details from Paddle.
        
        Args:
            subscription_id: Paddle subscription ID
        
        Returns:
            dict: Subscription details
        """
        url = f'{self.BASE_URL}/subscriptions/{subscription_id}'
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e), 'status_code': getattr(e.response, 'status_code', None)}
    
    def cancel_subscription(self, subscription_id):
        """
        Cancel subscription in Paddle.
        
        Args:
            subscription_id: Paddle subscription ID
        
        Returns:
            dict: Cancellation response
        """
        url = f'{self.BASE_URL}/subscriptions/{subscription_id}/cancel'
        
        try:
            response = requests.post(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e), 'status_code': getattr(e.response, 'status_code', None)}
    
    def pause_subscription(self, subscription_id):
        """
        Pause subscription in Paddle.
        
        Args:
            subscription_id: Paddle subscription ID
        
        Returns:
            dict: Pause response
        """
        url = f'{self.BASE_URL}/subscriptions/{subscription_id}/pause'
        
        try:
            response = requests.post(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e), 'status_code': getattr(e.response, 'status_code', None)}
    
    def resume_subscription(self, subscription_id):
        """
        Resume paused subscription in Paddle.
        
        Args:
            subscription_id: Paddle subscription ID
        
        Returns:
            dict: Resume response
        """
        url = f'{self.BASE_URL}/subscriptions/{subscription_id}/resume'
        
        try:
            response = requests.post(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e), 'status_code': getattr(e.response, 'status_code', None)}
    
    def get_transaction(self, transaction_id):
        """
        Get transaction details from Paddle.
        
        Args:
            transaction_id: Paddle transaction ID
        
        Returns:
            dict: Transaction details
        """
        url = f'{self.BASE_URL}/transactions/{transaction_id}'
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e), 'status_code': getattr(e.response, 'status_code', None)}
    
    def sync_subscription_from_paddle(self, paddle_subscription_id, trainer):
        """
        Sync subscription data from Paddle and create/update local record.
        
        Args:
            paddle_subscription_id: Paddle subscription ID
            trainer: Trainer instance
        
        Returns:
            Subscription: Created or updated subscription
        """
        paddle_data = self.get_subscription(paddle_subscription_id)
        
        if 'error' in paddle_data:
            raise Exception(f"Failed to fetch subscription: {paddle_data['error']}")
        
        # Map Paddle status to our status
        status_map = {
            'active': 'active',
            'paused': 'paused',
            'canceled': 'cancelled',
            'cancelled': 'cancelled',
            'expired': 'expired',
            'past_due': 'active',  # Treat past_due as active for now
        }
        
        paddle_status = paddle_data.get('status', 'active')
        local_status = status_map.get(paddle_status.lower(), 'active')
        
        # Parse next billing date
        next_billing_date = None
        if paddle_data.get('next_billed_at'):
            try:
                next_billing_date = datetime.fromisoformat(
                    paddle_data['next_billed_at'].replace('Z', '+00:00')
                ).date()
            except (ValueError, AttributeError):
                pass
        
        subscription, created = Subscription.objects.update_or_create(
            trainer=trainer,
            defaults={
                'paddle_subscription_id': paddle_subscription_id,
                'status': local_status,
                'next_billing_date': next_billing_date,
            }
        )
        
        return subscription


# Create singleton instance
paddle_service = PaddleService()

