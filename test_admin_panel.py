#!/usr/bin/env python
"""
Test script for Admin Panel API endpoints
Run with: python test_admin_panel.py
"""
import requests
import json
from getpass import getpass

# Configuration
BASE_URL = "http://localhost:8000/api"
ADMIN_EMAIL = input("Enter super admin email: ")
ADMIN_PASSWORD = getpass("Enter super admin password: ")

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}Testing: {name}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_response(data):
    print(json.dumps(data, indent=2))

# 1. Login as admin
print_test("Admin Login")
try:
    response = requests.post(f"{BASE_URL}/auth/login/", json={
        'email': ADMIN_EMAIL,
        'password': ADMIN_PASSWORD
    })
    response.raise_for_status()
    token = response.json().get('token') or response.json().get('access')
    headers = {'Authorization': f'Token {token}'}
    print_success("Login successful!")
    print(f"Token: {token[:20]}...")
except Exception as e:
    print_error(f"Login failed: {e}")
    exit(1)

# 2. Get platform stats
print_test("Platform Statistics")
try:
    response = requests.get(f"{BASE_URL}/admin/dashboard/stats/", headers=headers)
    response.raise_for_status()
    stats = response.json()
    print_success("Stats retrieved successfully!")
    print_response(stats)
except Exception as e:
    print_error(f"Failed to get stats: {e}")

# 3. List trainers
print_test("List All Trainers")
try:
    response = requests.get(f"{BASE_URL}/admin/trainers/", headers=headers)
    response.raise_for_status()
    trainers = response.json()
    print_success(f"Found {trainers.get('count', 0)} trainers")
    if trainers.get('results'):
        print("First trainer:")
        print_response(trainers['results'][0])
except Exception as e:
    print_error(f"Failed to list trainers: {e}")

# 4. Search trainers
print_test("Search Trainers")
search_term = input("Enter search term (or press Enter to skip): ")
if search_term:
    try:
        response = requests.get(
            f"{BASE_URL}/admin/trainers/",
            params={'search': search_term},
            headers=headers
        )
        response.raise_for_status()
        results = response.json()
        print_success(f"Found {results.get('count', 0)} matching trainers")
        print_response(results)
    except Exception as e:
        print_error(f"Search failed: {e}")

# 5. Get trainer detail
print_test("Get Trainer Detail")
trainer_id = input("Enter trainer ID to view (or press Enter to skip): ")
if trainer_id:
    try:
        response = requests.get(f"{BASE_URL}/admin/trainers/{trainer_id}/", headers=headers)
        response.raise_for_status()
        trainer = response.json()
        print_success("Trainer details retrieved!")
        print_response(trainer)
    except Exception as e:
        print_error(f"Failed to get trainer: {e}")

# 6. View action logs
print_test("Admin Action Logs")
try:
    response = requests.get(f"{BASE_URL}/admin/logs/", headers=headers)
    response.raise_for_status()
    logs = response.json()
    print_success(f"Found {logs.get('count', 0)} action logs")
    if logs.get('results'):
        print("Recent actions:")
        for log in logs['results'][:5]:
            print(f"  - {log['admin_email']} {log['action_display']} on {log.get('trainer_name', 'N/A')}")
except Exception as e:
    print_error(f"Failed to get logs: {e}")

# 7. Test impersonation (optional)
print_test("Test Impersonation (Optional)")
test_impersonate = input("Do you want to test impersonation? (y/n): ")
if test_impersonate.lower() == 'y':
    trainer_id = input("Enter trainer ID to impersonate: ")
    reason = input("Enter reason: ")
    try:
        response = requests.post(
            f"{BASE_URL}/admin/trainers/{trainer_id}/impersonate/",
            json={'trainer_id': int(trainer_id), 'reason': reason},
            headers=headers
        )
        response.raise_for_status()
        impersonate_data = response.json()
        print_success("Impersonation successful!")
        print_response(impersonate_data)
        print(f"\n{Colors.YELLOW}Use this token to access trainer dashboard:{Colors.END}")
        print(f"{Colors.YELLOW}{impersonate_data['token']}{Colors.END}")
    except Exception as e:
        print_error(f"Impersonation failed: {e}")

print(f"\n{Colors.GREEN}{'='*60}{Colors.END}")
print(f"{Colors.GREEN}Admin Panel Tests Complete!{Colors.END}")
print(f"{Colors.GREEN}{'='*60}{Colors.END}")

