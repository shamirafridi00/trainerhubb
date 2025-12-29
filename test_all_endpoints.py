#!/usr/bin/env python
"""
Comprehensive test script for all TrainerHub API endpoints.
Tests all Epics: 1-8 (Users, Clients, Bookings, Packages, Payments, Notifications, Analytics)
"""

import os
import django
import sys
import logging
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import requests
from django.contrib.auth import get_user_model
from apps.trainers.models import Trainer
from apps.clients.models import Client
from apps.bookings.models import Booking
from apps.packages.models import SessionPackage, ClientPackage
from apps.payments.models import Subscription, Payment

User = get_user_model()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "test_trainer@trainerhub.com"
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
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")
    logger.info(text)

def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")
    logger.error(text)

def print_info(text):
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")
    logger.info(text)

def print_warning(text):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")
    logger.warning(text)

class EndpointTester:
    """Test all API endpoints."""
    
    def __init__(self, base_url, email, password):
        self.base_url = base_url
        self.email = email
        self.password = password
        self.token = None
        self.headers = {}
        self.test_data = {}
        self.stats = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0
        }
    
    def setup_test_data(self):
        """Create test user, trainer, and client."""
        print_header("Setting Up Test Data")
        
        try:
            # Create or get user
            user, created = User.objects.get_or_create(
                email=self.email,
                defaults={
                    'first_name': 'Test',
                    'last_name': 'Trainer',
                    'role': 'trainer'
                }
            )
            if created:
                user.set_password(self.password)
                user.save()
                print_success(f"Created test user: {self.email}")
            else:
                print_info(f"Using existing user: {self.email}")
            
            # Create or get trainer profile
            trainer, created = Trainer.objects.get_or_create(
                user=user,
                defaults={
                    'business_name': 'Test Fitness Studio',
                    'bio': 'Testing all endpoints',
                    'location': 'Test City',
                    'expertise': ['strength training', 'yoga']
                }
            )
            if created:
                print_success(f"Created trainer profile: {trainer.business_name}")
            else:
                print_info(f"Using existing trainer: {trainer.business_name}")
            
            self.test_data['trainer'] = trainer
            self.test_data['user'] = user
            
            # Create or get test client
            client, created = Client.objects.get_or_create(
                trainer=trainer,
                email='test_client@trainerhub.com',
                defaults={
                    'first_name': 'Test',
                    'last_name': 'Client',
                    'fitness_level': 'intermediate',
                    'goals': ['weight loss', 'strength']
                }
            )
            if created:
                print_success(f"Created test client: {client.get_full_name()}")
            else:
                print_info(f"Using existing client: {client.get_full_name()}")
            
            self.test_data['client'] = client
            
            return True
        except Exception as e:
            print_error(f"Failed to setup test data: {str(e)}")
            return False
    
    def authenticate(self):
        """Get authentication token."""
        print_header("Authentication")
        
        try:
            response = requests.post(
                f"{self.base_url}/api/login/",
                json={
                    'email': self.email,
                    'password': self.password
                }
            )
            
            if response.status_code == 200:
                self.token = response.json().get('token')
                self.headers = {'Authorization': f'Token {self.token}'}
                print_success("Successfully authenticated")
                return True
            else:
                print_error(f"Authentication failed: {response.status_code}")
                print_error(f"Response: {response.text}")
                return False
        except Exception as e:
            print_error(f"Authentication error: {str(e)}")
            return False
    
    def test_endpoint(self, method, url, data=None, expected_status=200, description=""):
        """Test a single endpoint."""
        self.stats['total'] += 1
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=self.headers, json=data)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=self.headers, json=data)
            elif method.upper() == 'PATCH':
                response = requests.patch(url, headers=self.headers, json=data)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=self.headers)
            else:
                print_error(f"Unsupported method: {method}")
                self.stats['failed'] += 1
                return None
            
            if response.status_code == expected_status:
                print_success(f"{method} {url} - {description}")
                self.stats['passed'] += 1
                return response.json() if response.content else {}
            else:
                print_error(f"{method} {url} - Expected {expected_status}, got {response.status_code}")
                print_error(f"Response: {response.text[:200]}")
                self.stats['failed'] += 1
                return None
        except Exception as e:
            print_error(f"{method} {url} - Error: {str(e)}")
            self.stats['failed'] += 1
            return None
    
    def test_users_endpoints(self):
        """Test User endpoints (Epic 1-2)."""
        print_header("EPIC 1-2: User & Trainer Endpoints")
        
        # Get profile
        self.test_endpoint('GET', f"{self.base_url}/api/profile/", 
                          description="Get user profile")
        
        # Update profile
        self.test_endpoint('PATCH', f"{self.base_url}/api/profile/",
                          data={'first_name': 'Updated'},
                          description="Update user profile")
    
    def test_availability_endpoints(self):
        """Test Availability endpoints (Epic 2)."""
        print_header("EPIC 2: Availability Endpoints")
        
        # Create availability slot
        slot_data = {
            'day_of_week': 1,
            'start_time': '09:00:00',
            'end_time': '17:00:00',
            'is_active': True
        }
        slot_response = self.test_endpoint('POST', f"{self.base_url}/api/availability-slots/",
                                          data=slot_data, description="Create availability slot")
        
        if slot_response:
            slot_id = slot_response.get('id')
            
            # List slots
            self.test_endpoint('GET', f"{self.base_url}/api/availability-slots/",
                              description="List availability slots")
            
            # Get available slots
            tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            next_week = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
            self.test_endpoint('GET', 
                              f"{self.base_url}/api/availability-slots/available-slots/?trainer_id={self.test_data['trainer'].id}&start_date={tomorrow}&end_date={next_week}",
                              description="Get available slots")
    
    def test_clients_endpoints(self):
        """Test Client endpoints (Epic 3)."""
        print_header("EPIC 3: Client Management Endpoints")
        
        # List clients
        self.test_endpoint('GET', f"{self.base_url}/api/clients/",
                          description="List clients")
        
        # Get client details
        client_id = self.test_data['client'].id
        self.test_endpoint('GET', f"{self.base_url}/api/clients/{client_id}/",
                          description="Get client details")
        
        # Add note to client
        self.test_endpoint('POST', f"{self.base_url}/api/clients/{client_id}/add-note/",
                          data={'content': 'Test note from endpoint tester'},
                          description="Add note to client")
        
        # Get client notes
        self.test_endpoint('GET', f"{self.base_url}/api/clients/{client_id}/notes/",
                          description="Get client notes")
    
    def test_bookings_endpoints(self):
        """Test Booking endpoints (Epic 4)."""
        print_header("EPIC 4: Booking Endpoints")
        
        # List bookings
        self.test_endpoint('GET', f"{self.base_url}/api/bookings/",
                          description="List bookings")
        
        # Create booking
        start_time = (datetime.now() + timedelta(days=2)).replace(hour=10, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(hours=1)
        
        booking_data = {
            'client': self.test_data['client'].id,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'notes': 'Test booking'
        }
        booking_response = self.test_endpoint('POST', f"{self.base_url}/api/bookings/",
                                             data=booking_data, description="Create booking")
        
        if booking_response:
            booking_id = booking_response.get('id')
            
            # Get booking details
            self.test_endpoint('GET', f"{self.base_url}/api/bookings/{booking_id}/",
                              description="Get booking details")
            
            # Confirm booking
            self.test_endpoint('POST', f"{self.base_url}/api/bookings/{booking_id}/confirm/",
                              description="Confirm booking")
            
            # Get upcoming bookings
            self.test_endpoint('GET', f"{self.base_url}/api/bookings/upcoming/",
                              description="Get upcoming bookings")
            
            # Get past bookings
            self.test_endpoint('GET', f"{self.base_url}/api/bookings/past/",
                              description="Get past bookings")
    
    def test_packages_endpoints(self):
        """Test Package endpoints (Epic 5)."""
        print_header("EPIC 5: Session Package Endpoints")
        
        # Create package
        package_data = {
            'name': 'Test 5-Pack',
            'description': 'Test package',
            'sessions_count': 5,
            'price': '99.99',
            'is_active': True
        }
        package_response = self.test_endpoint('POST', f"{self.base_url}/api/packages/",
                                             data=package_data, description="Create package")
        
        if package_response:
            package_id = package_response.get('id')
            
            # List packages
            self.test_endpoint('GET', f"{self.base_url}/api/packages/",
                              description="List packages")
            
            # Assign package to client
            self.test_endpoint('POST', f"{self.base_url}/api/packages/{package_id}/assign-to-client/",
                              data={'client_id': self.test_data['client'].id},
                              description="Assign package to client")
            
            # List client packages
            self.test_endpoint('GET', f"{self.base_url}/api/client-packages/",
                              description="List client packages")
    
    def test_payments_endpoints(self):
        """Test Payment endpoints (Epic 6)."""
        print_header("EPIC 6: Payment Endpoints")
        
        # List subscriptions
        self.test_endpoint('GET', f"{self.base_url}/api/subscriptions/",
                          description="List subscriptions")
        
        # List payments
        self.test_endpoint('GET', f"{self.base_url}/api/payments/",
                          description="List payments")
    
    def test_notifications_endpoints(self):
        """Test Notification endpoints (Epic 7)."""
        print_header("EPIC 7: Notification Endpoints")
        
        # List notifications
        self.test_endpoint('GET', f"{self.base_url}/api/notifications/",
                          description="List notifications")
        
        # Get notification stats
        self.test_endpoint('GET', f"{self.base_url}/api/notifications/stats/",
                          description="Get notification statistics")
        
        # Get recent notifications
        self.test_endpoint('GET', f"{self.base_url}/api/notifications/recent/",
                          description="Get recent notifications")
    
    def test_analytics_endpoints(self):
        """Test Analytics endpoints (Epic 8)."""
        print_header("EPIC 8: Analytics Endpoints")
        
        # Get dashboard summary
        self.test_endpoint('GET', f"{self.base_url}/api/analytics/dashboard/",
                          description="Get dashboard summary")
        
        # Get revenue analytics
        self.test_endpoint('GET', f"{self.base_url}/api/analytics/revenue/?period=month",
                          description="Get revenue analytics")
        
        # Get booking statistics
        self.test_endpoint('GET', f"{self.base_url}/api/analytics/bookings-stats/",
                          description="Get booking statistics")
        
        # Get client statistics
        self.test_endpoint('GET', f"{self.base_url}/api/analytics/client-stats/",
                          description="Get client statistics")
        
        # Get metrics summary
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        self.test_endpoint('GET', 
                          f"{self.base_url}/api/analytics/metrics-summary/?start_date={start_date}&end_date={end_date}",
                          description="Get metrics summary")
    
    def run_all_tests(self):
        """Run all endpoint tests."""
        print_header("TRAINERHUB API ENDPOINT TEST SUITE")
        print(f"Base URL: {self.base_url}")
        print(f"Test User: {self.email}\n")
        
        # Setup
        if not self.setup_test_data():
            print_error("Cannot proceed without test data")
            return False
        
        if not self.authenticate():
            print_error("Cannot proceed without authentication")
            return False
        
        # Run tests
        self.test_users_endpoints()
        self.test_availability_endpoints()
        self.test_clients_endpoints()
        self.test_bookings_endpoints()
        self.test_packages_endpoints()
        self.test_payments_endpoints()
        self.test_notifications_endpoints()
        self.test_analytics_endpoints()
        
        # Print summary
        print_header("TEST SUMMARY")
        print(f"Total Tests: {self.stats['total']}")
        print_success(f"Passed: {self.stats['passed']}")
        print_error(f"Failed: {self.stats['failed']}")
        print_warning(f"Skipped: {self.stats['skipped']}")
        
        success_rate = (self.stats['passed'] / self.stats['total'] * 100) if self.stats['total'] > 0 else 0
        print(f"\nSuccess Rate: {success_rate:.2f}%")
        
        if self.stats['failed'] == 0:
            print_success("\n🎉 All tests passed!")
            return True
        else:
            print_error(f"\n⚠️  {self.stats['failed']} test(s) failed")
            return False

def main():
    """Main execution."""
    try:
        tester = EndpointTester(BASE_URL, TEST_EMAIL, TEST_PASSWORD)
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_error("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n\nUnexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

