"""
Health check endpoints and monitoring utilities
"""
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from django.conf import settings
import time


def health_check(request):
    """
    Basic health check endpoint.
    Returns 200 if the service is up.
    
    GET /health/
    """
    return JsonResponse({
        'status': 'healthy',
        'service': 'TrainerHub API',
        'timestamp': time.time()
    })


def readiness_check(request):
    """
    Readiness check - verifies dependencies are ready.
    Checks database, cache, and other critical services.
    
    GET /ready/
    """
    checks = {}
    is_ready = True
    
    # Check database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        checks['database'] = {'status': 'healthy', 'message': 'Connected'}
    except Exception as e:
        checks['database'] = {'status': 'unhealthy', 'message': str(e)}
        is_ready = False
    
    # Check cache (Redis)
    try:
        cache.set('health_check', 'ok', 10)
        value = cache.get('health_check')
        if value == 'ok':
            checks['cache'] = {'status': 'healthy', 'message': 'Connected'}
        else:
            checks['cache'] = {'status': 'unhealthy', 'message': 'Cache read/write failed'}
            is_ready = False
    except Exception as e:
        checks['cache'] = {'status': 'unhealthy', 'message': str(e)}
        is_ready = False
    
    # Check SendGrid (email)
    sendgrid_key = getattr(settings, 'SENDGRID_API_KEY', None)
    if sendgrid_key:
        checks['email'] = {'status': 'configured', 'message': 'SendGrid API key present'}
    else:
        checks['email'] = {'status': 'not_configured', 'message': 'SendGrid API key missing'}
    
    # Check Twilio (SMS)
    twilio_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
    if twilio_sid:
        checks['sms'] = {'status': 'configured', 'message': 'Twilio credentials present'}
    else:
        checks['sms'] = {'status': 'not_configured', 'message': 'Twilio credentials missing'}
    
    status_code = 200 if is_ready else 503
    
    return JsonResponse({
        'status': 'ready' if is_ready else 'not_ready',
        'checks': checks,
        'timestamp': time.time()
    }, status=status_code)


def liveness_check(request):
    """
    Liveness check - verifies the service is alive.
    Should return 200 as long as the process is running.
    
    GET /live/
    """
    return JsonResponse({
        'status': 'alive',
        'timestamp': time.time()
    })


def metrics(request):
    """
    Basic metrics endpoint.
    Returns simple application metrics.
    
    GET /metrics/
    """
    from django.contrib.auth import get_user_model
    from apps.trainers.models import Trainer
    from apps.bookings.models import Booking
    from apps.clients.models import Client
    
    User = get_user_model()
    
    try:
        metrics_data = {
            'users': {
                'total': User.objects.count(),
                'trainers': Trainer.objects.count(),
            },
            'bookings': {
                'total': Booking.objects.count(),
                'today': Booking.objects.filter(
                    booking_date=time.strftime('%Y-%m-%d')
                ).count(),
            },
            'clients': {
                'total': Client.objects.count(),
            },
            'timestamp': time.time()
        }
        
        return JsonResponse(metrics_data)
    except Exception as e:
        return JsonResponse({
            'error': 'Failed to fetch metrics',
            'message': str(e)
        }, status=500)

