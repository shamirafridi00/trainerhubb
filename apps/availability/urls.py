from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AvailabilitySlotViewSet, TrainerBreakViewSet

router = DefaultRouter()
router.register(r'availability-slots', AvailabilitySlotViewSet, basename='availability-slot')
router.register(r'breaks', TrainerBreakViewSet, basename='trainer-break')

urlpatterns = [
    path('', include(router.urls)),
]

