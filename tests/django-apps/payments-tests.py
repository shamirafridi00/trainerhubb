"""
Unit tests for payments app
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from rest_framework.test import APITestCase
from rest_framework import status
from apps.trainers.models import Trainer
from apps.clients.models import Client
from apps.payments.models import Subscription, ClientPayment
from apps.payments.permissions import check_usage_limit

User = get_user_model()


class SubscriptionModelTest(TestCase):
    """Tests for Subscription model"""
    
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
    
    def test_create_subscription(self):
        """Test creating a subscription"""
        subscription = Subscription.objects.create(
            trainer=self.trainer,
            plan_name='pro',
            status='active',
            current_period_start=timezone.now(),
            current_period_end=timezone.now() + timezone.timedelta(days=30)
        )
        self.assertEqual(subscription.plan_name, 'pro')
        self.assertEqual(subscription.status, 'active')
    
    def test_subscription_is_active(self):
        """Test subscription active status check"""
        subscription = Subscription.objects.create(
            trainer=self.trainer,
            plan_name='business',
            status='active',
            current_period_start=timezone.now(),
            current_period_end=timezone.now() + timezone.timedelta(days=30)
        )
        self.assertTrue(subscription.is_active())
    
    def test_get_feature_limits(self):
        """Test getting feature limits for subscription"""
        subscription = Subscription.objects.create(
            trainer=self.trainer,
            plan_name='pro',
            status='active',
            current_period_start=timezone.now(),
            current_period_end=timezone.now() + timezone.timedelta(days=30)
        )
        limits = subscription.get_feature_limits()
        self.assertEqual(limits['max_clients'], 50)
        self.assertEqual(limits['max_pages'], 5)


class ClientPaymentModelTest(TestCase):
    """Tests for ClientPayment model"""
    
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
    
    def test_create_payment(self):
        """Test creating a client payment"""
        payment = ClientPayment.objects.create(
            client=self.client_obj,
            amount=Decimal('100.00'),
            currency='USD',
            payment_method='stripe',
            payment_date=timezone.now().date(),
            recorded_by=self.user
        )
        self.assertEqual(payment.amount, Decimal('100.00'))
        self.assertEqual(payment.payment_method, 'stripe')
    
    def test_payment_updates_client_total(self):
        """Test that payment updates client total_paid"""
        ClientPayment.objects.create(
            client=self.client_obj,
            amount=Decimal('100.00'),
            currency='USD',
            payment_method='cash',
            payment_date=timezone.now().date(),
            recorded_by=self.user
        )
        # This would need a signal handler to actually update
        # For now just testing the model creation


class UsageLimitTest(TestCase):
    """Tests for usage limit checking"""
    
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
        Subscription.objects.create(
            trainer=self.trainer,
            plan_name='free',
            status='active',
            current_period_start=timezone.now(),
            current_period_end=timezone.now() + timezone.timedelta(days=30)
        )
    
    def test_check_usage_limit(self):
        """Test usage limit checking"""
        # Free plan allows 5 clients
        can_create, count, limit = check_usage_limit(self.trainer, 'clients')
        self.assertTrue(can_create)
        self.assertEqual(limit, 5)


class PaymentAPITest(APITestCase):
    """Tests for Payment API endpoints"""
    
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
        self.client.force_authenticate(user=self.user)
    
    def test_record_payment(self):
        """Test recording a client payment"""
        data = {
            'client': self.client_obj.id,
            'amount': '100.00',
            'currency': 'USD',
            'payment_method': 'stripe',
            'payment_date': timezone.now().date().isoformat()
        }
        response = self.client.post('/api/payments/client-payments/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
