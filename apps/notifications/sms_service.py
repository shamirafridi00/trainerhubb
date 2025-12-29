"""
SMS service for sending SMS messages via Twilio.
Handles booking reminders and confirmations.
"""
from twilio.rest import Client
from django.conf import settings
from django.utils import timezone
from .models import Notification


class SMSService:
    """Service for sending SMS via Twilio."""
    
    def __init__(self):
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.from_number = settings.TWILIO_PHONE_NUMBER
        
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
        else:
            self.client = None
    
    def send_booking_reminder(self, phone_number, booking, hours_before=24, trainer=None):
        """
        Send booking reminder SMS.
        
        Args:
            phone_number: Phone number of the client (E.164 format)
            booking: Booking instance
            hours_before: Hours before booking (default 24)
            trainer: Trainer instance (optional, extracted from booking if not provided)
        
        Returns:
            tuple: (success: bool, result: str or message SID)
        """
        if not self.client:
            return False, "Twilio credentials not configured"
        
        if not self.from_number:
            return False, "Twilio phone number not configured"
        
        if not trainer:
            trainer = booking.trainer
        
        message_text = (
            f"Reminder: Your session with {booking.trainer.business_name} "
            f"is {booking.start_time.strftime('%A at %I:%M %p')}. "
            f"Reply CONFIRM to confirm."
        )
        
        try:
            message = self.client.messages.create(
                body=message_text,
                from_=self.from_number,
                to=phone_number
            )
            
            Notification.objects.create(
                trainer=trainer,
                notification_type='sms',
                recipient=phone_number,
                message=message_text,
                status='sent',
                sent_at=timezone.now()
            )
            
            return True, message.sid
        except Exception as e:
            Notification.objects.create(
                trainer=trainer,
                notification_type='sms',
                recipient=phone_number,
                message=message_text,
                status='failed',
                failed_reason=str(e)
            )
            return False, str(e)
    
    def send_confirmation(self, phone_number, booking, trainer=None):
        """
        Send booking confirmation SMS.
        
        Args:
            phone_number: Phone number of the client (E.164 format)
            booking: Booking instance
            trainer: Trainer instance (optional, extracted from booking if not provided)
        
        Returns:
            tuple: (success: bool, result: str or message SID)
        """
        if not self.client:
            return False, "Twilio credentials not configured"
        
        if not self.from_number:
            return False, "Twilio phone number not configured"
        
        if not trainer:
            trainer = booking.trainer
        
        message_text = (
            f"Your session with {booking.trainer.business_name} "
            f"is confirmed for {booking.start_time.strftime('%A at %I:%M %p')}."
        )
        
        try:
            message = self.client.messages.create(
                body=message_text,
                from_=self.from_number,
                to=phone_number
            )
            
            Notification.objects.create(
                trainer=trainer,
                notification_type='sms',
                recipient=phone_number,
                message=message_text,
                status='sent',
                sent_at=timezone.now()
            )
            
            return True, message.sid
        except Exception as e:
            Notification.objects.create(
                trainer=trainer,
                notification_type='sms',
                recipient=phone_number,
                message=message_text,
                status='failed',
                failed_reason=str(e)
            )
            return False, str(e)
    
    def send_custom_sms(self, trainer, phone_number, message_text):
        """
        Send custom SMS message.
        
        Args:
            trainer: Trainer instance
            phone_number: Phone number (E.164 format)
            message_text: Message content
        
        Returns:
            tuple: (success: bool, result: str or message SID)
        """
        if not self.client:
            return False, "Twilio credentials not configured"
        
        if not self.from_number:
            return False, "Twilio phone number not configured"
        
        try:
            message = self.client.messages.create(
                body=message_text,
                from_=self.from_number,
                to=phone_number
            )
            
            Notification.objects.create(
                trainer=trainer,
                notification_type='sms',
                recipient=phone_number,
                message=message_text,
                status='sent',
                sent_at=timezone.now()
            )
            
            return True, message.sid
        except Exception as e:
            Notification.objects.create(
                trainer=trainer,
                notification_type='sms',
                recipient=phone_number,
                message=message_text,
                status='failed',
                failed_reason=str(e)
            )
            return False, str(e)


# Create singleton instance
sms_service = SMSService()

