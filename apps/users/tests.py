"""
Unit tests for users app
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase
from rest_framework import status

User = get_user_model()


class UserModelTest(TestCase):
    """Tests for User model"""
    
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123'
        }
    
    def test_create_user(self):
        """Test creating a regular user"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.username, self.user_data['username'])
        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_create_superuser(self):
        """Test creating a superuser"""
        admin = User.objects.create_superuser(**self.user_data)
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
    
    def test_user_str_representation(self):
        """Test user string representation"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), user.email)


class AuthenticationAPITest(APITestCase):
    """Tests for authentication endpoints"""
    
    def setUp(self):
        self.register_url = '/api/auth/register/'
        self.login_url = '/api/auth/login/'
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
    
    def test_user_registration(self):
        """Test user registration endpoint"""
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)
        
        # Verify user was created
        user = User.objects.get(email=self.user_data['email'])
        self.assertEqual(user.username, self.user_data['username'])
    
    def test_registration_password_mismatch(self):
        """Test registration fails with mismatched passwords"""
        data = self.user_data.copy()
        data['password_confirm'] = 'differentpass'
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_login(self):
        """Test user login endpoint"""
        # Create user first
        User.objects.create_user(**self.user_data)
        
        # Login
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
    
    def test_login_invalid_credentials(self):
        """Test login fails with invalid credentials"""
        User.objects.create_user(**self.user_data)
        
        login_data = {
            'email': self.user_data['email'],
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
