from rest_framework import serializers
from .models import Workflow, WorkflowTrigger, WorkflowAction, EmailTemplate, SMSTemplate, WorkflowExecutionLog, WorkflowTemplate


class WorkflowTriggerSerializer(serializers.ModelSerializer):
    """Serializer for workflow triggers"""
    
    class Meta:
        model = WorkflowTrigger
        fields = ['id', 'trigger_type', 'conditions', 'delay_minutes']
        read_only_fields = ['id']


class WorkflowActionSerializer(serializers.ModelSerializer):
    """Serializer for workflow actions"""
    
    class Meta:
        model = WorkflowAction
        fields = ['id', 'action_type', 'action_data', 'order']
        read_only_fields = ['id']


class WorkflowSerializer(serializers.ModelSerializer):
    """Serializer for workflows"""
    trigger = WorkflowTriggerSerializer(read_only=True)
    actions = WorkflowActionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Workflow
        fields = [
            'id', 'trainer', 'name', 'description', 'is_active',
            'trigger', 'actions', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'trainer', 'created_at', 'updated_at']


class WorkflowCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating workflows"""
    trigger = WorkflowTriggerSerializer()
    actions = WorkflowActionSerializer(many=True)
    
    class Meta:
        model = Workflow
        fields = ['name', 'description', 'is_active', 'trigger', 'actions']
    
    def create(self, validated_data):
        trigger_data = validated_data.pop('trigger')
        actions_data = validated_data.pop('actions')
        
        workflow = Workflow.objects.create(**validated_data)
        
        # Create trigger
        WorkflowTrigger.objects.create(workflow=workflow, **trigger_data)
        
        # Create actions
        for action_data in actions_data:
            WorkflowAction.objects.create(workflow=workflow, **action_data)
        
        return workflow


class EmailTemplateSerializer(serializers.ModelSerializer):
    """Serializer for email templates"""
    
    class Meta:
        model = EmailTemplate
        fields = ['id', 'name', 'subject', 'body', 'variables', 'created_at']
        read_only_fields = ['id', 'created_at']


class SMSTemplateSerializer(serializers.ModelSerializer):
    """Serializer for SMS templates"""
    
    class Meta:
        model = SMSTemplate
        fields = ['id', 'name', 'message', 'variables', 'created_at']
        read_only_fields = ['id', 'created_at']


class WorkflowExecutionLogSerializer(serializers.ModelSerializer):
    """Serializer for workflow execution logs"""
    
    class Meta:
        model = WorkflowExecutionLog
        fields = [
            'id', 'workflow', 'trigger_type', 'trigger_data',
            'status', 'error_message', 'executed_at'
        ]
        read_only_fields = ['id', 'executed_at']


class WorkflowTemplateSerializer(serializers.ModelSerializer):
    """Serializer for workflow templates"""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = WorkflowTemplate
        fields = [
            'id', 'name', 'description', 'category', 'category_display', 'icon',
            'trigger_type', 'trigger_delay_minutes', 'trigger_conditions',
            'actions_config', 'times_used', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'times_used', 'created_at']

