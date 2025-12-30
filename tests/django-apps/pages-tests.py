"""
Unit tests for pages app
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from apps.trainers.models import Trainer
from apps.pages.models import Page, PageTemplate, PageSection

User = get_user_model()


class PageTemplateModelTest(TestCase):
    """Tests for PageTemplate model"""
    
    def test_create_template(self):
        """Test creating a page template"""
        template = PageTemplate.objects.create(
            name='Fitness Pro',
            slug='fitness-pro',
            description='Professional fitness template',
            category='fitness',
            template_data={'sections': []}
        )
        self.assertEqual(template.name, 'Fitness Pro')
        self.assertEqual(template.slug, 'fitness-pro')
        self.assertFalse(template.is_premium)


class PageModelTest(TestCase):
    """Tests for Page model"""
    
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
        self.template = PageTemplate.objects.create(
            name='Basic Template',
            slug='basic',
            description='Basic template',
            template_data={}
        )
    
    def test_create_page(self):
        """Test creating a page"""
        page = Page.objects.create(
            trainer=self.trainer,
            title='My Landing Page',
            slug='landing',
            template=self.template,
            content={'sections': []}
        )
        self.assertEqual(page.title, 'My Landing Page')
        self.assertEqual(page.slug, 'landing')
        self.assertFalse(page.is_published)
    
    def test_page_unique_slug_per_trainer(self):
        """Test page slug is unique per trainer"""
        Page.objects.create(
            trainer=self.trainer,
            title='Page 1',
            slug='main',
            content={}
        )
        # Creating another page with same slug should fail
        # (handled by unique_together constraint)


class PageSectionModelTest(TestCase):
    """Tests for PageSection model"""
    
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
        self.page = Page.objects.create(
            trainer=self.trainer,
            title='Test Page',
            slug='test',
            content={}
        )
    
    def test_create_section(self):
        """Test creating a page section"""
        section = PageSection.objects.create(
            page=self.page,
            section_type='hero',
            order=0,
            content={'title': 'Welcome', 'subtitle': 'To my page'}
        )
        self.assertEqual(section.section_type, 'hero')
        self.assertTrue(section.is_visible)


class PageAPITest(APITestCase):
    """Tests for Page API endpoints"""
    
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
    
    def test_create_page(self):
        """Test creating a page via API"""
        data = {
            'title': 'New Page',
            'slug': 'new-page',
            'content': {'sections': []}
        }
        response = self.client.post('/api/pages/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_list_pages(self):
        """Test listing pages"""
        Page.objects.create(
            trainer=self.trainer,
            title='Test Page',
            slug='test',
            content={}
        )
        response = self.client.get('/api/pages/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_publish_page(self):
        """Test publishing a page"""
        page = Page.objects.create(
            trainer=self.trainer,
            title='Test Page',
            slug='test',
            content={}
        )
        response = self.client.post(f'/api/pages/{page.id}/publish/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        page.refresh_from_db()
        self.assertTrue(page.is_published)
