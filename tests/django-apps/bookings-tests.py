"""
Unit tests for bookings app
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase
from rest_framework import status
from apps.trainers.models import Trainer
from apps.clients.models import Client
from apps.bookings.models import Booking
from apps.availability.models import AvailabilitySlot
from apps.packages.models import Service

User = get_user_model()


class BookingModelTest(TestCase):
    """Tests for Booking model"""
    
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
        self.client_obj = Client.objects.create(
            trainer=self.trainer,
            first_name='John',
            last_name='Doe',
            email='john@example.com'
        )
        self.service = Service.objects.create(
            trainer=self.trainer,
            name='Personal Training',
            duration_minutes=60,
            price=100.00
        )
    
    def test_create_booking(self):
        """Test creating a booking"""
        start_time = timezone.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        booking = Booking.objects.create(
            trainer=self.trainer,
            client=self.client_obj,
            service=self.service,
            start_time=start_time,
            end_time=end_time,
            status='pending'
        )
        self.assertEqual(booking.status, 'pending')
        self.assertEqual(booking.service, self.service)
    
    def test_booking_str(self):
        """Test booking string representation"""
        start_time = timezone.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        booking = Booking.objects.create(
            trainer=self.trainer,
            client=self.client_obj,
            service=self.service,
            start_time=start_time,
            end_time=end_time
        )
        self.assertIn('John Doe', str(booking))


class AvailabilitySlotModelTest(TestCase):
    """Tests for AvailabilitySlot model"""
    
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
    
    def test_create_availability(self):
        """Test creating availability slot"""
        availability = AvailabilitySlot.objects.create(
            trainer=self.trainer,
            day_of_week=1,  # Monday
            start_time='09:00',
            end_time='17:00',
            is_available=True
        )
        self.assertTrue(availability.is_available)
        self.assertEqual(availability.day_of_week, 1)


class BookingAPITest(APITestCase):
    """Tests for Booking API endpoints"""
    
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
        self.client_obj = Client.objects.create(
            trainer=self.trainer,
            first_name='John',
            last_name='Doe',
            email='john@example.com'
        )
        self.service = Service.objects.create(
            trainer=self.trainer,
            name='Personal Training',
            duration_minutes=60,
            price=100.00
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_booking(self):
        """Test creating a booking via API"""
        start_time = timezone.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        data = {
            'client': self.client_obj.id,
            'service': self.service.id,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'status': 'pending'
        }
        response = self.client.post('/api/bookings/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_list_bookings(self):
        """Test listing bookings"""
        start_time = timezone.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        Booking.objects.create(
            trainer=self.trainer,
            client=self.client_obj,
            service=self.service,
            start_time=start_time,
            end_time=end_time
        )
        response = self.client.get('/api/bookings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
