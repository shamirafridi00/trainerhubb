from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Workflow, WorkflowTrigger, WorkflowAction, EmailTemplate, SMSTemplate, WorkflowExecutionLog, WorkflowTemplate
from .serializers import (
    WorkflowSerializer, WorkflowCreateSerializer,
    EmailTemplateSerializer, SMSTemplateSerializer,
    WorkflowExecutionLogSerializer, WorkflowTemplateSerializer
)
from apps.payments.permissions import check_usage_limit


class WorkflowViewSet(viewsets.ModelViewSet):
    """ViewSet for managing workflows"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter to current trainer's workflows"""
        if hasattr(self.request.user, 'trainer_profile'):
            return Workflow.objects.filter(
                trainer=self.request.user.trainer_profile
            ).prefetch_related('trigger', 'actions').order_by('-created_at')
        return Workflow.objects.none()
    
    def get_serializer_class(self):
        """Use different serializer for create"""
        if self.action == 'create':
            return WorkflowCreateSerializer
        return WorkflowSerializer
    
    def perform_create(self, serializer):
        """Set trainer and check usage limits"""
        if not hasattr(self.request.user, 'trainer_profile'):
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'error': 'User is not a trainer'})
        
        trainer = self.request.user.trainer_profile
        
        # Check workflow usage limit
        can_create, current_count, limit = check_usage_limit(trainer, 'workflows')
        if not can_create:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({
                'error': 'Usage limit reached',
                'detail': f'You have reached your limit of {limit} workflows. Upgrade your plan to add more.',
                'current_count': current_count,
                'limit': limit
            })
        
        serializer.save(trainer=trainer)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a workflow"""
        workflow = self.get_object()
        workflow.is_active = True
        workflow.save()
        serializer = self.get_serializer(workflow)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a workflow"""
        workflow = self.get_object()
        workflow.is_active = False
        workflow.save()
        serializer = self.get_serializer(workflow)
        return Response(serializer.data)


class EmailTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for managing email templates"""
    permission_classes = [IsAuthenticated]
    serializer_class = EmailTemplateSerializer
    
    def get_queryset(self):
        """Filter to current trainer's templates"""
        if hasattr(self.request.user, 'trainer_profile'):
            return EmailTemplate.objects.filter(
                trainer=self.request.user.trainer_profile
            ).order_by('-created_at')
        return EmailTemplate.objects.none()
    
    def perform_create(self, serializer):
        """Set trainer"""
        if not hasattr(self.request.user, 'trainer_profile'):
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'error': 'User is not a trainer'})
        serializer.save(trainer=self.request.user.trainer_profile)


class SMSTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for managing SMS templates"""
    permission_classes = [IsAuthenticated]
    serializer_class = SMSTemplateSerializer
    
    def get_queryset(self):
        """Filter to current trainer's templates"""
        if hasattr(self.request.user, 'trainer_profile'):
            return SMSTemplate.objects.filter(
                trainer=self.request.user.trainer_profile
            ).order_by('-created_at')
        return SMSTemplate.objects.none()
    
    def perform_create(self, serializer):
        """Set trainer"""
        if not hasattr(self.request.user, 'trainer_profile'):
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'error': 'User is not a trainer'})
        serializer.save(trainer=self.request.user.trainer_profile)


class WorkflowExecutionLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing workflow execution logs"""
    permission_classes = [IsAuthenticated]
    serializer_class = WorkflowExecutionLogSerializer
    
    def get_queryset(self):
        """Filter to current trainer's workflow executions"""
        if hasattr(self.request.user, 'trainer_profile'):
            trainer = self.request.user.trainer_profile
            workflow_ids = Workflow.objects.filter(trainer=trainer).values_list('id', flat=True)
            return WorkflowExecutionLog.objects.filter(
                workflow_id__in=workflow_ids
            ).select_related('workflow').order_by('-executed_at')
        return WorkflowExecutionLog.objects.none()


class WorkflowTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing and using workflow templates"""
    permission_classes = [IsAuthenticated]
    serializer_class = WorkflowTemplateSerializer
    queryset = WorkflowTemplate.objects.filter(is_active=True)
    
    @action(detail=True, methods=['post'])
    def use_template(self, request, pk=None):
        """
        Clone a template into a new workflow for the current trainer.
        POST /api/workflows/templates/{id}/use_template/
        """
        if not hasattr(request.user, 'trainer_profile'):
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'error': 'User is not a trainer'})
        
        trainer = request.user.trainer_profile
        template = self.get_object()
        
        # Check usage limits
        can_create, current_count, limit = check_usage_limit(trainer, 'workflows')
        if not can_create:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({
                'error': 'Usage limit reached',
                'detail': f'You have reached your limit of {limit} workflows. Upgrade your plan to add more.',
                'current_count': current_count,
                'limit': limit
            })
        
        # Create workflow from template
        workflow = Workflow.objects.create(
            trainer=trainer,
            name=template.name,
            description=template.description,
            is_active=False  # Start inactive so trainer can customize
        )
        
        # Create trigger
        WorkflowTrigger.objects.create(
            workflow=workflow,
            trigger_type=template.trigger_type,
            conditions=template.trigger_conditions,
            delay_minutes=template.trigger_delay_minutes
        )
        
        # Create actions
        for action_config in template.actions_config:
            WorkflowAction.objects.create(
                workflow=workflow,
                action_type=action_config['action_type'],
                action_data=action_config['action_data'],
                order=action_config['order']
            )
        
        # Increment usage counter
        template.times_used += 1
        template.save(update_fields=['times_used'])
        
        # Return the created workflow
        serializer = WorkflowSerializer(workflow)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
