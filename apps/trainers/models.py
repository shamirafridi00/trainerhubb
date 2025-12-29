from django.db import models
from apps.users.models import User


class Trainer(models.Model):
    """
    Trainer profile with business information.
    OneToOne relationship with User.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='trainer_profile')
    business_name = models.CharField(max_length=255)
    bio = models.TextField(blank=True)
    expertise = models.JSONField(default=list, help_text="List of specialties")
    location = models.CharField(max_length=255, blank=True)
    timezone = models.CharField(max_length=50, default='UTC')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_sessions = models.IntegerField(default=0)
    paddle_customer_id = models.CharField(max_length=255, blank=True, unique=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.business_name} ({self.user.email})"
