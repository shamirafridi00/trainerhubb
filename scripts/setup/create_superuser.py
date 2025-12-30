#!/usr/bin/env python
"""
Quick script to create a superuser for admin panel.
Run with: python create_superuser.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Admin credentials
EMAIL = 'admin@trainerhub.app'
USERNAME = 'admin'
PASSWORD = 'admin123456'  # Change this after first login!

# Check if superuser already exists
if User.objects.filter(email=EMAIL).exists():
    print(f"✗ Superuser with email {EMAIL} already exists!")
    user = User.objects.get(email=EMAIL)
    print(f"  User ID: {user.id}")
    print(f"  Is Superuser: {user.is_superuser}")
    print(f"  Is Active: {user.is_active}")
    
    # Update to ensure it's a superuser
    if not user.is_superuser:
        user.is_superuser = True
        user.is_staff = True
        user.save()
        print(f"✓ Updated user to superuser status")
    
    # Reset password
    reset = input("\nDo you want to reset the password to 'admin123456'? (y/n): ")
    if reset.lower() == 'y':
        user.set_password(PASSWORD)
        user.save()
        print("✓ Password reset successfully!")
else:
    # Create new superuser
    user = User.objects.create_superuser(
        email=EMAIL,
        username=USERNAME,
        password=PASSWORD
    )
    print(f"✓ Superuser created successfully!")
    print(f"  Email: {EMAIL}")
    print(f"  Username: {USERNAME}")
    print(f"  Password: {PASSWORD}")

print("\n" + "="*60)
print("LOGIN CREDENTIALS FOR ADMIN PANEL")
print("="*60)
print(f"Email:    {EMAIL}")
print(f"Password: {PASSWORD}")
print("="*60)
print("\n⚠️  IMPORTANT: Change this password after first login!")
print("\nTo login to admin panel:")
print("1. Start server: python manage.py runserver")
print("2. Login endpoint: POST http://localhost:8000/api/auth/login/")
print("3. Use the credentials above")

