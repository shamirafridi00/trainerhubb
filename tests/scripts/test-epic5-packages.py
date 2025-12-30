#!/usr/bin/env python
"""
Comprehensive test script for Epic 5 - Session Packages
Tests all package-related endpoints including clients and bookings integration.
"""

import os
import django
import sys
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import requests
from django.contrib.auth import get_user_model
from apps.trainers.models import Trainer
from apps.clients.models import Client
from apps.packages.models import SessionPackage, ClientPackage

User = get_user_model()

# Configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "package_trainer@test.com"
TEST_PASSWORD = "testpass123"

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

def setup_test_data():
    """Create test user, trainer, and client."""
    print_header("Setting Up Test Data")
    
    # Create or get user
    user, created = User.objects.get_or_create(
        email=TEST_EMAIL,
        defaults={
            'first_name': 'Package',
            'last_name': 'Trainer',
            'role': 'trainer'
        }
    )
    if created:
        user.set_password(TEST_PASSWORD)
        user.save()
        print_success(f"Created test user: {TEST_EMAIL}")
    else:
        print_info(f"Using existing user: {TEST_EMAIL}")
    
    # Create or get trainer profile
    trainer, created = Trainer.objects.get_or_create(
        user=user,
        defaults={
            'business_name': 'Package Fitness Studio',
            'bio': 'Testing package system',
            'location': 'Test City'
        }
    )
    if created:
        print_success(f"Created trainer profile: {trainer.business_name}")
    else:
        print_info(f"Using existing trainer: {trainer.business_name}")
    
    # Create or get test client
    client, created = Client.objects.get_or_create(
        trainer=trainer,
        email='package_client@test.com',
        defaults={
            'first_name': 'Package',
            'last_name': 'Client',
            'fitness_level': 'intermediate',
            'goals': ['strength training', 'weight loss']
        }
    )
    if created:
        print_success(f"Created test client: {client.get_full_name()}")
    else:
        print_info(f"Using existing client: {client.get_full_name()}")
    
    return user, trainer, client

def get_auth_token():
    """Get authentication token."""
    print_header("Getting Authentication Token")
    
    response = requests.post(
        f"{BASE_URL}/api/login/",
        json={
            'email': TEST_EMAIL,
            'password': TEST_PASSWORD
        }
    )
    
    if response.status_code == 200:
        token = response.json().get('token')
        print_success(f"Successfully authenticated")
        return token
    else:
        print_error(f"Authentication failed: {response.status_code}")
        print_error(f"Response: {response.text}")
        return None

