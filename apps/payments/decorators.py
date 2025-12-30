"""
Subscription-based decorators for views and viewsets.
"""
from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from .permissions import check_usage_limit


def check_resource_limit(resource_type):
    """
    Decorator to check usage limits before creating resources.
    
    Usage:
        @check_resource_limit('clients')
        def create(self, request, *args, **kwargs):
            ...
    
    Args:
        resource_type: 'clients', 'pages', or 'workflows'
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            # Check if user is a trainer
            if not hasattr(request.user, 'trainer_profile'):
                return Response(
                    {'error': 'User is not a trainer'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            trainer = request.user.trainer_profile
            
            # Check usage limit
            can_create, current_count, limit = check_usage_limit(trainer, resource_type)
            
            if not can_create:
                return Response({
                    'error': 'Usage limit reached',
                    'detail': f'You have reached your limit of {limit} {resource_type}. Upgrade your plan to add more.',
                    'current_count': current_count,
                    'limit': limit,
                    'resource_type': resource_type
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Proceed with the original function
            return func(self, request, *args, **kwargs)
        
        return wrapper
    return decorator


def require_plan(required_plan):
    """
    Decorator to require specific plan for view access.
    
    Usage:
        @require_plan('pro')
        def my_view(self, request, *args, **kwargs):
            ...
    
    Args:
        required_plan: 'pro' or 'business'
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            # Check if user is a trainer
            if not hasattr(request.user, 'trainer_profile'):
                return Response(
                    {'error': 'User is not a trainer'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            from .models import Subscription
            trainer = request.user.trainer_profile
            
            # Get subscription
            try:
                subscription = Subscription.objects.get(trainer=trainer)
            except Subscription.DoesNotExist:
                subscription = Subscription(plan='free')
            
            # Check plan hierarchy
            plan_hierarchy = {
                'free': 0,
                'pro': 1,
                'business': 2,
            }
            
            current_level = plan_hierarchy.get(subscription.plan, 0)
            required_level = plan_hierarchy.get(required_plan, 0)
            
            if current_level < required_level:
                return Response({
                    'error': 'Plan upgrade required',
                    'detail': f'This feature requires {required_plan.capitalize()} plan or higher.',
                    'current_plan': subscription.plan,
                    'required_plan': required_plan
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Proceed with the original function
            return func(self, request, *args, **kwargs)
        
        return wrapper
    return decorator


def require_feature(feature_name):
    """
    Decorator to require specific feature access.
    
    Usage:
        @require_feature('custom_domain')
        def my_view(self, request, *args, **kwargs):
            ...
    
    Args:
        feature_name: Feature key from subscription.can_access_feature()
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            # Check if user is a trainer
            if not hasattr(request.user, 'trainer_profile'):
                return Response(
                    {'error': 'User is not a trainer'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            from .models import Subscription
            trainer = request.user.trainer_profile
            
            # Get subscription
            try:
                subscription = Subscription.objects.get(trainer=trainer)
            except Subscription.DoesNotExist:
                subscription = Subscription(plan='free')
            
            # Check feature access
            if not subscription.can_access_feature(feature_name):
                return Response({
                    'error': 'Feature not available',
                    'detail': f'Your current plan does not include access to {feature_name}.',
                    'feature': feature_name,
                    'current_plan': subscription.plan
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Proceed with the original function
            return func(self, request, *args, **kwargs)
        
        return wrapper
    return decorator

