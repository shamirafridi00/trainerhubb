"""
Custom User model for TrainerHub with Supabase integration.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model with email as primary authentication field.
    Integrates with Supabase Auth but also maintains Django auth compatibility.
    """
    email = models.EmailField(unique=True, db_index=True)
    phone_number = models.CharField(max_length=20, blank=True)
    is_trainer = models.BooleanField(default=False)
    is_client = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    
    # Supabase user ID (optional, for linking with Supabase Auth)
    supabase_user_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['created_at']),
            models.Index(fields=['supabase_user_id']),
        ]
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or self.email
