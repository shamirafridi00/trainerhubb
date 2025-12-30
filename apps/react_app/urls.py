"""
URL configuration for React app routes.
These routes serve the React SPA when accessed via app.trainerhubb.app
"""
from django.urls import path
from django.shortcuts import render
from django.http import HttpResponse
from apps.trainers.models import Trainer
from apps.admin_panel.models import CustomDomain
import logging

logger = logging.getLogger('subdomain_routing')


def detect_subdomain_type(request):
    """
    Detect subdomain type from request (extracted from SubdomainMiddleware).
    Returns subdomain_type and trainer object.
    """
    host = request.get_host().split(':')[0]  # Remove port if present
    port = request.get_port()
    trainer = None

    # Check for subdomain type from nginx headers (production)
    nginx_subdomain_type = request.META.get('HTTP_X_SUBDOMAIN_TYPE')
    trainer_slug = request.META.get('HTTP_X_TRAINER_SLUG')

    if nginx_subdomain_type:
        # Production: nginx has already determined the subdomain type
        subdomain_type = nginx_subdomain_type

        if nginx_subdomain_type == 'public' and trainer_slug:
            # Find trainer for public pages
            try:
                trainer = Trainer.objects.filter(
                    user__username=trainer_slug
                ).select_related('user').first()

                if not trainer:
                    trainer = Trainer.objects.filter(
                        user__email__startswith=trainer_slug
                    ).select_related('user').first()
            except Trainer.DoesNotExist:
                pass
    else:
        # Local development: determine subdomain type from port
        if port == '3000':
            # Port 3000 -> React app
            subdomain_type = 'react_app'
        elif port == '3001':
            # Port 3001 -> Public pages
            subdomain_type = 'public'
        else:
            # Default port (8000) or any other -> Landing page
            subdomain_type = 'landing'

        # For local development, check if host indicates a specific subdomain type
        if host in ['app.localhost', 'app.trainerhubb.local']:
            subdomain_type = 'react_app'
        elif host.startswith(('trainer-', 'user-')) and (host.endswith('.localhost') or host.endswith('.trainerhubb.local')):
            # Extract trainer slug from subdomain
            trainer_slug = host.split('.')[0].replace('trainer-', '').replace('user-', '')
            subdomain_type = 'public'

            try:
                trainer = Trainer.objects.filter(
                    user__username=trainer_slug
                ).select_related('user').first()

                if not trainer:
                    trainer = Trainer.objects.filter(
                        user__email__startswith=trainer_slug
                    ).select_related('user').first()
            except Trainer.DoesNotExist:
                pass

        # Check for custom domain (even in development)
        try:
            custom_domain = CustomDomain.objects.filter(
                domain=host,
                status='active',
                dns_verified_at__isnull=False
            ).select_related('trainer').first()

            if custom_domain:
                trainer = custom_domain.trainer
                subdomain_type = 'public'
        except CustomDomain.DoesNotExist:
            pass

    # Attach trainer to request
    request.trainer = trainer
    request.is_public_page_request = trainer is not None
    request.subdomain_type = subdomain_type

    # Detect HTMX legacy usage
    if hasattr(request, 'subdomain_type'):
        is_htmx_legacy = request.subdomain_type in ['landing', 'public']
        if is_htmx_legacy:
            logger.warning(
                f"HTMX legacy route accessed: {host}:{port} -> {request.subdomain_type}",
                extra={
                    'host': host,
                    'port': port,
                    'subdomain_type': request.subdomain_type,
                    'trainer_slug': trainer_slug,
                    'trainer_id': trainer.id if trainer else None,
                    'legacy_component': 'subdomain_routing',
                }
            )

    return subdomain_type, trainer


def react_app_view(request, path=''):
    """
    Serve the React app for app.trainerhubb.app subdomain.
    All routes under app.trainerhubb.app should serve the React index.html
    """
    # Check if this is actually the React app subdomain
    subdomain_type, trainer = detect_subdomain_type(request)

    if subdomain_type == 'react_app':
        # This is the React app - serve the React build
        # In production, nginx would serve the built React files
        # For development, we'll serve a placeholder
        return render(request, 'react_app/index.html', {
            'title': 'TrainerHub - Fitness Business Management',
            'description': 'Manage your fitness business with ease'
        })
    else:
        # Not the React subdomain - let other URL patterns handle it
        from django.http import Http404
        raise Http404("Not found")


app_name = 'react_app'

urlpatterns = [
    # Catch-all pattern for React SPA routing
    # All routes under app.trainerhubb.app/* should serve the React app
    path('<path:path>', react_app_view, name='react_app'),
    path('', react_app_view, name='react_app_root'),
]
