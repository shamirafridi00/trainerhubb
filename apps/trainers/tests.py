"""
Unit tests for trainers app
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from apps.trainers.models import Trainer, WhiteLabelSettings, PaymentLinks

User = get_user_model()


class TrainerModelTest(TestCase):
    """Tests for Trainer model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='trainer@example.com',
            username='trainer1',
            password='pass123'
        )
    
    def test_create_trainer(self):
        """Test creating a trainer"""
        trainer = Trainer.objects.create(
            user=self.user,
            business_name='Fit Pro',
            bio='Professional trainer',
            location='New York'
        )
        self.assertEqual(trainer.business_name, 'Fit Pro')
        self.assertEqual(str(trainer), f'Fit Pro ({self.user.email})')
    
    def test_trainer_default_values(self):
        """Test trainer default field values"""
        trainer = Trainer.objects.create(
            user=self.user,
            business_name='Test Gym'
        )
        self.assertEqual(trainer.rating, 0.0)
        self.assertEqual(trainer.total_sessions, 0)
        self.assertFalse(trainer.is_verified)
        self.assertEqual(trainer.timezone, 'UTC')


class WhiteLabelSettingsTest(TestCase):
    """Tests for WhiteLabelSettings model"""
    
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
    
    def test_create_whitelabel_settings(self):
        """Test creating white-label settings"""
        settings = WhiteLabelSettings.objects.create(
            trainer=self.trainer,
            primary_color='#FF0000',
            remove_branding=True
        )
        self.assertEqual(settings.primary_color, '#FF0000')
        self.assertTrue(settings.remove_branding)
    
    def test_get_css_variables(self):
        """Test CSS variables generation"""
        settings = WhiteLabelSettings.objects.create(
            trainer=self.trainer,
            primary_color='#3b82f6',
            font_family='Roboto'
        )
        css_vars = settings.get_css_variables()
        self.assertIn('--primary-color', css_vars)
        self.assertEqual(css_vars['--primary-color'], '#3b82f6')
        self.assertIn('Roboto', css_vars['--font-family'])


class PaymentLinksTest(TestCase):
    """Tests for PaymentLinks model"""
    
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
    
    def test_create_payment_links(self):
        """Test creating payment links"""
        payment_links = PaymentLinks.objects.create(
            trainer=self.trainer,
            stripe_link='https://stripe.com/pay/123',
            venmo_username='fitpro'
        )
        self.assertEqual(payment_links.stripe_link, 'https://stripe.com/pay/123')
        self.assertEqual(payment_links.venmo_username, 'fitpro')
    
    def test_get_available_methods(self):
        """Test getting available payment methods"""
        payment_links = PaymentLinks.objects.create(
            trainer=self.trainer,
            stripe_link='https://stripe.com/pay/123',
            venmo_username='fitpro',
            paypal_link='https://paypal.me/fitpro'
        )
        methods = payment_links.get_available_methods()
        self.assertEqual(len(methods), 3)
        self.assertTrue(any(m['type'] == 'stripe' for m in methods))
        self.assertTrue(any(m['type'] == 'venmo' for m in methods))


class TrainerAPITest(APITestCase):
    """Tests for Trainer API endpoints"""
    
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
    
    def test_get_trainer_profile(self):
        """Test getting trainer profile"""
        response = self.client.get('/api/trainers/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['business_name'], 'Fit Pro')
    
    def test_update_trainer_profile(self):
        """Test updating trainer profile"""
        data = {'bio': 'Updated bio'}
        response = self.client.patch(f'/api/trainers/{self.trainer.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.trainer.refresh_from_db()
        self.assertEqual(self.trainer.bio, 'Updated bio')
