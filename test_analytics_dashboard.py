#!/usr/bin/env python
"""
Test script for Epic 0.4: Platform Analytics Dashboard
Tests all analytics endpoints to ensure they're working correctly.
"""
import os
import sys
import django
import requests
import json
from datetime import datetime

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/admin"

# Test credentials (use existing superuser)
ADMIN_EMAIL = "admin@trainerhubb.app"
ADMIN_PASSWORD = "admin123"

def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def print_result(test_name, success, data=None, error=None):
    """Print test result."""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} - {test_name}")
    if data:
        print(f"   Data: {json.dumps(data, indent=2)[:200]}...")
    if error:
        print(f"   Error: {error}")
    print()

def login():
    """Login and get auth token."""
    print_section("Authentication")
    
    response = requests.post(
        f"{BASE_URL}/api/users/login/",
        json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('token')
        print_result("Admin Login", True, {"token": token[:20] + "..."})
        return token
    else:
        print_result("Admin Login", False, error=response.text)
        return None

def test_platform_stats(token):
    """Test platform statistics endpoint."""
    print_section("Platform Statistics")
    
    headers = {"Authorization": f"Token {token}"}
    response = requests.get(f"{API_BASE}/dashboard/stats/", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print_result("Get Platform Stats", True, data)
        return True
    else:
        print_result("Get Platform Stats", False, error=response.text)
        return False

def test_analytics_dashboard(token):
    """Test complete analytics dashboard endpoint."""
    print_section("Analytics Dashboard")
    
    headers = {"Authorization": f"Token {token}"}
    
    # Test with default parameters
    response = requests.get(f"{API_BASE}/dashboard/analytics/", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print_result("Get Analytics Dashboard (30 days)", True, {
            "revenue_trends_count": len(data.get('revenue_trends', [])),
            "signup_trends_count": len(data.get('signup_trends', [])),
            "active_users_trends_count": len(data.get('active_users_trends', [])),
            "geographic_distribution_count": len(data.get('geographic_distribution', [])),
            "booking_trends_count": len(data.get('booking_trends', [])),
            "client_growth_trends_count": len(data.get('client_growth_trends', [])),
            "top_performing_trainers_count": len(data.get('top_performing_trainers', []))
        })
    else:
        print_result("Get Analytics Dashboard", False, error=response.text)
        return False
    
    # Test with custom parameters
    response = requests.get(
        f"{API_BASE}/dashboard/analytics/?days=90&group_by=month",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print_result("Get Analytics Dashboard (90 days, monthly)", True, {
            "revenue_trends_count": len(data.get('revenue_trends', [])),
            "signup_trends_count": len(data.get('signup_trends', []))
        })
    else:
        print_result("Get Analytics Dashboard (custom params)", False, error=response.text)
        return False
    
    return True

def test_revenue_trends(token):
    """Test revenue trends endpoint."""
    print_section("Revenue Trends")
    
    headers = {"Authorization": f"Token {token}"}
    
    # Test daily trends
    response = requests.get(
        f"{API_BASE}/dashboard/revenue-trends/?days=30&group_by=day",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print_result("Get Revenue Trends (daily)", True, {
            "count": len(data),
            "sample": data[:2] if data else []
        })
    else:
        print_result("Get Revenue Trends (daily)", False, error=response.text)
        return False
    
    # Test monthly trends
    response = requests.get(
        f"{API_BASE}/dashboard/revenue-trends/?days=365&group_by=month",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print_result("Get Revenue Trends (monthly)", True, {
            "count": len(data)
        })
    else:
        print_result("Get Revenue Trends (monthly)", False, error=response.text)
        return False
    
    return True

def test_signup_trends(token):
    """Test signup trends endpoint."""
    print_section("Signup Trends")
    
    headers = {"Authorization": f"Token {token}"}
    response = requests.get(
        f"{API_BASE}/dashboard/signup-trends/?days=30",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print_result("Get Signup Trends", True, {
            "count": len(data),
            "sample": data[:2] if data else []
        })
        return True
    else:
        print_result("Get Signup Trends", False, error=response.text)
        return False

def test_active_users_trends(token):
    """Test active users trends endpoint."""
    print_section("Active Users Trends")
    
    headers = {"Authorization": f"Token {token}"}
    response = requests.get(
        f"{API_BASE}/dashboard/active-users-trends/?days=30",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print_result("Get Active Users Trends", True, {
            "count": len(data),
            "sample": data[:2] if data else []
        })
        return True
    else:
        print_result("Get Active Users Trends", False, error=response.text)
        return False

def test_geographic_distribution(token):
    """Test geographic distribution endpoint."""
    print_section("Geographic Distribution")
    
    headers = {"Authorization": f"Token {token}"}
    response = requests.get(
        f"{API_BASE}/dashboard/geographic-distribution/",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print_result("Get Geographic Distribution", True, {
            "count": len(data),
            "sample": data[:3] if data else []
        })
        return True
    else:
        print_result("Get Geographic Distribution", False, error=response.text)
        return False

def test_booking_trends(token):
    """Test booking trends endpoint."""
    print_section("Booking Trends")
    
    headers = {"Authorization": f"Token {token}"}
    response = requests.get(
        f"{API_BASE}/dashboard/booking-trends/?days=30",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print_result("Get Booking Trends", True, {
            "count": len(data),
            "sample": data[:2] if data else []
        })
        return True
    else:
        print_result("Get Booking Trends", False, error=response.text)
        return False

def test_client_growth_trends(token):
    """Test client growth trends endpoint."""
    print_section("Client Growth Trends")
    
    headers = {"Authorization": f"Token {token}"}
    response = requests.get(
        f"{API_BASE}/dashboard/client-growth-trends/?days=30",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print_result("Get Client Growth Trends", True, {
            "count": len(data),
            "sample": data[:2] if data else []
        })
        return True
    else:
        print_result("Get Client Growth Trends", False, error=response.text)
        return False

def test_top_performing_trainers(token):
    """Test top performing trainers endpoint."""
    print_section("Top Performing Trainers")
    
    headers = {"Authorization": f"Token {token}"}
    
    # Test with default limit
    response = requests.get(
        f"{API_BASE}/dashboard/top-performing-trainers/",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print_result("Get Top Performing Trainers (default)", True, {
            "count": len(data),
            "sample": data[:2] if data else []
        })
    else:
        print_result("Get Top Performing Trainers", False, error=response.text)
        return False
    
    # Test with custom limit
    response = requests.get(
        f"{API_BASE}/dashboard/top-performing-trainers/?limit=5",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print_result("Get Top Performing Trainers (limit=5)", True, {
            "count": len(data)
        })
    else:
        print_result("Get Top Performing Trainers (custom limit)", False, error=response.text)
        return False
    
    return True

def test_export_stats(token):
    """Test export statistics endpoint."""
    print_section("Export Statistics")
    
    headers = {"Authorization": f"Token {token}"}
    response = requests.get(
        f"{API_BASE}/dashboard/export-stats/",
        headers=headers
    )
    
    if response.status_code == 200:
        # Should return CSV file
        content_type = response.headers.get('Content-Type', '')
        is_csv = 'csv' in content_type or 'text/csv' in content_type
        print_result("Export Platform Stats to CSV", is_csv, {
            "content_type": content_type,
            "content_length": len(response.content)
        })
        return is_csv
    else:
        print_result("Export Platform Stats", False, error=response.text)
        return False

def main():
    """Run all analytics tests."""
    print("\n" + "="*60)
    print("  EPIC 0.4: PLATFORM ANALYTICS DASHBOARD TEST SUITE")
    print("="*60)
    print(f"\nTesting against: {BASE_URL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Login
    token = login()
    if not token:
        print("\n❌ Authentication failed. Cannot proceed with tests.")
        return
    
    # Run all tests
    results = []
    results.append(("Platform Stats", test_platform_stats(token)))
    results.append(("Analytics Dashboard", test_analytics_dashboard(token)))
    results.append(("Revenue Trends", test_revenue_trends(token)))
    results.append(("Signup Trends", test_signup_trends(token)))
    results.append(("Active Users Trends", test_active_users_trends(token)))
    results.append(("Geographic Distribution", test_geographic_distribution(token)))
    results.append(("Booking Trends", test_booking_trends(token)))
    results.append(("Client Growth Trends", test_client_growth_trends(token)))
    results.append(("Top Performing Trainers", test_top_performing_trainers(token)))
    results.append(("Export Stats", test_export_stats(token)))
    
    # Summary
    print_section("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%\n")
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    print("\n" + "="*60)
    if passed == total:
        print("  🎉 ALL TESTS PASSED!")
        print("  Epic 0.4: Platform Analytics Dashboard is complete!")
    else:
        print("  ⚠️  SOME TESTS FAILED")
        print("  Please review the errors above.")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
