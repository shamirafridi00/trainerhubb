from django.db import models
from apps.trainers.models import Trainer


class Client(models.Model):
    """
    Client profile with fitness information.
    Many-to-one relationship with Trainer.
    """
    FITNESS_LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('athlete', 'Athlete'),
    ]
    
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='clients')
    email = models.EmailField()
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True)
    fitness_level = models.CharField(max_length=20, choices=FITNESS_LEVEL_CHOICES, default='beginner')
    goals = models.JSONField(default=list, help_text="List of fitness goals")
    preferences = models.JSONField(default=dict, help_text="Client preferences")
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    # Payment tracking fields
    total_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_payment_date = models.DateField(null=True, blank=True)
    payment_status = models.CharField(max_length=20, default='unpaid', choices=[
        ('unpaid', 'Unpaid'),
        ('partial', 'Partial'),
        ('paid', 'Paid'),
    ])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['trainer', 'email']
        indexes = [
            models.Index(fields=['trainer', 'email']),
            models.Index(fields=['trainer', 'is_active']),
            models.Index(fields=['trainer', 'payment_status']),
            models.Index(fields=['trainer', 'created_at']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.trainer.business_name})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class ClientNote(models.Model):
    """
    Notes about client progress and history.
    """
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='client_notes')
    content = models.TextField()
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['client', 'created_at']),
        ]
    
    def __str__(self):
        return f"Note for {self.client.get_full_name()} on {self.created_at.date()}"
