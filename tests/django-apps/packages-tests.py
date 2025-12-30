"""
Unit tests for packages app
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from apps.trainers.models import Trainer
from apps.packages.models import Service, Package

User = get_user_model()


class ServiceModelTest(TestCase):
    """Tests for Service model"""
    
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
    
    def test_create_service(self):
        """Test creating a service"""
        service = Service.objects.create(
            trainer=self.trainer,
            name='Personal Training',
            description='One-on-one training',
            duration_minutes=60,
            price=100.00
        )
        self.assertEqual(service.name, 'Personal Training')
        self.assertEqual(service.duration_minutes, 60)
        self.assertEqual(service.price, 100.00)


class PackageModelTest(TestCase):
    """Tests for Package model"""
    
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
    
    def test_create_package(self):
        """Test creating a package"""
        package = Package.objects.create(
            trainer=self.trainer,
            name='Starter Pack',
            description='5 sessions',
            number_of_sessions=5,
            price=450.00,
            validity_days=30
        )
        self.assertEqual(package.name, 'Starter Pack')
        self.assertEqual(package.number_of_sessions, 5)
        self.assertEqual(package.price, 450.00)


class PackageAPITest(APITestCase):
    """Tests for Package API endpoints"""
    
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
    
    def test_create_package(self):
        """Test creating a package via API"""
        data = {
            'name': 'Premium Pack',
            'description': '10 sessions',
            'number_of_sessions': 10,
            'price': 850.00,
            'validity_days': 60
        }
        response = self.client.post('/api/packages/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_list_packages(self):
        """Test listing packages"""
        Package.objects.create(
            trainer=self.trainer,
            name='Basic Pack',
            number_of_sessions=3,
            price=250.00
        )
        response = self.client.get('/api/packages/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
