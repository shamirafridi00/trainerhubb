"""
Core application views for health checks and system monitoring.
"""
import psycopg2
import redis
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.db import connection
import logging

logger = logging.getLogger(__name__)


@never_cache
@require_http_methods(["GET"])
def health_check(request):
    """
    Comprehensive health check endpoint for load balancers and monitoring systems.

    Returns JSON with system status and component health.
    """
    health_status = {
        'status': 'healthy',
        'timestamp': None,  # Will be set by middleware
        'version': getattr(settings, 'RELEASE_VERSION', 'unknown'),
        'environment': getattr(settings, 'ENVIRONMENT', 'development'),
        'checks': {}
    }

    # Database check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            health_status['checks']['database'] = {'status': 'healthy', 'message': 'OK'}
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status['checks']['database'] = {'status': 'unhealthy', 'message': str(e)}
        health_status['status'] = 'unhealthy'

    # Redis check (if configured)
    redis_url = getattr(settings, 'REDIS_URL', None)
    if redis_url:
        try:
            # Parse Redis URL
            if redis_url.startswith('redis://'):
                # Simple parsing for redis://host:port/db format
                redis_parts = redis_url.replace('redis://', '').split('/')
                host_port = redis_parts[0].split(':')
                host = host_port[0]
                port = int(host_port[1]) if len(host_port) > 1 else 6379
                db = int(redis_parts[1]) if len(redis_parts) > 1 else 0

                r = redis.Redis(host=host, port=port, db=db, socket_timeout=5)
                r.ping()
                health_status['checks']['redis'] = {'status': 'healthy', 'message': 'OK'}
            else:
                health_status['checks']['redis'] = {'status': 'unknown', 'message': 'Redis URL format not supported'}
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            health_status['checks']['redis'] = {'status': 'unhealthy', 'message': str(e)}
            health_status['status'] = 'unhealthy'
    else:
        health_status['checks']['redis'] = {'status': 'not_configured', 'message': 'Redis not configured'}

    # External services check (optional)
    external_checks = []

    # Check SendGrid (if configured)
    sendgrid_key = getattr(settings, 'SENDGRID_API_KEY', None)
    if sendgrid_key:
        # Basic check - just verify key is configured
        health_status['checks']['sendgrid'] = {'status': 'configured', 'message': 'API key configured'}
    else:
        health_status['checks']['sendgrid'] = {'status': 'not_configured', 'message': 'API key not set'}

    # Check Twilio (if configured)
    twilio_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
    if twilio_sid:
        health_status['checks']['twilio'] = {'status': 'configured', 'message': 'Credentials configured'}
    else:
        health_status['checks']['twilio'] = {'status': 'not_configured', 'message': 'Credentials not set'}

    # Check Paddle (if configured)
    paddle_key = getattr(settings, 'PADDLE_API_KEY', None)
    if paddle_key:
        health_status['checks']['paddle'] = {'status': 'configured', 'message': 'API key configured'}
    else:
        health_status['checks']['paddle'] = {'status': 'not_configured', 'message': 'API key not set'}

    # Response based on overall health
    status_code = 200 if health_status['status'] == 'healthy' else 503

    return JsonResponse(health_status, status=status_code)


@never_cache
@require_http_methods(["GET"])
def readiness_check(request):
    """
    Readiness check for Kubernetes/Docker deployments.
    Checks if the application is ready to serve traffic.
    """
    # For now, same as health check
    # In the future, this could check additional readiness criteria
    return health_check(request)


@never_cache
@require_http_methods(["GET"])
def liveness_check(request):
    """
    Liveness check for container orchestration.
    Simple check to see if the application is running.
    """
    return JsonResponse({'status': 'alive', 'timestamp': None})


@require_http_methods(["GET"])
def system_info(request):
    """
    System information endpoint for debugging and monitoring.
    Only available in DEBUG mode or with proper authentication.
    """
    if not getattr(settings, 'DEBUG', False):
        # In production, require authentication or special header
        auth_header = request.headers.get('X-Monitoring-Key')
        expected_key = getattr(settings, 'MONITORING_KEY', None)
        if not auth_header or auth_header != expected_key:
            return JsonResponse({'error': 'Unauthorized'}, status=401)

    info = {
        'version': getattr(settings, 'RELEASE_VERSION', 'unknown'),
        'environment': getattr(settings, 'ENVIRONMENT', 'development'),
        'debug': getattr(settings, 'DEBUG', False),
        'database_engine': settings.DATABASES['default']['ENGINE'].split('.')[-1],
        'cache_backend': settings.CACHES['default']['BACKEND'].split('.')[-1],
        'installed_apps': settings.INSTALLED_APPS,
        'middleware': [m.split('.')[-1] for m in settings.MIDDLEWARE],
    }

    return JsonResponse(info)
