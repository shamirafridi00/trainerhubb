#!/usr/bin/env python
"""
Test script for Domain Management (Epic 0.3)
Tests DNS verification, SSL provisioning, and admin workflows.
"""
import requests
import json
from getpass import getpass

# Configuration
BASE_URL = "http://localhost:8000/api"
ADMIN_EMAIL = input("Enter super admin email (default: admin@trainerhubb.com): ") or "admin@trainerhubb.com"
ADMIN_PASSWORD = getpass("Enter super admin password: ")

# Colors
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

# 1. Login
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

# 2. List all domains
print_test("List All Custom Domains")
try:
    response = requests.get(f"{BASE_URL}/admin/domains/", headers=headers)
    response.raise_for_status()
    domains = response.json()
    
    if 'results' in domains:
        domain_list = domains['results']
        count = domains.get('count', len(domain_list))
    else:
        domain_list = domains
        count = len(domain_list)
    
    print_success(f"Found {count} custom domain(s)")
    
    if domain_list:
        print("\nDomains:")
        for domain in domain_list[:5]:
            print(f"  - {domain['domain']} (Status: {domain['status']})")
            if domain['trainer_name']:
                print(f"    Trainer: {domain['trainer_name']}")
            if domain['dns_verified_at']:
                print(f"    DNS Verified: ✓")
            if domain['ssl_status'] == 'provisioned':
                print(f"    SSL: ✓ (Expires: {domain['ssl_expires_at']})")
    else:
        print_info("No custom domains yet")
        
except Exception as e:
    print_error(f"Failed to list domains: {e}")

# 3. Get pending domains
print_test("Get Pending Domain Requests")
try:
    response = requests.get(f"{BASE_URL}/admin/domains/pending/", headers=headers)
    response.raise_for_status()
    result = response.json()
    
    print_success(f"Found {result['count']} pending domain(s)")
    
    if result['results']:
        print("\nPending domains:")
        for domain in result['results']:
            print(f"  - {domain['domain']}")
            print(f"    Trainer: {domain['trainer_name']}")
            print(f"    Requested: {domain['created_at']}")
            print(f"    Verification method: {domain['verification_method']}")
except Exception as e:
    print_error(f"Failed to get pending domains: {e}")

# 4. Get domains needing SSL renewal
print_test("Get Domains Needing SSL Renewal")
try:
    response = requests.get(f"{BASE_URL}/admin/domains/needs-ssl-renewal/", headers=headers)
    response.raise_for_status()
    result = response.json()
    
    print_success(f"Found {result['count']} domain(s) needing renewal")
    
    if result['results']:
        print("\nDomains needing renewal:")
        for domain in result['results']:
            print(f"  - {domain['domain']}")
            print(f"    Expires: {domain['ssl_expires_at']}")
except Exception as e:
    print_error(f"Failed to get domains needing renewal: {e}")

# 5. Test domain verification (if domains exist)
print_test("Test Domain Verification")
test_verify = input("\nDo you want to test domain verification? (y/n): ")
if test_verify.lower() == 'y':
    domain_id = input("Enter domain ID to verify: ")
    if domain_id:
        try:
            response = requests.post(
                f"{BASE_URL}/admin/domains/{domain_id}/verify/",
                json={'force': True},
                headers=headers
            )
            
            result = response.json()
            
            if response.status_code == 200:
                print_success(f"Verification successful!")
                print_info(f"Status: {result.get('status')}")
                print_info(f"Message: {result.get('message')}")
                if result.get('next_step'):
                    print_info(f"Next step: {result['next_step']}")
            else:
                print_error(f"Verification failed")
                print_info(f"Message: {result.get('message')}")
                print_info(f"Attempts: {result.get('attempts')}")
        except Exception as e:
            print_error(f"Verification request failed: {e}")

# 6. Test SSL provisioning
print_test("Test SSL Provisioning")
test_ssl = input("\nDo you want to test SSL provisioning? (y/n): ")
if test_ssl.lower() == 'y':
    domain_id = input("Enter domain ID for SSL provisioning: ")
    if domain_id:
        try:
            response = requests.post(
                f"{BASE_URL}/admin/domains/{domain_id}/provision-ssl/",
                headers=headers
            )
            
            result = response.json()
            
            if response.status_code == 200:
                print_success(f"SSL provisioning successful!")
                print_info(f"Status: {result.get('status')}")
                print_info(f"Message: {result.get('message')}")
                if result.get('ssl_expires_at'):
                    print_info(f"Expires: {result['ssl_expires_at']}")
            else:
                print_error(f"SSL provisioning failed")
                print_info(f"Error: {result.get('error') or result.get('message')}")
        except Exception as e:
            print_error(f"SSL provisioning request failed: {e}")

# 7. Test domain approval/rejection
print_test("Test Domain Approval/Rejection")
test_approval = input("\nDo you want to test domain approval/rejection? (y/n): ")
if test_approval.lower() == 'y':
    domain_id = input("Enter domain ID: ")
    action = input("Enter action (approve/reject): ")
    reason = input("Enter reason (optional for reject): ")
    
    if domain_id and action in ['approve', 'reject']:
        try:
            response = requests.post(
                f"{BASE_URL}/admin/domains/{domain_id}/approve-reject/",
                json={
                    'action': action,
                    'reason': reason
                },
                headers=headers
            )
            response.raise_for_status()
            result = response.json()
            
            print_success(f"Domain {action}d!")
            print_info(f"Message: {result.get('message')}")
        except Exception as e:
            print_error(f"Approval/rejection failed: {e}")

# 8. View domain verification logs
print_test("View Domain Verification Logs")
test_logs = input("\nDo you want to view verification logs? (y/n): ")
if test_logs.lower() == 'y':
    domain_id = input("Enter domain ID (or press Enter for all): ")
    
    try:
        url = f"{BASE_URL}/admin/domain-logs/"
        params = {}
        if domain_id:
            params['domain_id'] = domain_id
        
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        logs = response.json()
        
        if 'results' in logs:
            log_list = logs['results']
        else:
            log_list = logs
        
        print_success(f"Found {len(log_list)} log(s)")
        
        if log_list:
            print("\nVerification Logs:")
            for log in log_list[:10]:
                print(f"\n  - Domain: {log['domain_name']}")
                print(f"    Type: {log['verification_type']}")
                print(f"    Status: {log['status']}")
                print(f"    Time: {log['created_at']}")
                if log.get('error_message'):
                    print(f"    Error: {log['error_message']}")
    except Exception as e:
        print_error(f"Failed to get logs: {e}")

print(f"\n{Colors.GREEN}{'='*70}{Colors.END}")
print(f"{Colors.GREEN}Domain Management Tests Complete!{Colors.END}")
print(f"{Colors.GREEN}{'='*70}{Colors.END}")

print("\nEndpoint Summary:")
print("  GET    /api/admin/domains/                    - List all domains")
print("  GET    /api/admin/domains/pending/            - Pending requests")
print("  GET    /api/admin/domains/needs-ssl-renewal/  - Expiring SSL")
print("  POST   /api/admin/domains/{id}/verify/        - Verify DNS")
print("  POST   /api/admin/domains/{id}/provision-ssl/ - Provision SSL")
print("  POST   /api/admin/domains/{id}/approve-reject/ - Approve/Reject")
print("  GET    /api/admin/domain-logs/                - Verification logs")

