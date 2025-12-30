"""
Views for the interactive logger/activity tracker.
"""
import json
import logging
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import datetime, timedelta

logger = logging.getLogger('user_interactions')


class ActivityLogger:
    """In-memory activity logger for real-time display."""
    
    _activities = []
    _max_activities = 1000
    
    @classmethod
    def log(cls, activity_type, message, details=None, user=None):
        """Log an activity."""
        activity = {
            'id': len(cls._activities) + 1,
            'type': activity_type,
            'message': message,
            'details': details or {},
            'user': user,
            'timestamp': timezone.now().isoformat(),
            'time': timezone.now().strftime('%H:%M:%S')
        }
        cls._activities.append(activity)
        
        # Keep only last N activities
        if len(cls._activities) > cls._max_activities:
            cls._activities = cls._activities[-cls._max_activities:]
        
        # Also log to Django logger (use a copy without 'message' key to avoid overwriting LogRecord field)
        log_extra = {k: v for k, v in activity.items() if k != 'message'}
        logger.info(f"{activity_type}: {message}", extra=log_extra)
        
        return activity
    
    @classmethod
    def get_activities(cls, limit=100):
        """Get recent activities."""
        return cls._activities[-limit:]
    
    @classmethod
    def clear(cls):
        """Clear all activities."""
        cls._activities = []


@login_required
def logger_viewer(request):
    """Logger viewer page."""
    # Only allow superusers and staff to view logger (optional - remove if you want all users)
    # if not (request.user.is_superuser or request.user.is_staff):
    #     from django.http import HttpResponseForbidden
    #     return HttpResponseForbidden("You don't have permission to view the logger.")
    return render(request, 'pages/logger/viewer.html')


@login_required
@require_http_methods(["POST"])
def log_activity(request):
    """Log an activity from frontend."""
    try:
        # Handle both JSON and form data
        content_type = request.content_type or ''
        
        if 'application/json' in content_type:
            try:
                data = json.loads(request.body.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                return JsonResponse({'error': f'Invalid JSON: {str(e)}'}, status=400)
        else:
            # Try to parse as JSON first (some browsers send JSON with wrong content-type)
            try:
                data = json.loads(request.body.decode('utf-8'))
            except:
                # Fall back to form data
                data = request.POST.dict()
        
        activity_type = data.get('type', 'click')
        message = data.get('message', 'User interaction')
        details = data.get('details', {})
        
        # Parse details if it's a string
        if isinstance(details, str):
            try:
                details = json.loads(details)
            except:
                details = {}
        
        # Ensure details is a dict
        if not isinstance(details, dict):
            details = {}
        
        ActivityLogger.log(
            activity_type=activity_type,
            message=message,
            details=details,
            user=request.user.email
        )
        
        return JsonResponse({'status': 'ok', 'logged': True})
    except Exception as e:
        import traceback
        import logging
        logger = logging.getLogger('user_interactions')
        error_msg = str(e)
        logger.error(f'Error logging activity: {error_msg}', exc_info=True)
        return JsonResponse({'error': error_msg}, status=400)


@login_required
def get_activities(request):
    """Get recent activities as JSON."""
    limit = int(request.GET.get('limit', 100))
    activities = ActivityLogger.get_activities(limit=limit)
    return JsonResponse({'activities': activities})


@login_required
@require_http_methods(["POST"])
def clear_activities(request):
    """Clear all activities."""
    ActivityLogger.clear()
    return JsonResponse({'status': 'cleared'})

