"""
Subscription-based Permission Classes
Enforce feature access based on subscription tier.
"""
from rest_framework import permissions
from .models import Subscription


class RequiresPlan(permissions.BasePermission):
    """
    Permission class that checks if user's subscription plan allows access.
    
    Usage:
        @permission_classes([RequiresPlan])
        @required_plan('pro')  # or use self.required_plans in the view
        def my_view(request):
            ...
    """
    
    def __init__(self, required_plan='free'):
        self.required_plan = required_plan
        super().__init__()
    
    def has_permission(self, request, view):
        """Check if user has required plan."""
        # Allow if user is superuser
        if request.user.is_superuser:
            return True
        
        # Check if user is a trainer
        if not hasattr(request.user, 'trainer_profile'):
            return False
        
        trainer = request.user.trainer_profile
        
        # Get subscription
        try:
            subscription = Subscription.objects.get(trainer=trainer)
        except Subscription.DoesNotExist:
            # No subscription = free tier
            subscription = Subscription(plan='free')
        
        # Check if subscription is active
        if not subscription.is_active():
            return False
        
        # Get required plan from view if available
        required_plan = getattr(view, 'required_plan', self.required_plan)
        
        # Check plan hierarchy: business > pro > free
        plan_hierarchy = {
            'free': 0,
            'pro': 1,
            'business': 2,
        }
        
        current_level = plan_hierarchy.get(subscription.plan, 0)
        required_level = plan_hierarchy.get(required_plan, 0)
        
        return current_level >= required_level


class RequiresActiveSubscription(permissions.BasePermission):
    """
    Permission class that checks if user has an active subscription.
    """
    
    def has_permission(self, request, view):
        """Check if user has active subscription."""
        # Allow if user is superuser
        if request.user.is_superuser:
            return True
        
        # Check if user is a trainer
        if not hasattr(request.user, 'trainer_profile'):
            return False
        
        trainer = request.user.trainer_profile
        
        # Get subscription
        try:
            subscription = Subscription.objects.get(trainer=trainer)
            return subscription.is_active()
        except Subscription.DoesNotExist:
            # Free tier is always "active"
            return True


class RequiresFeature(permissions.BasePermission):
    """
    Permission class that checks if subscription allows specific feature.
    
    Usage:
        @permission_classes([RequiresFeature])
        @required_feature('custom_domain')
        def my_view(request):
            ...
    """
    
    def __init__(self, feature=None):
        self.feature = feature
        super().__init__()
    
    def has_permission(self, request, view):
        """Check if subscription allows feature."""
        # Allow if user is superuser
        if request.user.is_superuser:
            return True
        
        # Check if user is a trainer
        if not hasattr(request.user, 'trainer_profile'):
            return False
        
        trainer = request.user.trainer_profile
        
        # Get subscription
        try:
            subscription = Subscription.objects.get(trainer=trainer)
        except Subscription.DoesNotExist:
            subscription = Subscription(plan='free')
        
        # Check if subscription is active
        if not subscription.is_active():
            return False
        
        # Get feature from view if available
        feature = getattr(view, 'required_feature', self.feature)
        
        if not feature:
            return True
        
        return subscription.can_access_feature(feature)


def check_usage_limit(trainer, resource_type):
    """
    Check if trainer has reached usage limit for a resource.
    
    Args:
        trainer: Trainer instance
        resource_type: 'clients', 'pages', 'workflows'
    
    Returns:
        tuple: (can_create: bool, current_count: int, limit: int)
    """
    from apps.clients.models import Client
    
    # Get subscription
    try:
        subscription = Subscription.objects.get(trainer=trainer)
    except Subscription.DoesNotExist:
        subscription = Subscription(plan='free')
    
    # Get current count
    if resource_type == 'clients':
        current_count = Client.objects.filter(trainer=trainer, is_active=True).count()
        limit = subscription.can_access_feature('max_clients')
    elif resource_type == 'pages':
        from apps.pages.models import Page
        current_count = Page.objects.filter(trainer=trainer).count()
        limit = subscription.can_access_feature('max_pages')
    elif resource_type == 'workflows':
        from apps.workflows.models import Workflow
        current_count = Workflow.objects.filter(trainer=trainer).count()
        limit = subscription.can_access_feature('workflows')
        if isinstance(limit, bool):
            limit = 3 if subscription.plan == 'pro' else (-1 if subscription.plan == 'business' else 0)
    else:
        return False, 0, 0
    
    # -1 means unlimited
    if limit == -1:
        return True, current_count, limit
    
    # Check if limit reached
    can_create = current_count < limit
    return can_create, current_count, limit

