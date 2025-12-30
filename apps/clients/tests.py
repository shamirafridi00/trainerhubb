"""
Unit tests for clients app
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from apps.trainers.models import Trainer
from apps.clients.models import Client

User = get_user_model()


class ClientModelTest(TestCase):
    """Tests for Client model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='trainer@example.com',
            username='trainer1',
            password='pass123'
        )
        self.trainer = Trainer.objects.create(
            user=self.user,
            business_name='Fit Pro'
        )
    
    def test_create_client(self):
        """Test creating a client"""
        client = Client.objects.create(
            trainer=self.trainer,
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone_number='+1234567890'
        )
        self.assertEqual(client.get_full_name(), 'John Doe')
        self.assertEqual(str(client), 'John Doe')
    
    def test_client_default_values(self):
        """Test client default field values"""
        client = Client.objects.create(
            trainer=self.trainer,
            first_name='Jane',
            last_name='Smith',
            email='jane@example.com'
        )
        self.assertEqual(client.status, 'active')
        self.assertEqual(client.payment_status, 'unpaid')
        self.assertEqual(client.total_paid, 0)


class ClientAPITest(APITestCase):
    """Tests for Client API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='trainer@example.com',
            username='trainer1',
            password='pass123'
        )
        self.trainer = Trainer.objects.create(
            user=self.user,
            business_name='Fit Pro'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_list_clients(self):
        """Test listing clients"""
        Client.objects.create(
            trainer=self.trainer,
            first_name='John',
            last_name='Doe',
            email='john@example.com'
        )
        response = self.client.get('/api/clients/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_create_client(self):
        """Test creating a client"""
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane@example.com',
            'phone_number': '+1234567890'
        }
        response = self.client.post('/api/clients/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Client.objects.count(), 1)
    
    def test_update_client(self):
        """Test updating a client"""
        client = Client.objects.create(
            trainer=self.trainer,
            first_name='John',
            last_name='Doe',
            email='john@example.com'
        )
        data = {'phone_number': '+9876543210'}
        response = self.client.patch(f'/api/clients/{client.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        client.refresh_from_db()
        self.assertEqual(client.phone_number, '+9876543210')
    
    def test_delete_client(self):
        """Test deleting a client"""
        client = Client.objects.create(
            trainer=self.trainer,
            first_name='John',
            last_name='Doe',
            email='john@example.com'
        )
        response = self.client.delete(f'/api/clients/{client.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Client.objects.count(), 0)
