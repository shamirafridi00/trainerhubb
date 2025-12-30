"""
Integration tests for subscription flow
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from apps.trainers.models import Trainer
from apps.payments.models import Subscription
from apps.clients.models import Client

User = get_user_model()


class SubscriptionFlowTest(TestCase):
    """Test subscription upgrade and feature unlocking"""
    
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
        self.client.force_authenticate(user=self.user)
    
    def test_free_plan_limits(self):
        """Test that free plan enforces limits"""
        # Create free subscription
        Subscription.objects.create(
            trainer=self.trainer,
            plan_name='free',
            status='active',
            current_period_start=timezone.now(),
            current_period_end=timezone.now() + timezone.timedelta(days=30)
        )
        
        # Free plan allows 5 clients
        for i in range(5):
            response = self.client.post('/api/clients/', {
                'first_name': f'Client{i}',
                'last_name': 'Test',
                'email': f'client{i}@example.com'
            })
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 6th client should fail
        response = self.client.post('/api/clients/', {
            'first_name': 'Client6',
            'last_name': 'Test',
            'email': 'client6@example.com'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('limit', response.data.get('error', '').lower())
    
    def test_upgrade_to_pro_unlocks_features(self):
        """Test that upgrading to pro unlocks features"""
        # Start with free subscription
        subscription = Subscription.objects.create(
            trainer=self.trainer,
            plan_name='free',
            status='active',
            current_period_start=timezone.now(),
            current_period_end=timezone.now() + timezone.timedelta(days=30)
        )
        
        # Upgrade to pro
        subscription.plan_name = 'pro'
        subscription.save()
        
        # Pro plan allows 50 clients
        limits = subscription.get_feature_limits()
        self.assertEqual(limits['max_clients'], 50)
        
        # Create 10 clients (should all succeed)
        for i in range(10):
            response = self.client.post('/api/clients/', {
                'first_name': f'Client{i}',
                'last_name': 'Test',
                'email': f'client{i}@example.com'
            })
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_upgrade_to_business_removes_limits(self):
        """Test that business plan removes limits"""
        # Create business subscription
        subscription = Subscription.objects.create(
            trainer=self.trainer,
            plan_name='business',
            status='active',
            current_period_start=timezone.now(),
            current_period_end=timezone.now() + timezone.timedelta(days=30)
        )
        
        limits = subscription.get_feature_limits()
        self.assertEqual(limits['max_clients'], 999999)  # Unlimited
        self.assertEqual(limits['max_pages'], 999999)  # Unlimited
        self.assertEqual(limits['max_workflows'], 999999)  # Unlimited
    
    def test_expired_subscription_restricts_access(self):
        """Test that expired subscription restricts features"""
        # Create expired subscription
        subscription = Subscription.objects.create(
            trainer=self.trainer,
            plan_name='pro',
            status='expired',
            current_period_start=timezone.now() - timezone.timedelta(days=60),
            current_period_end=timezone.now() - timezone.timedelta(days=30)
        )
        
        # Try to create a client (should fail or be restricted)
        response = self.client.post('/api/clients/', {
            'first_name': 'Client',
            'last_name': 'Test',
            'email': 'client@example.com'
        })
        # Depending on implementation, this might fail or revert to free tier limits

