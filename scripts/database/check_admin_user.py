#!/usr/bin/env python
"""
Check if admin user exists and show its status.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

print("="*70)
print("ADMIN USER STATUS")
print("="*70)

# Check for admin user
admin_emails = ['admin@trainerhub.app', 'admin@example.com']
admin_usernames = ['admin', 'superuser']

found_admins = []

# Search by email
for email in admin_emails:
    users = User.objects.filter(email=email)
    for user in users:
        found_admins.append(user)

# Search by username
for username in admin_usernames:
    users = User.objects.filter(username=username)
    for user in users:
        if user not in found_admins:
            found_admins.append(user)

if not found_admins:
    print("\n❌ No admin users found!")
    print("\nCreate one with:")
    print("  python manage.py createsuperuser")
else:
    print(f"\n✓ Found {len(found_admins)} admin user(s):\n")
    
    for user in found_admins:
        print("-"*70)
        print(f"ID:           {user.id}")
        print(f"Username:     {user.username}")
        print(f"Email:        {user.email}")
        print(f"First Name:   {user.first_name or '(not set)'}")
        print(f"Last Name:    {user.last_name or '(not set)'}")
        print(f"Is Active:    {user.is_active}")
        print(f"Is Staff:     {user.is_staff}")
        print(f"Is Superuser: {user.is_superuser}")
        print(f"Created:      {user.created_at if hasattr(user, 'created_at') else 'N/A'}")
        
        if not user.is_superuser:
            print("\n⚠️  This user is NOT a superuser!")
            print("   Upgrading to superuser...")
            user.is_superuser = True
            user.is_staff = True
            user.save()
            print("   ✓ User upgraded to superuser")

print("\n" + "="*70)
print("LOGIN CREDENTIALS")
print("="*70)

if found_admins:
    user = found_admins[0]
    print(f"\nEmail:    {user.email}")
    print(f"Username: {user.username}")
    print(f"Password: [You need to know this or reset it]")
    
    reset = input("\nDo you want to reset the password to 'admin123456'? (y/n): ")
    if reset.lower() == 'y':
        user.set_password('admin123456')
        user.save()
        print("\n✅ Password reset successfully!")
        print("\n" + "="*70)
        print("NEW LOGIN CREDENTIALS")
        print("="*70)
        print(f"Email:    {user.email}")
        print(f"Password: admin123456")
        print("\n⚠️  Change this password after first login!")
    else:
        print("\nPassword not changed. Use your existing password.")

print("\n" + "="*70)
print("NEXT STEPS")
print("="*70)
print("1. Start server: python manage.py runserver")
print("2. Test login:")
print(f"   curl -X POST http://localhost:8000/api/auth/login/ \\")
print(f"     -H 'Content-Type: application/json' \\")
print(f"     -d '{{\"email\":\"{found_admins[0].email if found_admins else 'admin@trainerhub.app'}\",\"password\":\"admin123456\"}}'")
print("3. Or run: python test_admin_panel.py")
print("="*70)

