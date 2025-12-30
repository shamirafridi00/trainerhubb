#!/usr/bin/env python3
"""
Script to create or update trainer profile for a user.
Usage: python create_trainer_profile.py <email> [business_name]
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.trainers.models import Trainer

User = get_user_model()

def create_trainer_profile(email, business_name=None):
    """Create or update trainer profile for a user."""
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        print(f"❌ User with email {email} not found.")
        return False
    
    # Check if trainer profile already exists
    try:
        trainer = user.trainer_profile
        print(f"✓ Trainer profile already exists for {email}")
        print(f"  Business Name: {trainer.business_name}")
        
        if business_name and business_name != trainer.business_name:
            trainer.business_name = business_name
            trainer.save()
            print(f"  Updated business name to: {business_name}")
        
        return True
    except Trainer.DoesNotExist:
        # Create new trainer profile
        if not business_name:
            business_name = user.get_full_name() or f"{user.email}'s Fitness Business"
        
        trainer = Trainer.objects.create(
            user=user,
            business_name=business_name,
            bio='',
            location='',
            timezone='UTC',
            is_verified=False
        )
        print(f"✓ Created trainer profile for {email}")
        print(f"  Business Name: {trainer.business_name}")
        return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python create_trainer_profile.py <email> [business_name]")
        print("\nExample:")
        print("  python create_trainer_profile.py user@example.com")
        print("  python create_trainer_profile.py user@example.com 'My Fitness Studio'")
        sys.exit(1)
    
    email = sys.argv[1]
    business_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = create_trainer_profile(email, business_name)
    sys.exit(0 if success else 1)

