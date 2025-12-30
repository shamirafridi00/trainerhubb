from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubscriptionViewSet, PaymentViewSet, ClientPaymentViewSet, paddle_webhook

app_name = 'payments'

router = DefaultRouter()
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'client-payments', ClientPaymentViewSet, basename='client-payment')

urlpatterns = [
    path('', include(router.urls)),
    path('paddle-webhook/', paddle_webhook, name='paddle-webhook'),
    path('webhooks/paddle/', paddle_webhook, name='paddle-webhook-alt'),
]

