"""
Integration tests for authentication flow
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.trainers.models import Trainer
from apps.payments.models import Subscription

User = get_user_model()


class AuthenticationFlowTest(TestCase):
    """Test complete authentication flow"""
    
    def setUp(self):
        self.client = APIClient()
    
    def test_complete_registration_to_dashboard_flow(self):
        """Test user registration → login → access dashboard"""
        # Step 1: Register new user
        register_data = {
            'email': 'newtrainer@example.com',
            'username': 'newtrainer',
            'password': 'securepass123',
            'password_confirm': 'securepass123'
        }
        response = self.client.post('/api/auth/register/', register_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        
        token = response.data['token']
        user_id = response.data['user']['id']
        
        # Step 2: Verify user was created
        user = User.objects.get(id=user_id)
        self.assertEqual(user.email, register_data['email'])
        
        # Step 3: Verify trainer profile was created
        trainer = Trainer.objects.get(user=user)
        self.assertIsNotNone(trainer)
        
        # Step 4: Verify free subscription was created
        subscription = Subscription.objects.filter(trainer=trainer).first()
        self.assertIsNotNone(subscription)
        self.assertEqual(subscription.plan_name, 'free')
        self.assertEqual(subscription.status, 'active')
        
        # Step 5: Use token to access protected endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        response = self.client.get('/api/trainers/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Step 6: Access dashboard endpoints
        response = self.client.get('/api/clients/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response = self.client.get('/api/bookings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response = self.client.get('/api/packages/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_login_logout_flow(self):
        """Test user login and logout"""
        # Create user
        user = User.objects.create_user(
            email='trainer@example.com',
            username='trainer1',
            password='pass123'
        )
        trainer = Trainer.objects.create(user=user, business_name='Fit Pro')
        
        # Login
        login_data = {
            'email': 'trainer@example.com',
            'password': 'pass123'
        }
        response = self.client.post('/api/auth/login/', login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        
        token = response.data['token']
        
        # Access protected endpoint with token
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        response = self.client.get('/api/trainers/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Logout
        response = self.client.post('/api/auth/logout/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Token should no longer work (depending on implementation)
        # Some implementations keep token valid but remove it on client side
    
    def test_password_reset_flow(self):
        """Test password reset flow"""
        # Create user
        user = User.objects.create_user(
            email='trainer@example.com',
            username='trainer1',
            password='oldpass123'
        )
        
        # Request password reset (if endpoint exists)
        # This would typically send an email with a reset link
        # For now, just test that the endpoint exists and responds
        
        # Login with new password after reset
        # This would be tested after implementing password reset
        pass

