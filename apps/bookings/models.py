from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.trainers.models import Trainer
from apps.clients.models import Client


class Booking(models.Model):
    """
    Booking record linking trainer and client at specific time.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no-show', 'No-Show'),
    ]
    
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='bookings')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='bookings')
    start_time = models.DateTimeField(db_index=True)
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    notes = models.TextField(blank=True)
    cancellation_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['trainer', 'start_time']),
            models.Index(fields=['client', 'start_time']),
            models.Index(fields=['status', 'start_time']),
        ]
    
    def clean(self):
        """Validate booking times."""
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError("End time must be after start time.")
            
            # Only check past bookings for new bookings (not updates)
            if not self.pk and self.start_time < timezone.now():
                raise ValidationError("Cannot book in the past.")
            
            # Check for trainer availability conflicts
            if self.status in ['pending', 'confirmed']:
                from apps.availability.utils import has_conflict
                if has_conflict(self.trainer_id, self.start_time, self.end_time):
                    raise ValidationError("Trainer is not available at this time.")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.client.get_full_name()} with {self.trainer.business_name} on {self.start_time.date()}"
    
    @property
    def duration_minutes(self):
        """Calculate duration in minutes."""
        delta = self.end_time - self.start_time
        return int(delta.total_seconds() / 60)
    
    @property
    def is_upcoming(self):
        """Check if booking is in the future."""
        return self.start_time > timezone.now() and self.status != 'cancelled'
    
    @property
    def is_past(self):
        """Check if booking is in the past."""
        return self.end_time < timezone.now()
