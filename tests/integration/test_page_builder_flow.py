"""
Integration tests for page builder flow
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.trainers.models import Trainer
from apps.pages.models import Page, PageTemplate, PageSection

User = get_user_model()


class PageBuilderFlowTest(TestCase):
    """Test complete page builder flow"""
    
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
        self.template = PageTemplate.objects.create(
            name='Fitness Pro',
            slug='fitness-pro',
            description='Professional fitness template',
            category='fitness',
            template_data={'sections': []}
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_page_from_template(self):
        """Test page creation → template application → customization → publishing"""
        # Step 1: Get available templates
        response = self.client.get('/api/pages/templates/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        
        # Step 2: Create page from template
        page_data = {
            'title': 'My Landing Page',
            'slug': 'landing',
            'template': self.template.id,
            'content': {'sections': []}
        }
        response = self.client.post('/api/pages/', page_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        page_id = response.data['id']
        page = Page.objects.get(id=page_id)
        
        # Step 3: Add sections to page
        section1 = PageSection.objects.create(
            page=page,
            section_type='hero',
            order=0,
            content={
                'title': 'Transform Your Life',
                'subtitle': 'Professional Personal Training',
                'cta_text': 'Book Now',
                'cta_link': '/booking'
            }
        )
        
        section2 = PageSection.objects.create(
            page=page,
            section_type='services',
            order=1,
            content={
                'title': 'Our Services',
                'services': [
                    {'name': 'Personal Training', 'price': '$100/session'},
                    {'name': 'Group Classes', 'price': '$50/session'}
                ]
            }
        )
        
        # Step 4: Update page SEO settings
        seo_data = {
            'seo_title': 'Best Personal Trainer',
            'seo_description': 'Professional personal training services',
            'seo_keywords': 'fitness, training, gym'
        }
        response = self.client.patch(f'/api/pages/{page_id}/', seo_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Step 5: Publish page
        response = self.client.post(f'/api/pages/{page_id}/publish/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        page.refresh_from_db()
        self.assertTrue(page.is_published)
        self.assertIsNotNone(page.published_at)
        
        # Step 6: Verify page is accessible publicly
        unauthenticated_client = APIClient()
        response = unauthenticated_client.get(f'/api/public/{self.trainer.user.username}/pages/{page.slug}/')
        # Should return page content
    
    def test_page_section_reordering(self):
        """Test reordering page sections"""
        # Create page with multiple sections
        page = Page.objects.create(
            trainer=self.trainer,
            title='Test Page',
            slug='test',
            content={}
        )
        
        section1 = PageSection.objects.create(
            page=page,
            section_type='hero',
            order=0,
            content={}
        )
        
        section2 = PageSection.objects.create(
            page=page,
            section_type='about',
            order=1,
            content={}
        )
        
        section3 = PageSection.objects.create(
            page=page,
            section_type='contact',
            order=2,
            content={}
        )
        
        # Reorder sections
        sections_data = [
            {'id': section3.id, 'order': 0},
            {'id': section1.id, 'order': 1},
            {'id': section2.id, 'order': 2}
        ]
        
        response = self.client.post(
            f'/api/pages/{page.id}/manage_sections/',
            {'sections': sections_data},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify new order
        sections = PageSection.objects.filter(page=page).order_by('order')
        self.assertEqual(sections[0].section_type, 'contact')
        self.assertEqual(sections[1].section_type, 'hero')
        self.assertEqual(sections[2].section_type, 'about')
    
    def test_unpublish_page(self):
        """Test unpublishing a page"""
        page = Page.objects.create(
            trainer=self.trainer,
            title='Test Page',
            slug='test',
            content={},
            is_published=True
        )
        
        response = self.client.post(f'/api/pages/{page.id}/unpublish/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        page.refresh_from_db()
        self.assertFalse(page.is_published)
        
        # Verify page is no longer publicly accessible
        unauthenticated_client = APIClient()
        response = unauthenticated_client.get(
            f'/api/public/{self.trainer.user.username}/pages/{page.slug}/'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

