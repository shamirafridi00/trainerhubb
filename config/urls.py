"""
URL configuration for TrainerHub project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import api_root

urlpatterns = [
    path('admin/', admin.site.urls),

    # DRF API (available for both HTMX and React)
    path('api/', include('apps.users.urls')),
    path('api/trainers/', include('apps.trainers.urls')),
    path('api/', include('apps.availability.urls')),
    path('api/', include('apps.clients.urls')),
    path('api/', include('apps.bookings.urls')),
    path('api/', include('apps.packages.urls')),
    path('api/', include('apps.payments.urls')),  # Includes subscriptions, payments, and webhooks
    path('api/pages/', include('apps.pages.urls')),
    path('api/workflows/', include('apps.workflows.urls')),
    path('api/', include('apps.notifications.urls')),
    path('api/', include('apps.analytics.urls')),
    path('api/admin/', include('apps.admin_panel.urls')),  # Super admin endpoints

    # Public pages API (no authentication)
    path('api/public/<str:trainer_slug>/', include('apps.pages.public_urls')),
]

# Health checks and monitoring (import directly to avoid circular imports)
from apps.core.health_checks import health_check, readiness_check, liveness_check, metrics

urlpatterns += [
    path('health/', health_check, name='health-check'),
    path('ready/', readiness_check, name='readiness-check'),
    path('live/', liveness_check, name='liveness-check'),
    path('metrics/', metrics, name='metrics'),
]

# Dynamic routing based on subdomain type
def get_urlpatterns():
    """Return appropriate urlpatterns based on subdomain."""
    from django.urls import include, path

    # Import here to avoid circular imports
    from apps.pages.middleware import SubdomainMiddleware

    # Create a dummy request to check subdomain type
    from django.http import HttpRequest
    dummy_request = HttpRequest()
    dummy_request.META = {'HTTP_HOST': 'dummy'}  # Will be overridden by middleware

    middleware = SubdomainMiddleware()
    middleware.process_request(dummy_request)

    # For actual routing, we'll use a custom URL resolver
    # For now, include both - middleware will handle the logic
    return [
        path('', include('apps.frontend.urls')),  # HTMX for landing and public pages
        path('', include('apps.react_app.urls')),  # React app URLs
    ]

# Include both frontend systems - middleware will route appropriately
urlpatterns += [
    path('', include('apps.frontend.urls')),  # HTMX landing and public pages
    path('', include('apps.react_app.urls')),  # React app (when subdomain_type == 'react_app')
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
