"""
Context processors for Django templates.
"""
import logging
from django.conf import settings

logger = logging.getLogger('template_rendering')


def htmx_legacy_warning(request):
    """
    Add deprecation warning for HTMX legacy templates.

    This context processor detects when legacy HTMX templates are being rendered
    and logs a warning for observability during the migration period.
    """
    # This will be called for every template render
    # We can't easily detect which specific template, but we can detect legacy usage
    if hasattr(request, 'path') and not request.path.startswith('/api/'):
        # Check if this might be an HTMX legacy request
        is_legacy_path = any(request.path.startswith(prefix) for prefix in [
            '/dashboard', '/bookings', '/clients', '/packages',
            '/analytics', '/settings', '/notifications'
        ])

        if is_legacy_path and hasattr(settings, 'USE_HTMX') and settings.USE_HTMX:
            logger.warning(
                f"Legacy HTMX template rendered: {request.path}",
                extra={
                    'path': request.path,
                    'user': request.user.email if request.user.is_authenticated else 'anonymous',
                    'method': request.method,
                    'legacy_component': 'template_rendering',
                }
            )

    return {}
