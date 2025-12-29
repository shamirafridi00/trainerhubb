from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.trainers.models import Trainer
from apps.clients.models import Client


class SessionPackage(models.Model):
    """
    Session package (e.g., "5-Pack", "10-Pack").
    """
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='packages')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    sessions_count = models.IntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['trainer', 'name']
        indexes = [
            models.Index(fields=['trainer', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.sessions_count} sessions (${self.price})"


class ClientPackage(models.Model):
    """
    Client's purchase of a package (tracks remaining sessions).
    """
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='purchased_packages')
    session_package = models.ForeignKey(SessionPackage, on_delete=models.SET_NULL, null=True, related_name='client_packages')
    sessions_remaining = models.IntegerField()
    expiry_date = models.DateField(null=True, blank=True)
    purchased_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-purchased_at']
        indexes = [
            models.Index(fields=['client', 'expiry_date']),
        ]
    
    def clean(self):
        """Validate sessions remaining."""
        if self.sessions_remaining < 0:
            raise ValidationError("Sessions remaining cannot be negative.")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.client.get_full_name()} - {self.sessions_remaining} sessions remaining"
    
    @property
    def is_expired(self):
        """Check if package has expired."""
        if not self.expiry_date:
            return False
        return timezone.now().date() > self.expiry_date
    
    @property
    def is_active(self):
        """Check if package is active."""
        return self.sessions_remaining > 0 and not self.is_expired
