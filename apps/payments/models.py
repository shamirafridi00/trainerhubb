from django.db import models
from apps.trainers.models import Trainer
from apps.clients.models import Client
from apps.users.models import User


class Subscription(models.Model):
    """
    Paddle subscription linked to trainer.
    Stores subscription details and handles plan-based feature access.
    """
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('pro', 'Pro'),
        ('business', 'Business'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('past_due', 'Past Due'),
        ('paused', 'Paused'),
        ('cancelled', 'Cancelled'),
        ('trialing', 'Trialing'),
    ]
    
    trainer = models.OneToOneField(Trainer, on_delete=models.CASCADE, related_name='subscription')
    paddle_subscription_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    paddle_customer_id = models.CharField(max_length=255, null=True, blank=True)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    cancel_at_period_end = models.BooleanField(default=False)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    trial_end = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['trainer', 'status']),
            models.Index(fields=['plan']),
            models.Index(fields=['paddle_subscription_id']),
        ]
    
    def __str__(self):
        return f"{self.trainer.business_name} - {self.get_plan_display()} ({self.status})"
    
    def is_active(self):
        """Check if subscription is active."""
        return self.status in ['active', 'trialing']
    
    def can_access_feature(self, feature):
        """Check if plan allows access to a feature."""
        feature_matrix = {
            'free': {
                'max_clients': 10,
                'max_pages': 1,
                'custom_domain': False,
                'white_label': False,
                'workflows': False,
            },
            'pro': {
                'max_clients': -1,  # unlimited
                'max_pages': 5,
                'custom_domain': False,
                'white_label': False,
                'workflows': True,
            },
            'business': {
                'max_clients': -1,  # unlimited
                'max_pages': -1,  # unlimited
                'custom_domain': True,
                'white_label': True,
                'workflows': True,
            },
        }
        return feature_matrix.get(self.plan, {}).get(feature, False)


class Payment(models.Model):
    """
    Payment record from Paddle webhook.
    Tracks all transactions for subscription billing.
    """
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    paddle_transaction_id = models.CharField(max_length=255, unique=True)
    paddle_invoice_id = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    receipt_url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['subscription', 'created_at']),
            models.Index(fields=['trainer', 'created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['paddle_transaction_id']),
        ]
    
    def __str__(self):
        trainer_name = self.subscription.trainer.business_name if self.subscription else self.trainer.business_name
        return f"{trainer_name} - ${self.amount} ({self.status})"


class WebhookEvent(models.Model):
    """
    Log of all Paddle webhook events for debugging and audit.
    """
    event_id = models.CharField(max_length=255, unique=True)
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event_type', 'created_at']),
            models.Index(fields=['processed']),
            models.Index(fields=['event_id']),
        ]
    
    def __str__(self):
        return f"{self.event_type} - {self.event_id} ({'Processed' if self.processed else 'Pending'})"


class ClientPayment(models.Model):
    """
    Manual payment tracking - platform doesn't process these payments.
    Trainers manually record when clients pay them via external methods.
    """
    PAYMENT_METHODS = [
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('venmo', 'Venmo'),
        ('zelle', 'Zelle'),
        ('other', 'Other'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS)
    payment_date = models.DateField()
    reference_id = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # Optional links
    package = models.ForeignKey('packages.ClientPackage', null=True, blank=True, on_delete=models.SET_NULL)
    booking = models.ForeignKey('bookings.Booking', null=True, blank=True, on_delete=models.SET_NULL)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-payment_date', '-created_at']
        indexes = [
            models.Index(fields=['client', 'payment_date']),
            models.Index(fields=['payment_method']),
            models.Index(fields=['payment_date']),
        ]
    
    def __str__(self):
        return f"{self.client.get_full_name()} - {self.currency} {self.amount} ({self.payment_method})"
