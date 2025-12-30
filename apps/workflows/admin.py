from django.contrib import admin
from .models import Workflow, WorkflowTrigger, WorkflowAction, EmailTemplate, SMSTemplate, WorkflowExecutionLog


@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'trainer', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'trainer__business_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(WorkflowTrigger)
class WorkflowTriggerAdmin(admin.ModelAdmin):
    list_display = ['id', 'workflow', 'trigger_type', 'delay_minutes']
    list_filter = ['trigger_type']
    search_fields = ['workflow__name']


@admin.register(WorkflowAction)
class WorkflowActionAdmin(admin.ModelAdmin):
    list_display = ['id', 'workflow', 'action_type', 'order']
    list_filter = ['action_type']
    search_fields = ['workflow__name']
    ordering = ['workflow', 'order']


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'trainer', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'trainer__business_name', 'subject']
    readonly_fields = ['created_at']


@admin.register(SMSTemplate)
class SMSTemplateAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'trainer', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'trainer__business_name']
    readonly_fields = ['created_at']


@admin.register(WorkflowExecutionLog)
class WorkflowExecutionLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'workflow', 'trigger_type', 'status', 'executed_at']
    list_filter = ['status', 'trigger_type', 'executed_at']
    search_fields = ['workflow__name']
    readonly_fields = ['executed_at']
