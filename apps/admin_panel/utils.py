"""
Admin Panel Utility Functions
"""


def log_admin_action(admin_user, action, target_trainer=None, details=None, request=None):
    """
    Log an admin action for audit trail.
    
    Args:
        admin_user: User performing the action
        action: Action type (string from ACTION_CHOICES)
        target_trainer: Trainer being acted upon (optional)
        details: Additional details as dict (optional)
        request: HTTP request object (optional, for IP/user agent)
    """
    from .models import AdminActionLog
    
    log_data = {
        'admin_user': admin_user,
        'action': action,
        'target_trainer': target_trainer,
        'details': details or {},
    }
    
    if request:
        log_data['ip_address'] = get_client_ip(request)
        log_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')[:500]
    
    return AdminActionLog.objects.create(**log_data)


def get_client_ip(request):
    """
    Extract client IP address from request.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

