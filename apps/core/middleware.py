"""
Core middleware for request logging, performance monitoring, and security.
"""
import time
import logging
import json
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log HTTP requests with performance metrics.
    """

    def process_request(self, request):
        """Store request start time."""
        request.start_time = time.time()

    def process_response(self, request, response):
        """Log request details and performance metrics."""
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
        else:
            duration = 0

        # Create structured log entry
        log_data = {
            'method': request.method,
            'path': request.path,
            'query_string': request.GET.urlencode() if request.GET else '',
            'status_code': response.status_code,
            'duration_ms': round(duration * 1000, 2),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'remote_addr': self.get_client_ip(request),
            'content_length': len(response.content) if hasattr(response, 'content') else 0,
        }

        # Add user info if authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            log_data['user_id'] = request.user.id
            log_data['username'] = request.user.username

        # Add trainer info if available
        if hasattr(request, 'trainer') and request.trainer:
            log_data['trainer_id'] = request.trainer.id
            log_data['trainer_slug'] = getattr(request.trainer.user, 'username', None)

        # Log based on status code
        if response.status_code >= 500:
            logger.error("Request failed", extra=log_data)
        elif response.status_code >= 400:
            logger.warning("Request error", extra=log_data)
        elif duration > 5.0:  # Slow requests (>5 seconds)
            logger.warning("Slow request", extra=log_data)
        else:
            logger.info("Request completed", extra=log_data)

        return response

    def get_client_ip(self, request):
        """Get the client's IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class HealthCheckMiddleware(MiddlewareMixin):
    """
    Middleware to add timestamp to health check responses.
    """

    def process_response(self, request, response):
        """Add timestamp to health check responses."""
        if request.path in ['/health/', '/api/health/', '/readiness/', '/liveness/']:
            import datetime
            response_data = json.loads(response.content.decode('utf-8'))
            response_data['timestamp'] = datetime.datetime.utcnow().isoformat() + 'Z'
            response.content = json.dumps(response_data).encode('utf-8')
            response['Content-Type'] = 'application/json'

        return response


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add security headers to all responses.
    """

    def process_response(self, request, response):
        """Add security headers."""
        # Only add headers to HTML responses and API responses
        content_type = response.get('Content-Type', '').lower()
        if 'text/html' in content_type or 'application/json' in content_type or not content_type:
            # Security headers
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-Frame-Options'] = 'DENY'
            response['X-XSS-Protection'] = '1; mode=block'

            # HTTPS only headers (in production)
            if not getattr(settings, 'DEBUG', True):
                response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

        return response


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """
    Middleware to monitor application performance and resource usage.
    """

    def process_request(self, request):
        """Initialize performance monitoring."""
        request.performance_data = {
            'db_queries': 0,
            'db_time': 0.0,
            'cache_hits': 0,
            'cache_misses': 0,
        }

    def process_response(self, request, response):
        """Log performance metrics for monitoring."""
        if hasattr(request, 'performance_data'):
            perf_data = request.performance_data

            # Log high resource usage requests
            if perf_data['db_queries'] > 50 or perf_data['db_time'] > 2.0:
                logger.warning("High resource usage detected", extra={
                    'path': request.path,
                    'method': request.method,
                    'db_queries': perf_data['db_queries'],
                    'db_time': perf_data['db_time'],
                    'cache_hits': perf_data['cache_hits'],
                    'cache_misses': perf_data['cache_misses'],
                })

        return response
