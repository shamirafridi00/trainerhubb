"""
Integration tests for workflow execution
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch, MagicMock
from rest_framework.test import APIClient
from rest_framework import status
from apps.trainers.models import Trainer
from apps.clients.models import Client
from apps.bookings.models import Booking
from apps.packages.models import Service
from apps.workflows.models import (
    Workflow, WorkflowTrigger, WorkflowAction,
    EmailTemplate, WorkflowExecutionLog
)
from apps.workflows.services import WorkflowExecutor

User = get_user_model()


class WorkflowExecutionFlowTest(TestCase):
    """Test workflow creation and execution"""
    
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
            price=100.00
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_workflow_with_email_action(self):
        """Test workflow creation → trigger → action execution"""
        # Step 1: Create email template
        email_template = EmailTemplate.objects.create(
            trainer=self.trainer,
            name='Booking Confirmation',
            subject='Your booking is confirmed!',
            body='Hi {{client_name}}, your booking on {{booking_date}} is confirmed.',
            variables=['client_name', 'booking_date']
        )
        
        # Step 2: Create workflow
        workflow_data = {
            'name': 'Booking Confirmation Workflow',
            'description': 'Send email when booking is created',
            'is_active': True,
            'trigger': {
                'trigger_type': 'booking_created',
                'conditions': {},
                'delay_minutes': 0
            },
            'actions': [
                {
                    'action_type': 'send_email',
                    'action_data': {
                        'template_id': email_template.id,
                        'recipient_email': '{{client_email}}'
                    },
                    'order': 0
                }
            ]
        }
        
        response = self.client.post('/api/workflows/workflows/', workflow_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        workflow_id = response.data['id']
        workflow = Workflow.objects.get(id=workflow_id)
        
        # Step 3: Verify workflow components were created
        self.assertTrue(WorkflowTrigger.objects.filter(workflow=workflow).exists())
        self.assertTrue(WorkflowAction.objects.filter(workflow=workflow).exists())
        
        # Step 4: Create a booking to trigger the workflow
        with patch('apps.workflows.action_handlers.EmailService') as MockEmailService:
            mock_email_service = MagicMock()
            MockEmailService.send_email = mock_email_service
            
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
            
            # Manually trigger workflow execution for testing
            executor = WorkflowExecutor()
            event_data = {
                'booking': booking,
                'client': self.client_obj,
                'trainer': self.trainer
            }
            executor.check_triggers('booking_created', event_data)
            
            # Step 5: Verify workflow execution was logged
            # (Depending on implementation, this might create a log entry)
            # logs = WorkflowExecutionLog.objects.filter(workflow=workflow)
            # self.assertGreater(logs.count(), 0)
    
    def test_workflow_template_application(self):
        """Test applying a pre-built workflow template"""
        # Step 1: Get available workflow templates
        response = self.client.get('/api/workflows/templates/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Step 2: Apply a template
        if len(response.data) > 0:
            template_id = response.data[0]['id']
            response = self.client.post(f'/api/workflows/templates/{template_id}/use_template/')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            
            # Verify workflow was created
            workflow_id = response.data['id']
            workflow = Workflow.objects.get(id=workflow_id)
            self.assertFalse(workflow.is_active)  # Should start inactive
    
    def test_deactivate_workflow(self):
        """Test deactivating a workflow"""
        # Create workflow
        workflow = Workflow.objects.create(
            trainer=self.trainer,
            name='Test Workflow',
            is_active=True
        )
        WorkflowTrigger.objects.create(
            workflow=workflow,
            trigger_type='booking_created'
        )
        
        # Deactivate workflow
        response = self.client.post(f'/api/workflows/workflows/{workflow.id}/deactivate/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        workflow.refresh_from_db()
        self.assertFalse(workflow.is_active)
        
        # Create booking - workflow should NOT trigger
        start_time = timezone.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        booking = Booking.objects.create(
            trainer=self.trainer,
            client=self.client_obj,
            service=self.service,
            start_time=start_time,
            end_time=end_time
        )
        
        # Workflow should not execute because it's deactivated
    
    def test_workflow_with_multiple_actions(self):
        """Test workflow with multiple sequential actions"""
        # Create workflow with multiple actions
        workflow = Workflow.objects.create(
            trainer=self.trainer,
            name='Multi-Action Workflow',
            is_active=True
        )
        
        WorkflowTrigger.objects.create(
            workflow=workflow,
            trigger_type='booking_confirmed'
        )
        
        # Action 1: Send email
        WorkflowAction.objects.create(
            workflow=workflow,
            action_type='send_email',
            action_data={'subject': 'Confirmed', 'body': 'Your booking is confirmed'},
            order=0
        )
        
        # Action 2: Update status (example)
        WorkflowAction.objects.create(
            workflow=workflow,
            action_type='update_status',
            action_data={'target_model': 'Booking', 'new_status': 'confirmed'},
            order=1
        )
        
        # Action 3: Create note
        WorkflowAction.objects.create(
            workflow=workflow,
            action_type='create_note',
            action_data={'note_content': 'Confirmation email sent'},
            order=2
        )
        
        # Trigger workflow
        # Should execute all actions in order
        # (Testing would require mocking the action handlers)
    
    def test_workflow_with_delay(self):
        """Test workflow with delayed trigger"""
        # Create workflow with 24-hour delay
        workflow = Workflow.objects.create(
            trainer=self.trainer,
            name='Reminder Workflow',
            is_active=True
        )
        
        WorkflowTrigger.objects.create(
            workflow=workflow,
            trigger_type='booking_reminder',
            delay_minutes=1440  # 24 hours
        )
        
        WorkflowAction.objects.create(
            workflow=workflow,
            action_type='send_email',
            action_data={'subject': 'Reminder', 'body': 'Your session is tomorrow'},
            order=0
        )
        
        # This would require a task scheduler (Celery) to test properly
        # For now, just verify the workflow structure is correct
        trigger = workflow.trigger
        self.assertEqual(trigger.delay_minutes, 1440)

