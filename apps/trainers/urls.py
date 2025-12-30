"""
URL Configuration for Trainers App
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TrainerViewSet, WhiteLabelSettingsViewSet, PaymentLinksViewSet

app_name = 'trainers'

router = DefaultRouter()
router.register(r'', TrainerViewSet, basename='trainer')
router.register(r'whitelabel', WhiteLabelSettingsViewSet, basename='whitelabel')
router.register(r'payment-links', PaymentLinksViewSet, basename='payment-links')

urlpatterns = [
    path('', include(router.urls)),
]

