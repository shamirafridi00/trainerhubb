"""
Admin Panel Permissions
Only superusers can access admin panel functionality.
"""
from rest_framework import permissions


class IsSuperUser(permissions.BasePermission):
    """
    Only allow superusers to access admin panel.
    """
    message = 'You must be a superuser to access this resource.'
    
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_superuser
        )

