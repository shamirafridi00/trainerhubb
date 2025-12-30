"""
Middleware for detecting trainer subdomain from request.
"""
import logging
from django.utils.deprecation import MiddlewareMixin
from apps.trainers.models import Trainer
from apps.admin_panel.models import CustomDomain

logger = logging.getLogger('subdomain_routing')


class SubdomainMiddleware(MiddlewareMixin):
    """
    Detect subdomain type and route accordingly:
    - trainerhubb.app -> Landing page (HTMX)
    - app.trainerhubb.app -> React app
    - trainer-slug.trainerhubb.app -> Public pages (HTMX)
    - custom-domain.com -> Public pages (HTMX)
    """

    def process_request(self, request):
        host = request.get_host().split(':')[0]  # Remove port if present
        port = request.get_port()
        trainer = None

        # Check for subdomain type from nginx headers (production)
        nginx_subdomain_type = request.META.get('HTTP_X_SUBDOMAIN_TYPE')
        trainer_slug = request.META.get('HTTP_X_TRAINER_SLUG')

        if nginx_subdomain_type:
            # Production: nginx has already determined the subdomain type
            request.subdomain_type = nginx_subdomain_type

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
                request.subdomain_type = 'react_app'
            elif port == '3001':
                # Port 3001 -> Public pages
                request.subdomain_type = 'public'
            else:
                # Default port (8000) or any other -> Landing page
                request.subdomain_type = 'landing'

            # For local development, check if host indicates a specific subdomain type
            if host in ['app.localhost', 'app.trainerhubb.local']:
                request.subdomain_type = 'react_app'
            elif host.startswith(('trainer-', 'user-')) and (host.endswith('.localhost') or host.endswith('.trainerhubb.local')):
                # Extract trainer slug from subdomain
                trainer_slug = host.split('.')[0].replace('trainer-', '').replace('user-', '')
                request.subdomain_type = 'public'

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
                    request.subdomain_type = 'public'
            except CustomDomain.DoesNotExist:
                pass

        # Attach trainer to request
        request.trainer = trainer
        request.is_public_page_request = trainer is not None

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

        return None

