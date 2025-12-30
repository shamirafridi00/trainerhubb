"""
Workflow execution service - executes workflows when triggers occur
"""
import logging
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Workflow, WorkflowExecutionLog
from .action_handlers import execute_action

logger = logging.getLogger(__name__)


class WorkflowExecutor:
    """Execute workflows when triggers occur"""
    
    def check_triggers(self, event_type: str, event_data: dict):
        """
        Check if any workflows should trigger for this event.
        
        Args:
            event_type: Type of event (e.g., 'booking_created')
            event_data: Data associated with the event
        """
        # Find all active workflows with matching trigger type
        workflows = Workflow.objects.filter(
            is_active=True,
            trigger__trigger_type=event_type
        ).select_related('trigger').prefetch_related('actions')
        
        for workflow in workflows:
            try:
                if self.should_trigger(workflow, event_data):
                    self.execute_workflow(workflow, event_data)
            except Exception as e:
                logger.error(f"Error checking trigger for workflow {workflow.id}: {e}")
    
    def should_trigger(self, workflow: Workflow, event_data: dict) -> bool:
        """
        Check if workflow conditions are met.
        
        Args:
            workflow: Workflow to check
            event_data: Event data to check against conditions
        
        Returns:
            True if workflow should trigger
        """
        trigger = workflow.trigger
        conditions = trigger.conditions or {}
        
        # If no conditions, always trigger
        if not conditions:
            return True
        
        # Check each condition
        for field, expected_value in conditions.items():
            actual_value = event_data.get(field)
            
            # Handle different condition types
            if isinstance(expected_value, dict):
                operator = expected_value.get('operator', 'equals')
                value = expected_value.get('value')
                
                if operator == 'equals' and actual_value != value:
                    return False
                elif operator == 'not_equals' and actual_value == value:
                    return False
                elif operator == 'contains' and value not in str(actual_value):
                    return False
                elif operator == 'greater_than' and not (actual_value > value):
                    return False
                elif operator == 'less_than' and not (actual_value < value):
                    return False
            else:
                # Simple equality check
                if actual_value != expected_value:
                    return False
        
        return True
    
    def execute_workflow(self, workflow: Workflow, event_data: dict):
        """
        Execute all actions in a workflow.
        
        Args:
            workflow: Workflow to execute
            event_data: Event data to pass to actions
        """
        # Create execution log
        log = WorkflowExecutionLog.objects.create(
            workflow=workflow,
            trigger_type=workflow.trigger.trigger_type,
            trigger_data=event_data,
            status='running'
        )
        
        try:
            # Check if there's a delay
            delay_minutes = workflow.trigger.delay_minutes
            if delay_minutes > 0:
                # Schedule for later execution (would need celery/background task)
                logger.info(f"Workflow {workflow.id} scheduled for {delay_minutes} minutes from now")
                # TODO: Implement with Celery
                # execute_workflow_delayed.apply_async((workflow.id, event_data), countdown=delay_minutes * 60)
                log.status = 'pending'
                log.save()
                return
            
            # Execute actions in order
            actions = workflow.actions.all().order_by('order')
            
            for action in actions:
                try:
                    execute_action(action, event_data)
                except Exception as e:
                    logger.error(f"Error executing action {action.id}: {e}")
                    log.status = 'failed'
                    log.error_message = str(e)
                    log.save()
                    return
            
            # Mark as completed
            log.status = 'completed'
            log.save()
            logger.info(f"Workflow {workflow.id} executed successfully")
            
        except Exception as e:
            logger.error(f"Error executing workflow {workflow.id}: {e}")
            log.status = 'failed'
            log.error_message = str(e)
            log.save()


# Global instance
workflow_executor = WorkflowExecutor()


def trigger_workflow(event_type: str, event_data: dict):
    """
    Convenience function to trigger workflows.
    
    Args:
        event_type: Type of event
        event_data: Event data
    """
    workflow_executor.check_triggers(event_type, event_data)

