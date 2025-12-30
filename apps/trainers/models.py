from django.db import models
from apps.users.models import User


class WhiteLabelSettings(models.Model):
    """
    White-label branding settings for Business tier trainers.
    """
    trainer = models.OneToOneField('Trainer', on_delete=models.CASCADE, related_name='whitelabel_settings')
    
    # Branding Options
    remove_branding = models.BooleanField(default=False, help_text="Remove 'Powered by TrainerHub' footer")
    custom_logo = models.ImageField(upload_to='whitelabel/logos/', null=True, blank=True, help_text="Custom logo (max 500KB, PNG/SVG)")
    custom_favicon = models.ImageField(upload_to='whitelabel/favicons/', null=True, blank=True, help_text="Custom favicon (16x16 or 32x32)")
    
    # Brand Colors
    primary_color = models.CharField(max_length=7, default='#3b82f6', help_text="Primary brand color (hex)")
    secondary_color = models.CharField(max_length=7, default='#10b981', help_text="Secondary brand color (hex)")
    accent_color = models.CharField(max_length=7, default='#f59e0b', help_text="Accent color (hex)")
    
    # Text Colors
    text_color = models.CharField(max_length=7, default='#1f2937', help_text="Primary text color (hex)")
    background_color = models.CharField(max_length=7, default='#ffffff', help_text="Background color (hex)")
    
    # Typography
    font_family = models.CharField(
        max_length=100,
        default='Inter',
        help_text="Google Fonts font family name"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'White Label Settings'
        verbose_name_plural = 'White Label Settings'
    
    def __str__(self):
        return f"White Label Settings - {self.trainer.business_name}"
    
    def has_custom_branding(self):
        """Check if trainer has any custom branding."""
        return (
            self.remove_branding or
            self.custom_logo or
            self.primary_color != '#3b82f6' or
            self.secondary_color != '#10b981'
        )
    
    def get_css_variables(self):
        """Generate CSS variables for custom branding."""
        return {
            '--primary-color': self.primary_color,
            '--secondary-color': self.secondary_color,
            '--accent-color': self.accent_color,
            '--text-color': self.text_color,
            '--background-color': self.background_color,
            '--font-family': f"'{self.font_family}', sans-serif",
        }


class PaymentLinks(models.Model):
    """
    Payment links configuration for trainers to receive payments.
    """
    trainer = models.OneToOneField('Trainer', on_delete=models.CASCADE, related_name='payment_links')
    
    # Popular payment methods
    stripe_link = models.URLField(blank=True, help_text="Stripe payment link")
    paypal_link = models.URLField(blank=True, help_text="PayPal.me or payment link")
    venmo_username = models.CharField(max_length=100, blank=True, help_text="Venmo username (without @)")
    zelle_email = models.EmailField(blank=True, help_text="Zelle email or phone")
    cashapp_username = models.CharField(max_length=100, blank=True, help_text="Cash App $cashtag (without $)")
    
    # Bank transfer info
    bank_name = models.CharField(max_length=100, blank=True)
    account_holder_name = models.CharField(max_length=100, blank=True)
    account_number_last4 = models.CharField(max_length=4, blank=True, help_text="Last 4 digits only")
    routing_number = models.CharField(max_length=20, blank=True)
    
    # Custom payment links
    custom_links = models.JSONField(
        default=list,
        help_text="List of custom payment links: [{'label': 'Link Name', 'url': 'https://...'}]"
    )
    
    # Display preferences
    show_on_public_pages = models.BooleanField(default=True)
    payment_instructions = models.TextField(blank=True, help_text="Custom instructions for clients")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Payment Links'
        verbose_name_plural = 'Payment Links'
    
    def __str__(self):
        return f"Payment Links - {self.trainer.business_name}"
    
    def get_available_methods(self):
        """Get list of configured payment methods."""
        methods = []
        if self.stripe_link:
            methods.append({'type': 'stripe', 'label': 'Credit/Debit Card', 'url': self.stripe_link})
        if self.paypal_link:
            methods.append({'type': 'paypal', 'label': 'PayPal', 'url': self.paypal_link})
        if self.venmo_username:
            methods.append({'type': 'venmo', 'label': 'Venmo', 'url': f'https://venmo.com/{self.venmo_username}'})
        if self.zelle_email:
            methods.append({'type': 'zelle', 'label': 'Zelle', 'info': self.zelle_email})
        if self.cashapp_username:
            methods.append({'type': 'cashapp', 'label': 'Cash App', 'url': f'https://cash.app/${self.cashapp_username}'})
        if self.bank_name:
            methods.append({
                'type': 'bank',
                'label': 'Bank Transfer',
                'info': f'{self.bank_name} - ending in {self.account_number_last4}'
            })
        for link in self.custom_links:
            methods.append({'type': 'custom', 'label': link.get('label'), 'url': link.get('url')})
        return methods


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
