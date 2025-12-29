from django.db import models
from apps.trainers.models import Trainer


class DashboardMetrics(models.Model):
    """Daily metrics snapshot for analytics."""
    
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='metrics')
    date = models.DateField(db_index=True)
    bookings_count = models.IntegerField(default=0)
    completed_bookings = models.IntegerField(default=0)
    cancelled_bookings = models.IntegerField(default=0)
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    new_clients = models.IntegerField(default=0)
    active_clients = models.IntegerField(default=0)
    average_session_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
        unique_together = ['trainer', 'date']
        indexes = [
            models.Index(fields=['trainer', 'date']),
        ]
    
    def __str__(self):
        return f"{self.trainer.business_name} - {self.date}"
    
    @property
    def completion_rate(self):
        """Calculate booking completion rate."""
        if self.bookings_count == 0:
            return 0
        return round((self.completed_bookings / self.bookings_count) * 100, 2)
    
    @property
    def cancellation_rate(self):
        """Calculate booking cancellation rate."""
        if self.bookings_count == 0:
            return 0
        return round((self.cancelled_bookings / self.bookings_count) * 100, 2)
    
    @property
    def average_revenue_per_booking(self):
        """Calculate average revenue per booking."""
        if self.completed_bookings == 0:
            return 0
        return round(self.revenue / self.completed_bookings, 2)

