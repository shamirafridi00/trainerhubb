"""
White-Label Settings Models
Allows Business tier trainers to customize branding on their public pages.
"""
from django.db import models
from .models import Trainer


class WhiteLabelSettings(models.Model):
    """
    White-label branding settings for Business tier trainers.
    """
    trainer = models.OneToOneField(Trainer, on_delete=models.CASCADE, related_name='whitelabel_settings')
    
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

