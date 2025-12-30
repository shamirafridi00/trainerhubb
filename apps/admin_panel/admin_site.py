"""
Custom Admin Site Configuration
Provides better branding and organization for the Django admin interface.
"""
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _


class TrainerHubAdminSite(AdminSite):
    """
    Custom admin site with TrainerHub branding.
    """
    site_header = "TrainerHub Admin Panel"
    site_title = "TrainerHub Admin"
    index_title = "Welcome to TrainerHub Administration"
    site_url = "/"
    
    def get_app_list(self, request):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site, with custom ordering.
        """
        app_dict = self._build_app_dict(request)
        
        # Custom ordering for apps
        app_ordering = {
            'admin_panel': 1,
            'users': 2,
            'trainers': 3,
            'clients': 4,
            'bookings': 5,
            'payments': 6,
            'packages': 7,
            'notifications': 8,
            'analytics': 9,
            'availability': 10,
        }
        
        # Sort apps by custom ordering
        app_list = sorted(
            app_dict.values(),
            key=lambda x: app_ordering.get(x['app_label'], 999)
        )
        
        return app_list


# Create custom admin site instance
admin_site = TrainerHubAdminSite(name='trainerhub_admin')

