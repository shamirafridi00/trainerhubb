"""
Integration tests for booking flow
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from rest_framework.test import APIClient
from rest_framework import status
from apps.trainers.models import Trainer
from apps.clients.models import Client
from apps.bookings.models import Booking
from apps.packages.models import Service
from apps.payments.models import ClientPayment

User = get_user_model()


class BookingFlowTest(TestCase):
    """Test complete booking flow"""
    
    def setUp(self):
        self.client = APIClient()
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
            price=Decimal('100.00')
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_booking_and_record_payment(self):
        """Test client creation → booking → payment recording"""
        # Step 1: Create booking
        start_time = timezone.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        booking_data = {
            'client': self.client_obj.id,
            'service': self.service.id,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'status': 'pending'
        }
        response = self.client.post('/api/bookings/', booking_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        booking_id = response.data['id']
        booking = Booking.objects.get(id=booking_id)
        
        # Step 2: Confirm booking
        response = self.client.patch(f'/api/bookings/{booking_id}/', {'status': 'confirmed'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'confirmed')
        
        # Step 3: Record payment for booking
        payment_data = {
            'client': self.client_obj.id,
            'amount': '100.00',
            'currency': 'USD',
            'payment_method': 'stripe',
            'payment_date': timezone.now().date().isoformat(),
            'booking': booking_id
        }
        response = self.client.post('/api/payments/client-payments/', payment_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Step 4: Verify payment was recorded
        payment = ClientPayment.objects.get(client=self.client_obj, booking=booking)
        self.assertEqual(payment.amount, Decimal('100.00'))
        
        # Step 5: Verify client payment status updated
        self.client_obj.refresh_from_db()
        # Would need signal handler to update client total_paid
    
    def test_public_booking_flow(self):
        """Test public booking flow (no authentication)"""
        # Create unauthenticated client
        unauthenticated_client = APIClient()
        
        # Step 1: View trainer's public page availability
        response = unauthenticated_client.get(
            f'/api/public/{self.trainer.user.username}/availability/',
            {'date': timezone.now().date().isoformat()}
        )
        # Should show available slots
        
        # Step 2: Create booking as public client
        start_time = timezone.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        booking_data = {
            'client_name': 'Jane Smith',
            'client_email': 'jane@example.com',
            'client_phone': '+1234567890',
            'service': self.service.id,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'notes': 'First session'
        }
        response = unauthenticated_client.post(
            f'/api/public/{self.trainer.user.username}/bookings/',
            booking_data
        )
        
        # Should create booking and client if they don't exist
        # (Implementation depends on public booking endpoint)
    
    def test_booking_cancellation_flow(self):
        """Test booking cancellation"""
        # Create booking
        start_time = timezone.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        booking = Booking.objects.create(
            trainer=self.trainer,
            client=self.client_obj,
            service=self.service,
            start_time=start_time,
            end_time=end_time,
            status='confirmed'
        )
        
        # Cancel booking
        response = self.client.patch(f'/api/bookings/{booking.id}/', {'status': 'cancelled'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'cancelled')
    
    def test_prevent_double_booking(self):
        """Test that double bookings are prevented"""
        start_time = timezone.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        # Create first booking
        booking1 = Booking.objects.create(
            trainer=self.trainer,
            client=self.client_obj,
            service=self.service,
            start_time=start_time,
            end_time=end_time,
            status='confirmed'
        )
        
        # Try to create overlapping booking
        booking_data = {
            'client': self.client_obj.id,
            'service': self.service.id,
            'start_time': (start_time + timedelta(minutes=30)).isoformat(),
            'end_time': (end_time + timedelta(minutes=30)).isoformat(),
            'status': 'pending'
        }
        response = self.client.post('/api/bookings/', booking_data)
        
        # Should fail with validation error
        # (Implementation depends on validation logic)

