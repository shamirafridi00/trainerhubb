"""
URL routing for users app.
"""
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

app_name = 'users'
urlpatterns = router.urls

