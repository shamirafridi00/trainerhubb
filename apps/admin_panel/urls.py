"""
Admin Panel URL Configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AdminDashboardViewSet,
    TrainerAdminViewSet,
    AdminActionLogViewSet
)
from .domain_views import (
    DomainAdminViewSet,
    DomainVerificationLogViewSet
)

app_name = 'admin_panel'

router = DefaultRouter()
router.register(r'dashboard', AdminDashboardViewSet, basename='admin-dashboard')
router.register(r'trainers', TrainerAdminViewSet, basename='admin-trainers')
router.register(r'logs', AdminActionLogViewSet, basename='admin-logs')
router.register(r'domains', DomainAdminViewSet, basename='admin-domains')
router.register(r'domain-logs', DomainVerificationLogViewSet, basename='admin-domain-logs')

# Note: bulk-action, export, and export-detail are @action decorators on TrainerAdminViewSet
# They are automatically registered by DRF at:
# - /trainers/bulk-action/
# - /trainers/export/
# - /trainers/{id}/export-detail/
#
# Domain action endpoints:
# - /domains/pending/
# - /domains/needs-ssl-renewal/
# - /domains/{id}/verify/
# - /domains/{id}/provision-ssl/
# - /domains/{id}/approve-reject/

urlpatterns = [
    path('', include(router.urls)),
]

