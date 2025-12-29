#!/usr/bin/env python3
"""
TrainerHub - Availability API Test Script
Tests all Epic 2 endpoints
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

# Colors for terminal output
class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def print_test(test_name):
    print(f"\n{Colors.YELLOW}{'='*50}")
    print(f"Test: {test_name}")
    print(f"{'='*50}{Colors.NC}")

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.NC}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.NC}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ {message}{Colors.NC}")

def main():
    print(f"\n{Colors.BLUE}{'='*60}")
    print("TrainerHub - Availability API Test Suite")
    print(f"{'='*60}{Colors.NC}\n")

    token = None
    user_id = None
    
    # Test 1: Login with existing user
    print_test("1. User Login")
    try:
        response = requests.post(
            f"{BASE_URL}/api/users/login/",
            json={
                "email": "trainer@test.com",
                "password": "trainer123"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            user_id = data.get('id')
            print_success(f"Login successful (User ID: {user_id})")
            print_info(f"Token: {token[:20]}...")
        else:
            print_error(f"Login failed: {response.status_code}")
            print_info("Trying to register new user...")
            
            # Try to register
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            response = requests.post(
                f"{BASE_URL}/api/users/register/",
                json={
                    "email": f"testuser{timestamp}@example.com",
                    "username": f"testuser{timestamp}",
                    "first_name": "Test",
                    "last_name": "User",
                    "password": "testpass123",
                    "password_confirm": "testpass123"
                }
            )
            
            if response.status_code == 201:
                data = response.json()
                token = data.get('token')
                user_id = data.get('id')
                print_success(f"Registration successful (User ID: {user_id})")
            else:
                print_error(f"Registration failed: {response.json()}")
                return
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return

    if not token:
        print_error("No authentication token available. Cannot continue.")
        return

    headers = {"Authorization": f"Token {token}"}

    # Test 2: Get User Profile
    print_test("2. Get Current User Profile")
    try:
        response = requests.get(f"{BASE_URL}/api/users/me/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print_success("User profile retrieved")
            print(json.dumps(data, indent=2))
        else:
            print_error(f"Failed to get profile: {response.status_code}")
    except Exception as e:
        print_error(f"Error: {str(e)}")

    # Test 3: List Availability Slots
    print_test("3. List Availability Slots (for current trainer)")
    try:
        response = requests.get(f"{BASE_URL}/api/availability-slots/", headers=headers)
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print_success(f"Found {len(data)} availability slots")
            else:
                print_success(f"Found {data.get('count', 0)} availability slots")
            print(json.dumps(data, indent=2))
        else:
            print_info(f"Response: {response.text}")
            if "trainer_profile" in response.text.lower():
                print_error("User needs a trainer profile to manage availability")
                print_info("This is expected - availability requires a trainer profile")
            else:
                print_error(f"Request failed: {response.status_code}")
    except Exception as e:
        print_error(f"Error: {str(e)}")

    # Test 4: Create Availability Slot
    print_test("4. Create Availability Slot (Monday 9am-5pm)")
    try:
        response = requests.post(
            f"{BASE_URL}/api/availability-slots/",
            headers=headers,
            json={
                "day_of_week": 0,
                "start_time": "09:00:00",
                "end_time": "17:00:00",
                "is_recurring": True,
                "is_active": True
            }
        )
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print_success(f"Availability slot created (ID: {data.get('id')})")
            print(json.dumps(data, indent=2))
        else:
            print_info(f"Response: {response.text}")
            if "trainer_profile" in response.text.lower():
                print_error("User needs a trainer profile")
                print_info("Create a trainer profile via: http://localhost:8000/admin/")
            else:
                print_error(f"Failed to create slot: {response.status_code}")
    except Exception as e:
        print_error(f"Error: {str(e)}")

    # Test 5: Query Available Slots
    print_test("5. Query Available Slots (for trainer ID 1)")
    try:
        start_date = datetime.now().strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        response = requests.get(
            f"{BASE_URL}/api/availability-slots/available-slots/",
            headers=headers,
            params={
                "trainer_id": 1,
                "start_date": start_date,
                "end_date": end_date,
                "duration": 60
            }
        )
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Available slots retrieved")
            slots_count = sum(len(slots) for slots in data.get('available_slots', {}).values())
            print_info(f"Total available time slots: {slots_count}")
            print(json.dumps(data, indent=2))
        else:
            print_error(f"Failed to query slots: {response.status_code}")
            print_info(f"Response: {response.text}")
    except Exception as e:
        print_error(f"Error: {str(e)}")

    # Test 6: List Trainer Breaks
    print_test("6. List Trainer Breaks")
    try:
        response = requests.get(f"{BASE_URL}/api/breaks/", headers=headers)
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print_success(f"Found {len(data)} breaks")
            else:
                print_success(f"Found {data.get('count', 0)} breaks")
            print(json.dumps(data, indent=2))
        else:
            print_info(f"Response: {response.text}")
    except Exception as e:
        print_error(f"Error: {str(e)}")

    # Test 7: Create Trainer Break
    print_test("7. Create Trainer Break (Vacation)")
    try:
        start_date = (datetime.now() + timedelta(days=30)).isoformat() + "Z"
        end_date = (datetime.now() + timedelta(days=35)).isoformat() + "Z"
        
        response = requests.post(
            f"{BASE_URL}/api/breaks/",
            headers=headers,
            json={
                "start_date": start_date,
                "end_date": end_date,
                "reason": "Holiday vacation"
            }
        )
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print_success(f"Trainer break created (ID: {data.get('id')})")
            print(json.dumps(data, indent=2))
        else:
            print_info(f"Response: {response.text}")
            if "trainer_profile" in response.text.lower():
                print_error("User needs a trainer profile")
            else:
                print_error(f"Failed to create break: {response.status_code}")
    except Exception as e:
        print_error(f"Error: {str(e)}")

    # Summary
    print(f"\n{Colors.BLUE}{'='*60}")
    print("Test Suite Complete!")
    print(f"{'='*60}{Colors.NC}\n")
    
    print_info("Note: Some tests require a trainer profile to be created.")
    print_info("Visit the admin panel to create a trainer profile:")
    print_info(f"  {BASE_URL}/admin/trainers/trainer/add/")
    print("")

if __name__ == "__main__":
    main()

