from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubscriptionViewSet, PaymentViewSet, paddle_webhook

router = DefaultRouter()
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
    path('webhooks/paddle/', paddle_webhook, name='paddle_webhook'),
]

