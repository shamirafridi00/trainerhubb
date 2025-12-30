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
    
    # DRF API (keep for React Native)
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

# Frontend HTMX views (must be last to catch root URL)
urlpatterns += [
    path('', include('apps.frontend.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
