"""
Middleware for detecting trainer subdomain from request.
"""
from django.utils.deprecation import MiddlewareMixin
from apps.trainers.models import Trainer
from apps.admin_panel.models import CustomDomain


class SubdomainMiddleware(MiddlewareMixin):
    """
    Detect trainer subdomain or custom domain from request and attach trainer to request object.
    """
    
    def process_request(self, request):
        host = request.get_host().split(':')[0]  # Remove port if present
        trainer = None
        
        # Check if this is a custom domain
        try:
            custom_domain = CustomDomain.objects.filter(
                domain=host,
                status='active',
                dns_verified_at__isnull=False
            ).select_related('trainer').first()
            
            if custom_domain:
                trainer = custom_domain.trainer
        except CustomDomain.DoesNotExist:
            pass
        
        # If not custom domain, check for subdomain
        if not trainer and '.trainerhubb.app' in host:
            # Extract subdomain: trainer-slug.trainerhubb.app -> trainer-slug
            subdomain = host.split('.trainerhubb.app')[0]
            
            # Don't process if it's www or api
            if subdomain not in ['www', 'api', 'admin']:
                try:
                    # Try to find trainer by slug
                    # Assuming trainer has a slug field (we'll add this if needed)
                    trainer = Trainer.objects.filter(
                        user__username=subdomain
                    ).select_related('user').first()
                    
                    # Fallback: try by user email prefix
                    if not trainer:
                        trainer = Trainer.objects.filter(
                            user__email__startswith=subdomain
                        ).select_related('user').first()
                except Trainer.DoesNotExist:
                    pass
        
        # Attach trainer to request
        request.trainer = trainer
        request.is_public_page_request = trainer is not None
        
        return None

