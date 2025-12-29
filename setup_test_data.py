#!/usr/bin/env python3
"""
Setup test data for TrainerHub
Creates a test user with trainer profile and availability
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.trainers.models import Trainer
from apps.availability.models import AvailabilitySlot, TrainerBreak
from datetime import time, datetime, timedelta

User = get_user_model()

def create_test_data():
    print("Setting up test data for TrainerHub...\n")
    
    # Create or get test user
    email = "trainer@test.com"
    password = "trainer123"
    
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            'username': 'trainer_test',
            'first_name': 'Test',
            'last_name': 'Trainer',
            'is_trainer': True,
            'is_active': True
        }
    )
    
    if created:
        user.set_password(password)
        user.save()
        print(f"✓ Created test user: {email}")
    else:
        print(f"✓ Test user already exists: {email}")
    
    print(f"  Email: {email}")
    print(f"  Password: {password}")
    print(f"  User ID: {user.id}\n")
    
    # Create or get trainer profile
    trainer, created = Trainer.objects.get_or_create(
        user=user,
        defaults={
            'business_name': 'Test Fitness Studio',
            'bio': 'Professional fitness trainer with 10+ years of experience',
            'expertise': ['strength training', 'cardio', 'nutrition'],
            'location': 'New York, NY',
            'timezone': 'America/New_York',
            'is_verified': True
        }
    )
    
    if created:
        print(f"✓ Created trainer profile: {trainer.business_name}")
    else:
        print(f"✓ Trainer profile already exists: {trainer.business_name}")
    
    print(f"  Trainer ID: {trainer.id}")
    print(f"  Business: {trainer.business_name}\n")
    
    # Create availability slots (Monday to Friday, 9am-5pm)
    days = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday')
    ]
    
    created_slots = 0
    for day_num, day_name in days:
        slot, created = AvailabilitySlot.objects.get_or_create(
            trainer=trainer,
            day_of_week=day_num,
            start_time=time(9, 0),
            end_time=time(17, 0),
            defaults={
                'is_recurring': True,
                'is_active': True
            }
        )
        
        if created:
            created_slots += 1
            print(f"  ✓ Created availability slot: {day_name} 9:00-17:00")
    
    if created_slots > 0:
        print(f"\n✓ Created {created_slots} availability slots")
    else:
        print(f"\n✓ Availability slots already exist")
    
    # Create a sample break (vacation)
    start_date = datetime.now() + timedelta(days=60)
    end_date = start_date + timedelta(days=7)
    
    break_obj, created = TrainerBreak.objects.get_or_create(
        trainer=trainer,
        start_date=start_date,
        end_date=end_date,
        defaults={
            'reason': 'Summer vacation'
        }
    )
    
    if created:
        print(f"✓ Created trainer break: {start_date.date()} to {end_date.date()}")
    else:
        print(f"✓ Trainer break already exists")
    
    print("\n" + "="*60)
    print("Test Data Setup Complete!")
    print("="*60)
    print(f"\nYou can now login with:")
    print(f"  Email: {email}")
    print(f"  Password: {password}")
    print(f"\nAPI Token can be obtained via:")
    print(f"  POST {os.getenv('BASE_URL', 'http://localhost:8000')}/api/users/login/")
    print()

if __name__ == '__main__':
    try:
        create_test_data()
    except Exception as e:
        print(f"\n✗ Error setting up test data: {str(e)}")
        import traceback
        traceback.print_exc()