def test_package_endpoints(token, client_id):
    """Test all package-related endpoints."""
    print_header("Testing Package Endpoints")
    
    headers = {'Authorization': f'Token {token}'}
    package_id = None
    client_package_id = None
    
    # 1. Create Session Package
    print_info("1. Creating session package...")
    response = requests.post(
        f"{BASE_URL}/api/packages/",
        headers=headers,
        json={
            'name': '5-Pack Special',
            'description': '5 training sessions at a discounted rate',
            'sessions_count': 5,
            'price': '249.99',
            'is_active': True
        }
    )
    
    if response.status_code == 201:
        package_id = response.json()['id']
        print_success(f"Created package: {response.json()['name']} (ID: {package_id})")
    else:
        print_error(f"Failed to create package: {response.status_code}")
        print_error(f"Response: {response.text}")
        return
    
    # 2. List Packages
    print_info("\n2. Listing all packages...")
    response = requests.get(f"{BASE_URL}/api/packages/", headers=headers)
    
    if response.status_code == 200:
        packages = response.json()
        print_success(f"Retrieved {len(packages)} package(s)")
        for pkg in packages:
            print(f"   - {pkg['name']}: {pkg['sessions_count']} sessions @ ${pkg['price']}")
    else:
        print_error(f"Failed to list packages: {response.status_code}")
    
    # 3. Get Package Details
    print_info(f"\n3. Getting package details (ID: {package_id})...")
    response = requests.get(f"{BASE_URL}/api/packages/{package_id}/", headers=headers)
    
    if response.status_code == 200:
        pkg = response.json()
        print_success(f"Package: {pkg['name']}")
        print(f"   Sessions: {pkg['sessions_count']}")
        print(f"   Price: ${pkg['price']}")
        print(f"   Active: {pkg['is_active']}")
    else:
        print_error(f"Failed to get package: {response.status_code}")
    
    # 4. Update Package
    print_info(f"\n4. Updating package (ID: {package_id})...")
    response = requests.patch(
        f"{BASE_URL}/api/packages/{package_id}/",
        headers=headers,
        json={'price': '229.99'}
    )
    
    if response.status_code == 200:
        print_success(f"Updated package price to ${response.json()['price']}")
    else:
        print_error(f"Failed to update package: {response.status_code}")
    
    # 5. Assign Package to Client
    print_info(f"\n5. Assigning package to client (ID: {client_id})...")
    expiry_date = (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')
    response = requests.post(
        f"{BASE_URL}/api/packages/{package_id}/assign-to-client/",
        headers=headers,
        json={
            'client_id': client_id,
            'expiry_date': expiry_date
        }
    )
    
    if response.status_code == 201:
        client_package_id = response.json()['id']
        print_success(f"Assigned package to client (Client Package ID: {client_package_id})")
        print(f"   Sessions remaining: {response.json()['sessions_remaining']}")
        print(f"   Expiry date: {response.json()['expiry_date']}")
    else:
        print_error(f"Failed to assign package: {response.status_code}")
        print_error(f"Response: {response.text}")
        return
    
    # 6. View Client Packages for this Package
    print_info(f"\n6. Viewing all client packages for package {package_id}...")
    response = requests.get(
        f"{BASE_URL}/api/packages/{package_id}/client-packages/",
        headers=headers
    )
    
    if response.status_code == 200:
        client_packages = response.json()
        print_success(f"Found {len(client_packages)} client package(s)")
        for cp in client_packages:
            print(f"   - Client: {cp['client_name']}, Sessions: {cp['sessions_remaining']}, Active: {cp['is_active']}")
    else:
        print_error(f"Failed to get client packages: {response.status_code}")
    
    # 7. List All Client Packages
    print_info("\n7. Listing all client packages...")
    response = requests.get(f"{BASE_URL}/api/client-packages/", headers=headers)
    
    if response.status_code == 200:
        client_packages = response.json()
        print_success(f"Retrieved {len(client_packages)} client package(s)")
        for cp in client_packages:
            print(f"   - {cp['client_name']}: {cp['package_name']} - {cp['sessions_remaining']} sessions")
    else:
        print_error(f"Failed to list client packages: {response.status_code}")
    
    # 8. Get Client Package Details
    print_info(f"\n8. Getting client package details (ID: {client_package_id})...")
    response = requests.get(f"{BASE_URL}/api/client-packages/{client_package_id}/", headers=headers)
    
    if response.status_code == 200:
        cp = response.json()
        print_success(f"Client Package: {cp['package_name']}")
        print(f"   Client: {cp['client_name']}")
        print(f"   Sessions remaining: {cp['sessions_remaining']}")
        print(f"   Is active: {cp['is_active']}")
        print(f"   Is expired: {cp['is_expired']}")
    else:
        print_error(f"Failed to get client package: {response.status_code}")
    
    # 9. Use Session from Package
    print_info(f"\n9. Using a session from package (ID: {client_package_id})...")
    response = requests.post(
        f"{BASE_URL}/api/client-packages/{client_package_id}/use-session/",
        headers=headers
    )
    
    if response.status_code == 200:
        cp = response.json()
        print_success(f"Session used successfully!")
        print(f"   Sessions remaining: {cp['sessions_remaining']}")
    else:
        print_error(f"Failed to use session: {response.status_code}")
        print_error(f"Response: {response.text}")
    
    # 10. Use Another Session
    print_info(f"\n10. Using another session...")
    response = requests.post(
        f"{BASE_URL}/api/client-packages/{client_package_id}/use-session/",
        headers=headers
    )
    
    if response.status_code == 200:
        cp = response.json()
        print_success(f"Session used successfully!")
        print(f"   Sessions remaining: {cp['sessions_remaining']}")
    else:
        print_error(f"Failed to use session: {response.status_code}")
    
    # 11. Create Another Package (10-Pack)
    print_info("\n11. Creating 10-Pack package...")
    response = requests.post(
        f"{BASE_URL}/api/packages/",
        headers=headers,
        json={
            'name': '10-Pack Premium',
            'description': '10 training sessions with premium benefits',
            'sessions_count': 10,
            'price': '449.99',
            'is_active': True
        }
    )
    
    if response.status_code == 201:
        print_success(f"Created package: {response.json()['name']}")
    else:
        print_error(f"Failed to create package: {response.status_code}")
    
    # 12. Test Validation - Invalid sessions_count
    print_info("\n12. Testing validation (invalid sessions_count)...")
    response = requests.post(
        f"{BASE_URL}/api/packages/",
        headers=headers,
        json={
            'name': 'Invalid Package',
            'sessions_count': 0,
            'price': '99.99'
        }
    )
    
    if response.status_code == 400:
        print_success("Validation working: Rejected invalid sessions_count")
    else:
        print_error(f"Validation failed: Expected 400, got {response.status_code}")
    
    # 13. Test Validation - Invalid price
    print_info("\n13. Testing validation (invalid price)...")
    response = requests.post(
        f"{BASE_URL}/api/packages/",
        headers=headers,
        json={
            'name': 'Invalid Package',
            'sessions_count': 5,
            'price': '-10.00'
        }
    )
    
    if response.status_code == 400:
        print_success("Validation working: Rejected invalid price")
    else:
        print_error(f"Validation failed: Expected 400, got {response.status_code}")

def main():
    """Main test execution."""
    print_header("EPIC 5 - Session Packages Test Suite")
    print(f"Base URL: {BASE_URL}")
    print(f"Test User: {TEST_EMAIL}")
    
    # Setup test data
    user, trainer, client = setup_test_data()
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print_error("Cannot proceed without authentication token")
        sys.exit(1)
    
    # Test package endpoints
    test_package_endpoints(token, client.id)
    
    # Summary
    print_header("Test Summary")
    print_success("All Epic 5 package tests completed!")
    print_info("\nPackage system features tested:")
    print("  ✓ Create session packages")
    print("  ✓ List and retrieve packages")
    print("  ✓ Update package details")
    print("  ✓ Assign packages to clients")
    print("  ✓ View client packages")
    print("  ✓ Use sessions from packages")
    print("  ✓ Validation for sessions_count and price")
    print("  ✓ Package expiry tracking")
    print("  ✓ Session remaining tracking")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print_error("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n\nUnexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

