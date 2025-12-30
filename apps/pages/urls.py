from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PageTemplateViewSet, PageViewSet

app_name = 'pages'

router = DefaultRouter()
router.register(r'templates', PageTemplateViewSet, basename='template')
router.register(r'', PageViewSet, basename='page')

urlpatterns = [
    path('', include(router.urls)),
    # Section management routes
    path('<int:pk>/sections/', PageViewSet.as_view({'get': 'manage_sections', 'post': 'manage_sections'}), name='page-sections'),
    path('<int:pk>/sections/<int:section_id>/', PageViewSet.as_view({'patch': 'manage_section', 'delete': 'manage_section'}), name='page-section-detail'),
]

