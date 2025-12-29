from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SessionPackageViewSet, ClientPackageViewSet

router = DefaultRouter()
router.register(r'packages', SessionPackageViewSet, basename='package')
router.register(r'client-packages', ClientPackageViewSet, basename='client-package')

urlpatterns = [
    path('', include(router.urls)),
]

