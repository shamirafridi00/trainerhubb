from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    WorkflowViewSet, EmailTemplateViewSet, SMSTemplateViewSet, WorkflowExecutionLogViewSet
)

app_name = 'workflows'

router = DefaultRouter()
router.register(r'workflows', WorkflowViewSet, basename='workflow')
router.register(r'email-templates', EmailTemplateViewSet, basename='email-template')
router.register(r'sms-templates', SMSTemplateViewSet, basename='sms-template')
router.register(r'execution-logs', WorkflowExecutionLogViewSet, basename='execution-log')

urlpatterns = [
    path('', include(router.urls)),
]

