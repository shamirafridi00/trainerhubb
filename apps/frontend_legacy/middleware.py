"""
Middleware for logging user interactions and requests.
"""
import logging
import json
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('user_interactions')


class UserInteractionLoggerMiddleware(MiddlewareMixin):
    """
    Middleware to log user interactions and page views.
    """
    
    def process_request(self, request):
        """Log incoming requests."""
        if request.user.is_authenticated:
            logger.info(
                f"User {request.user.email} - {request.method} {request.path}",
                extra={
                    'user': request.user.email,
                    'method': request.method,
                    'path': request.path,
                    'ip': self.get_client_ip(request),
                    'timestamp': timezone.now().isoformat(),
                }
            )
        return None
    
    def process_response(self, request, response):
        """Log responses."""
        if request.user.is_authenticated and response.status_code < 400:
            logger.info(
                f"Response - {request.method} {request.path} - {response.status_code}",
                extra={
                    'user': request.user.email,
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code,
                    'timestamp': timezone.now().isoformat(),
                }
            )
        return response
    
    def get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

