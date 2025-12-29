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
    path('api/', include('apps.availability.urls')),
    path('api/', include('apps.clients.urls')),
    path('api/', include('apps.bookings.urls')),
    path('api/', include('apps.packages.urls')),
    path('api/', include('apps.payments.urls')),  # Includes subscriptions, payments, and webhooks
    path('api/', include('apps.notifications.urls')),
    path('api/', include('apps.analytics.urls')),
    
    # Frontend HTMX views (must be last to catch root URL)
    path('', include('apps.frontend.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
