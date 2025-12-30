#!/usr/bin/env python
"""
Test script for Enhanced Admin Panel Features (Epic 0.2)
Tests bulk actions and export functionality.
"""
import requests
import json
from getpass import getpass

# Configuration
BASE_URL = "http://localhost:8000/api"
ADMIN_EMAIL = input("Enter super admin email (default: admin@trainerhubb.com): ") or "admin@trainerhubb.com"
ADMIN_PASSWORD = getpass("Enter super admin password: ")

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name):
    print(f"\n{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}Testing: {name}{Colors.END}")
    print(f"{Colors.BLUE}{'='*70}{Colors.END}")

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.YELLOW}ℹ {message}{Colors.END}")

# 1. Login as admin
print_test("Admin Login")
try:
    response = requests.post(f"{BASE_URL}/users/login/", json={
        'email': ADMIN_EMAIL,
        'password': ADMIN_PASSWORD
    })
    response.raise_for_status()
    token = response.json().get('token')
    headers = {'Authorization': f'Token {token}'}
    print_success("Login successful!")
except Exception as e:
    print_error(f"Login failed: {e}")
    exit(1)

# 2. Test Export Trainers
print_test("Export Trainers to CSV")
try:
    response = requests.get(f"{BASE_URL}/admin/trainers/export/", headers=headers)
    response.raise_for_status()
    
    # Save to file
    filename = "trainers_export_test.csv"
    with open(filename, 'wb') as f:
        f.write(response.content)
    
    print_success(f"Trainers exported successfully!")
    print_info(f"Saved to: {filename}")
    print_info(f"File size: {len(response.content)} bytes")
except Exception as e:
    print_error(f"Export failed: {e}")

# 3. Test Export Platform Stats
print_test("Export Platform Statistics to CSV")
try:
    response = requests.get(f"{BASE_URL}/admin/dashboard/export-stats/", headers=headers)
    response.raise_for_status()
    
    filename = "platform_stats_export_test.csv"
    with open(filename, 'wb') as f:
        f.write(response.content)
    
    print_success(f"Platform stats exported successfully!")
    print_info(f"Saved to: {filename}")
    print_info(f"File size: {len(response.content)} bytes")
except Exception as e:
    print_error(f"Export failed: {e}")

# 4. Get list of trainers for testing
print_test("Get Trainer List for Bulk Actions")
try:
    response = requests.get(f"{BASE_URL}/admin/trainers/", headers=headers)
    response.raise_for_status()
    trainers = response.json()['results']
    
    if len(trainers) < 1:
        print_error("No trainers found. Create some trainers first.")
        exit(1)
    
    print_success(f"Found {len(trainers)} trainers")
    
    # Show trainers
    for trainer in trainers[:5]:
        status = "Active" if trainer['user_is_active'] else "Suspended"
        verified = "✓" if trainer['is_verified'] else "✗"
        print(f"  - ID: {trainer['id']}, {trainer['business_name']} [{status}] [Verified: {verified}]")
    
except Exception as e:
    print_error(f"Failed to get trainers: {e}")
    exit(1)

# 5. Test Bulk Verify
print_test("Bulk Verify Trainers")
test_bulk_verify = input("\nDo you want to test bulk verify? (y/n): ")
if test_bulk_verify.lower() == 'y':
    # Get trainer IDs to verify
    trainer_ids_input = input("Enter trainer IDs to verify (comma-separated): ")
    if trainer_ids_input:
        trainer_ids = [int(id.strip()) for id in trainer_ids_input.split(',')]
        
        try:
            response = requests.post(
                f"{BASE_URL}/admin/trainers/bulk-action/",
                json={
                    'action': 'verify',
                    'trainer_ids': trainer_ids
                },
                headers=headers
            )
            response.raise_for_status()
            result = response.json()
            
            print_success(f"Bulk verify completed!")
            print_info(f"Successfully verified: {result['success_count']}")
            if result['failed_count'] > 0:
                print_error(f"Failed: {result['failed_count']}")
                for failed in result['failed']:
                    print(f"  - {failed['business_name']}: {failed['reason']}")
        except Exception as e:
            print_error(f"Bulk verify failed: {e}")

# 6. Test Bulk Suspend/Activate
print_test("Bulk Suspend/Activate Trainers")
test_bulk_suspend = input("\nDo you want to test bulk suspend/activate? (y/n): ")
if test_bulk_suspend.lower() == 'y':
    action = input("Enter action (suspend/activate): ")
    trainer_ids_input = input("Enter trainer IDs (comma-separated): ")
    reason = input("Enter reason: ")
    
    if trainer_ids_input and action in ['suspend', 'activate']:
        trainer_ids = [int(id.strip()) for id in trainer_ids_input.split(',')]
        
        try:
            response = requests.post(
                f"{BASE_URL}/admin/trainers/bulk-action/",
                json={
                    'action': action,
                    'trainer_ids': trainer_ids,
                    'reason': reason
                },
                headers=headers
            )
            response.raise_for_status()
            result = response.json()
            
            print_success(f"Bulk {action} completed!")
            print_info(f"Successfully {action}d: {result['success_count']}")
            if result['failed_count'] > 0:
                print_error(f"Failed: {result['failed_count']}")
                for failed in result['failed']:
                    print(f"  - {failed['business_name']}: {failed['reason']}")
        except Exception as e:
            print_error(f"Bulk {action} failed: {e}")

# 7. Test Export Trainer Detail
print_test("Export Single Trainer Detail")
test_export_detail = input("\nDo you want to export a trainer's details? (y/n): ")
if test_export_detail.lower() == 'y':
    trainer_id = input("Enter trainer ID: ")
    if trainer_id:
        try:
            response = requests.get(
                f"{BASE_URL}/admin/trainers/{trainer_id}/export-detail/",
                headers=headers
            )
            response.raise_for_status()
            
            filename = f"trainer_{trainer_id}_detail_export_test.csv"
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            print_success(f"Trainer detail exported successfully!")
            print_info(f"Saved to: {filename}")
            print_info(f"File size: {len(response.content)} bytes")
        except Exception as e:
            print_error(f"Export failed: {e}")

# 8. Test Export with Filters
print_test("Export with Filters")
test_filtered_export = input("\nDo you want to test filtered export? (y/n): ")
if test_filtered_export.lower() == 'y':
    search_term = input("Enter search term (or press Enter to skip): ")
    is_active = input("Filter by active status? (true/false or press Enter to skip): ")
    
    params = {}
    if search_term:
        params['search'] = search_term
    if is_active:
        params['is_active'] = is_active
    
    try:
        response = requests.get(
            f"{BASE_URL}/admin/trainers/export/",
            params=params,
            headers=headers
        )
        response.raise_for_status()
        
        filename = "trainers_filtered_export_test.csv"
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        print_success(f"Filtered export completed!")
        print_info(f"Saved to: {filename}")
        print_info(f"Filters applied: {params}")
    except Exception as e:
        print_error(f"Filtered export failed: {e}")

print(f"\n{Colors.GREEN}{'='*70}{Colors.END}")
print(f"{Colors.GREEN}Enhanced Admin Panel Tests Complete!{Colors.END}")
print(f"{Colors.GREEN}{'='*70}{Colors.END}")
print("\nExported files (if any) are in the current directory.")
print("Check the CSV files to verify the exports worked correctly.")

