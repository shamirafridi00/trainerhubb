"""
Subscription Middleware
Checks subscription status and feature access on API requests.
"""
from django.http import JsonResponse
from .models import Subscription


class SubscriptionMiddleware:
    """
    Middleware that checks subscription status for trainer requests.
    Blocks access if subscription is inactive (past_due, cancelled).
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Exempt paths that don't require active subscription
        self.exempt_paths = [
            '/api/users/',
            '/api/payments/subscriptions/',
            '/api/payments/paddle-webhook/',
            '/api/admin/',
            '/admin/',
            '/static/',
            '/media/',
        ]
    
    def __call__(self, request):
        # Check if path is exempt
        if any(request.path.startswith(path) for path in self.exempt_paths):
            return self.get_response(request)
        
        # Only check for authenticated users
        if request.user.is_authenticated:
            # Skip for superusers
            if request.user.is_superuser:
                return self.get_response(request)
            
            # Check if user is a trainer
            if hasattr(request.user, 'trainer_profile'):
                trainer = request.user.trainer_profile
                
                try:
                    subscription = Subscription.objects.get(trainer=trainer)
                    
                    # Check if subscription is inactive
                    if subscription.status in ['past_due', 'cancelled'] and subscription.cancel_at_period_end:
                        return JsonResponse({
                            'error': 'Subscription inactive',
                            'detail': 'Your subscription is inactive. Please update your payment method.',
                            'status': subscription.status
                        }, status=403)
                    
                except Subscription.DoesNotExist:
                    # No subscription = free tier, allow access
                    pass
        
        response = self.get_response(request)
        return response

