from django.db import models
from apps.trainers.models import Trainer
from apps.users.models import User


class Workflow(models.Model):
    """Automated workflow definition"""
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='workflows')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['trainer', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.trainer.business_name} - {self.name}"


class WorkflowTrigger(models.Model):
    """Event that triggers workflow"""
    TRIGGER_TYPES = [
        ('booking_created', 'Booking Created'),
        ('booking_confirmed', 'Booking Confirmed'),
        ('booking_cancelled', 'Booking Cancelled'),
        ('booking_reminder', 'Booking Reminder'),
        ('payment_received', 'Payment Received'),
        ('client_created', 'Client Created'),
        ('package_purchased', 'Package Purchased'),
        ('custom', 'Custom Trigger'),
    ]
    
    workflow = models.OneToOneField(Workflow, on_delete=models.CASCADE, related_name='trigger')
    trigger_type = models.CharField(max_length=50, choices=TRIGGER_TYPES)
    conditions = models.JSONField(default=dict)  # Additional conditions
    delay_minutes = models.IntegerField(default=0)  # Delay before triggering
    
    def __str__(self):
        return f"{self.workflow.name} - {self.get_trigger_type_display()}"


class WorkflowAction(models.Model):
    """Action to execute when workflow triggers"""
    ACTION_TYPES = [
        ('send_email', 'Send Email'),
        ('send_sms', 'Send SMS'),
        ('update_status', 'Update Status'),
        ('create_note', 'Create Note'),
    ]
    
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='actions')
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    action_data = models.JSONField(default=dict)  # Action-specific data
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        indexes = [
            models.Index(fields=['workflow', 'order']),
        ]
    
    def __str__(self):
        return f"{self.workflow.name} - {self.get_action_type_display()}"


class EmailTemplate(models.Model):
    """Email template for workflows"""
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='email_templates')
    name = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    variables = models.JSONField(default=list)  # Available variables
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.trainer.business_name} - {self.name}"


class SMSTemplate(models.Model):
    """SMS template for workflows"""
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='sms_templates')
    name = models.CharField(max_length=255)
    message = models.CharField(max_length=160)  # SMS limit
    variables = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.trainer.business_name} - {self.name}"


class WorkflowTemplate(models.Model):
    """Pre-built workflow templates that can be cloned"""
    CATEGORY_CHOICES = [
        ('booking', 'Booking Management'),
        ('payment', 'Payment & Billing'),
        ('client', 'Client Communication'),
        ('reminder', 'Reminders & Notifications'),
        ('general', 'General'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='general')
    icon = models.CharField(max_length=50, blank=True)  # Icon name for UI
    
    # Template configuration (to be cloned)
    trigger_type = models.CharField(max_length=50)
    trigger_delay_minutes = models.IntegerField(default=0)
    trigger_conditions = models.JSONField(default=dict)
    
    # Actions configuration (list of actions to create)
    actions_config = models.JSONField(default=list)  # List of action dicts
    
    # Usage tracking
    times_used = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['category', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class WorkflowExecutionLog(models.Model):
    """Log of workflow executions"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='executions')
    trigger_type = models.CharField(max_length=50)
    trigger_data = models.JSONField(default=dict)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    executed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-executed_at']
        indexes = [
            models.Index(fields=['workflow', 'status']),
            models.Index(fields=['executed_at']),
        ]
    
    def __str__(self):
        return f"{self.workflow.name} - {self.status} - {self.executed_at}"
