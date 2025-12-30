"""
Public URL routes for serving trainer pages without authentication.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .public_views import (
    PublicPageViewSet,
    get_trainer_profile,
    get_trainer_availability,
    submit_contact_form,
    get_payment_methods,
)
from apps.bookings.public_views import create_public_booking

app_name = 'pages_public'

router = DefaultRouter()
# Note: We use trainer_slug in the URL pattern at the config level
router.register(r'pages', PublicPageViewSet, basename='public-page')

urlpatterns = [
    path('', include(router.urls)),
    path('profile/', get_trainer_profile, name='trainer-profile'),
    path('availability/', get_trainer_availability, name='trainer-availability'),
    path('bookings/', create_public_booking, name='create-booking'),
    path('contact/', submit_contact_form, name='contact-form'),
    path('payment-methods/', get_payment_methods, name='payment-methods'),
]

