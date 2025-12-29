from django.db import models
from django.core.exceptions import ValidationError
from apps.trainers.models import Trainer
from datetime import datetime, time


class AvailabilitySlot(models.Model):
    """
    Recurring availability slots (e.g., Monday 9am-5pm).
    """
    DAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='availability_slots')
    day_of_week = models.IntegerField(choices=DAY_CHOICES)  # 0=Monday, 6=Sunday
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_recurring = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['day_of_week', 'start_time']
        unique_together = ['trainer', 'day_of_week', 'start_time', 'end_time']
        indexes = [
            models.Index(fields=['trainer', 'day_of_week']),
        ]
    
    def clean(self):
        """Validate that end_time is after start_time."""
        if self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time.")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.get_day_of_week_display()} {self.start_time}-{self.end_time}"


class TrainerBreak(models.Model):
    """
    Time off/vacation for trainer (overrides availability).
    """
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='breaks')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['trainer', 'start_date']),
        ]
    
    def clean(self):
        """Validate that end_date is after start_date."""
        if self.start_date >= self.end_date:
            raise ValidationError("End date must be after start date.")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.trainer.business_name} break: {self.start_date.date()}-{self.end_date.date()}"
