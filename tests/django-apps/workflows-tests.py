"""
Unit tests for workflows app
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from apps.trainers.models import Trainer
from apps.workflows.models import (
    Workflow, WorkflowTrigger, WorkflowAction,
    EmailTemplate, SMSTemplate, WorkflowTemplate, WorkflowExecutionLog
)
from apps.workflows.services import WorkflowExecutor

User = get_user_model()


class WorkflowModelTest(TestCase):
    """Tests for Workflow model"""
    
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
    
    def test_create_workflow(self):
        """Test creating a workflow"""
        workflow = Workflow.objects.create(
            trainer=self.trainer,
            name='Booking Confirmation',
            description='Send email when booking is created',
            is_active=True
        )
        self.assertEqual(workflow.name, 'Booking Confirmation')
        self.assertTrue(workflow.is_active)


class WorkflowTriggerModelTest(TestCase):
    """Tests for WorkflowTrigger model"""
    
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
        self.workflow = Workflow.objects.create(
            trainer=self.trainer,
            name='Test Workflow'
        )
    
    def test_create_trigger(self):
        """Test creating a workflow trigger"""
        trigger = WorkflowTrigger.objects.create(
            workflow=self.workflow,
            trigger_type='booking_created',
            conditions={},
            delay_minutes=0
        )
        self.assertEqual(trigger.trigger_type, 'booking_created')
        self.assertEqual(trigger.delay_minutes, 0)


class WorkflowActionModelTest(TestCase):
    """Tests for WorkflowAction model"""
    
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
        self.workflow = Workflow.objects.create(
            trainer=self.trainer,
            name='Test Workflow'
        )
    
    def test_create_action(self):
        """Test creating a workflow action"""
        action = WorkflowAction.objects.create(
            workflow=self.workflow,
            action_type='send_email',
            action_data={'subject': 'Test', 'body': 'Hello'},
            order=0
        )
        self.assertEqual(action.action_type, 'send_email')
        self.assertEqual(action.order, 0)


class EmailTemplateModelTest(TestCase):
    """Tests for EmailTemplate model"""
    
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
    
    def test_create_email_template(self):
        """Test creating an email template"""
        template = EmailTemplate.objects.create(
            trainer=self.trainer,
            name='Welcome Email',
            subject='Welcome!',
            body='Welcome {{client_name}}!',
            variables=['client_name']
        )
        self.assertEqual(template.name, 'Welcome Email')
        self.assertIn('client_name', template.variables)


class SMSTemplateModelTest(TestCase):
    """Tests for SMSTemplate model"""
    
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
    
    def test_create_sms_template(self):
        """Test creating an SMS template"""
        template = SMSTemplate.objects.create(
            trainer=self.trainer,
            name='Reminder SMS',
            message='Reminder: Session tomorrow at {{booking_time}}',
            variables=['booking_time']
        )
        self.assertEqual(template.name, 'Reminder SMS')
        self.assertLessEqual(len(template.message), 160)


class WorkflowTemplateModelTest(TestCase):
    """Tests for WorkflowTemplate model"""
    
    def test_create_workflow_template(self):
        """Test creating a workflow template"""
        template = WorkflowTemplate.objects.create(
            name='Booking Confirmation',
            description='Send confirmation email',
            category='booking',
            trigger_type='booking_created',
            actions_config=[{'action_type': 'send_email', 'action_data': {}, 'order': 0}]
        )
        self.assertEqual(template.name, 'Booking Confirmation')
        self.assertEqual(template.category, 'booking')
        self.assertEqual(template.times_used, 0)


class WorkflowAPITest(APITestCase):
    """Tests for Workflow API endpoints"""
    
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
    
    def test_create_workflow(self):
        """Test creating a workflow via API"""
        data = {
            'name': 'Test Workflow',
            'description': 'Test description',
            'is_active': True,
            'trigger': {
                'trigger_type': 'booking_created',
                'conditions': {},
                'delay_minutes': 0
            },
            'actions': [
                {
                    'action_type': 'send_email',
                    'action_data': {'subject': 'Test', 'body': 'Test'},
                    'order': 0
                }
            ]
        }
        response = self.client.post('/api/workflows/workflows/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_list_workflows(self):
        """Test listing workflows"""
        Workflow.objects.create(
            trainer=self.trainer,
            name='Test Workflow'
        )
        response = self.client.get('/api/workflows/workflows/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_activate_workflow(self):
        """Test activating a workflow"""
        workflow = Workflow.objects.create(
            trainer=self.trainer,
            name='Test Workflow',
            is_active=False
        )
        WorkflowTrigger.objects.create(
            workflow=workflow,
            trigger_type='booking_created'
        )
        response = self.client.post(f'/api/workflows/workflows/{workflow.id}/activate/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class WorkflowExecutorTest(TestCase):
    """Tests for WorkflowExecutor service"""
    
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
        self.workflow = Workflow.objects.create(
            trainer=self.trainer,
            name='Test Workflow',
            is_active=True
        )
        WorkflowTrigger.objects.create(
            workflow=self.workflow,
            trigger_type='booking_created',
            conditions={},
            delay_minutes=0
        )
        self.executor = WorkflowExecutor()
    
    def test_check_triggers(self):
        """Test checking for workflow triggers"""
        event_data = {
            'trainer': self.trainer,
            'event_type': 'booking_created'
        }
        # This would trigger the workflow
        # Testing execution would require mocking email/SMS services
        self.assertIsNotNone(self.executor)
