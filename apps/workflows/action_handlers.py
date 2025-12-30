"""
Action handlers for workflow automation
"""
import logging
from django.core.mail import send_mail
from django.conf import settings
from .models import WorkflowAction, EmailTemplate, SMSTemplate
from .utils import replace_variables

logger = logging.getLogger(__name__)


def execute_action(action: WorkflowAction, event_data: dict):
    """
    Execute a workflow action.
    
    Args:
        action: Action to execute
        event_data: Event data for variable replacement
    """
    action_type = action.action_type
    action_data = action.action_data or {}
    
    handlers = {
        'send_email': handle_send_email,
        'send_sms': handle_send_sms,
        'update_status': handle_update_status,
        'create_note': handle_create_note,
    }
    
    handler = handlers.get(action_type)
    if handler:
        handler(action_data, event_data)
    else:
        logger.warning(f"Unknown action type: {action_type}")


def handle_send_email(action_data: dict, event_data: dict):
    """Send an email action."""
    template_id = action_data.get('template_id')
    recipient = action_data.get('recipient') or event_data.get('client_email')
    custom_subject = action_data.get('subject')
    custom_body = action_data.get('body')
    
    if not recipient:
        logger.error("No recipient specified for email action")
        return
    
    # Use template if provided
    if template_id:
        try:
            template = EmailTemplate.objects.get(id=template_id)
            subject = replace_variables(template.subject, event_data)
            body = replace_variables(template.body, event_data)
        except EmailTemplate.DoesNotExist:
            logger.error(f"Email template {template_id} not found")
            return
    else:
        subject = replace_variables(custom_subject or "Notification", event_data)
        body = replace_variables(custom_body or "", event_data)
    
    # Send email
    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,
        )
        logger.info(f"Email sent to {recipient}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        raise


def handle_send_sms(action_data: dict, event_data: dict):
    """Send an SMS action."""
    template_id = action_data.get('template_id')
    recipient = action_data.get('recipient') or event_data.get('client_phone')
    custom_message = action_data.get('message')
    
    if not recipient:
        logger.error("No recipient specified for SMS action")
        return
    
    # Use template if provided
    if template_id:
        try:
            template = SMSTemplate.objects.get(id=template_id)
            message = replace_variables(template.message, event_data)
        except SMSTemplate.DoesNotExist:
            logger.error(f"SMS template {template_id} not found")
            return
    else:
        message = replace_variables(custom_message or "", event_data)
    
    # Send SMS using Twilio
    try:
        from twilio.rest import Client as TwilioClient
        
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        from_number = settings.TWILIO_PHONE_NUMBER
        
        client = TwilioClient(account_sid, auth_token)
        
        message_obj = client.messages.create(
            body=message,
            from_=from_number,
            to=recipient
        )
        
        logger.info(f"SMS sent to {recipient}: {message_obj.sid}")
    except Exception as e:
        logger.error(f"Failed to send SMS: {e}")
        raise


def handle_update_status(action_data: dict, event_data: dict):
    """Update status action."""
    model_type = action_data.get('model_type')  # e.g., 'booking', 'client'
    object_id = event_data.get('id') or event_data.get('booking_id') or event_data.get('client_id')
    new_status = action_data.get('status')
    
    if not all([model_type, object_id, new_status]):
        logger.error("Missing required fields for update_status action")
        return
    
    try:
        if model_type == 'booking':
            from apps.bookings.models import Booking
            obj = Booking.objects.get(id=object_id)
            obj.status = new_status
            obj.save()
            logger.info(f"Updated booking {object_id} status to {new_status}")
        elif model_type == 'client':
            from apps.clients.models import Client
            obj = Client.objects.get(id=object_id)
            obj.status = new_status
            obj.save()
            logger.info(f"Updated client {object_id} status to {new_status}")
        else:
            logger.warning(f"Unknown model type: {model_type}")
    except Exception as e:
        logger.error(f"Failed to update status: {e}")
        raise


def handle_create_note(action_data: dict, event_data: dict):
    """Create a note action."""
    model_type = action_data.get('model_type')
    object_id = event_data.get('id') or event_data.get('booking_id') or event_data.get('client_id')
    note_content = replace_variables(action_data.get('content', ''), event_data)
    
    if not all([model_type, object_id, note_content]):
        logger.error("Missing required fields for create_note action")
        return
    
    try:
        if model_type == 'booking':
            from apps.bookings.models import Booking
            obj = Booking.objects.get(id=object_id)
            obj.notes = f"{obj.notes}\n\n{note_content}" if obj.notes else note_content
            obj.save()
            logger.info(f"Added note to booking {object_id}")
        elif model_type == 'client':
            from apps.clients.models import Client
            obj = Client.objects.get(id=object_id)
            obj.notes = f"{obj.notes}\n\n{note_content}" if obj.notes else note_content
            obj.save()
            logger.info(f"Added note to client {object_id}")
        else:
            logger.warning(f"Unknown model type: {model_type}")
    except Exception as e:
        logger.error(f"Failed to create note: {e}")
        raise

