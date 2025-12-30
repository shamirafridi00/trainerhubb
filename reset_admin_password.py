#!/usr/bin/env python
"""
Reset admin password to admin123456
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Reset admin password
admin = User.objects.get(email='admin@trainerhubb.com')
admin.set_password('admin123456')
admin.save()

print("="*70)
print("✓ Password reset successfully!")
print("="*70)
print(f"Email:    {admin.email}")
print(f"Password: admin123456")
print("="*70)

