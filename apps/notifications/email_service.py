"""
Email service for sending emails via SendGrid.
Handles booking confirmations, reminders, and payment receipts.
"""
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from .models import Notification


class EmailService:
    """Service for sending emails via SendGrid."""
    
    def __init__(self):
        self.api_key = settings.SENDGRID_API_KEY
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@trainerhub.com')
        
        if self.api_key:
            self.client = SendGridAPIClient(self.api_key)
        else:
            self.client = None
    
    def send_booking_confirmation(self, client_email, booking, trainer=None):
        """
        Send booking confirmation email.
        
        Args:
            client_email: Email address of the client
            booking: Booking instance
            trainer: Trainer instance (optional, extracted from booking if not provided)
        
        Returns:
            tuple: (success: bool, result: str or error message)
        """
        if not self.client:
            return False, "SendGrid API key not configured"
        
        if not trainer:
            trainer = booking.trainer
        
        subject = f'Booking Confirmed with {booking.trainer.business_name}'
        
        # Simple HTML email template
        html_content = self._render_booking_confirmation_template({
            'client_name': booking.client.get_full_name(),
            'trainer_name': booking.trainer.business_name,
            'date': booking.start_time.date(),
            'time': booking.start_time.strftime('%I:%M %p'),
            'duration': booking.duration_minutes,
            'location': getattr(booking.trainer, 'location', ''),
        })
        
        message = Mail(
            from_email=self.from_email,
            to_emails=client_email,
            subject=subject,
            html_content=html_content
        )
        
        try:
            response = self.client.send(message)
            
            # Create notification record
            Notification.objects.create(
                trainer=trainer,
                notification_type='email',
                recipient=client_email,
                subject=subject,
                message=f'Booking confirmed for {booking.start_time}',
                status='sent',
                sent_at=timezone.now()
            )
            
            return True, response.status_code
        except Exception as e:
            # Create failed notification record
            Notification.objects.create(
                trainer=trainer,
                notification_type='email',
                recipient=client_email,
                subject=subject,
                message=f'Booking confirmed for {booking.start_time}',
                status='failed',
                failed_reason=str(e)
            )
            return False, str(e)
    
    def send_booking_reminder(self, client_email, booking, hours_before=24, trainer=None):
        """
        Send booking reminder email.
        
        Args:
            client_email: Email address of the client
            booking: Booking instance
            hours_before: Hours before booking (default 24)
            trainer: Trainer instance (optional)
        
        Returns:
            tuple: (success: bool, result: str or error message)
        """
        if not self.client:
            return False, "SendGrid API key not configured"
        
        if not trainer:
            trainer = booking.trainer
        
        subject = f'Reminder: Your session in {hours_before} hours'
        
        html_content = self._render_booking_reminder_template({
            'client_name': booking.client.get_full_name(),
            'trainer_name': booking.trainer.business_name,
            'date': booking.start_time.date(),
            'time': booking.start_time.strftime('%I:%M %p'),
            'hours_before': hours_before,
            'location': getattr(booking.trainer, 'location', ''),
        })
        
        message = Mail(
            from_email=self.from_email,
            to_emails=client_email,
            subject=subject,
            html_content=html_content
        )
        
        try:
            response = self.client.send(message)
            
            Notification.objects.create(
                trainer=trainer,
                notification_type='email',
                recipient=client_email,
                subject=subject,
                message=f'Reminder: Booking in {hours_before} hours',
                status='sent',
                sent_at=timezone.now()
            )
            
            return True, response.status_code
        except Exception as e:
            Notification.objects.create(
                trainer=trainer,
                notification_type='email',
                recipient=client_email,
                subject=subject,
                message=f'Reminder: Booking in {hours_before} hours',
                status='failed',
                failed_reason=str(e)
            )
            return False, str(e)
    
    def send_payment_receipt(self, trainer_email, payment, trainer=None):
        """
        Send payment receipt email.
        
        Args:
            trainer_email: Email address of the trainer
            payment: Payment instance
            trainer: Trainer instance (optional, extracted from payment if not provided)
        
        Returns:
            tuple: (success: bool, result: str or error message)
        """
        if not self.client:
            return False, "SendGrid API key not configured"
        
        if not trainer:
            trainer = payment.subscription.trainer
        
        subject = f'Payment Receipt - ${payment.amount}'
        
        html_content = self._render_payment_receipt_template({
            'trainer_name': trainer.business_name,
            'amount': payment.amount,
            'currency': payment.currency,
            'transaction_id': payment.paddle_transaction_id,
            'date': payment.created_at.date(),
        })
        
        message = Mail(
            from_email=self.from_email,
            to_emails=trainer_email,
            subject=subject,
            html_content=html_content
        )
        
        try:
            response = self.client.send(message)
            
            Notification.objects.create(
                trainer=trainer,
                notification_type='email',
                recipient=trainer_email,
                subject=subject,
                message=f'Payment receipt for ${payment.amount}',
                status='sent',
                sent_at=timezone.now()
            )
            
            return True, response.status_code
        except Exception as e:
            Notification.objects.create(
                trainer=trainer,
                notification_type='email',
                recipient=trainer_email,
                subject=subject,
                message=f'Payment receipt for ${payment.amount}',
                status='failed',
                failed_reason=str(e)
            )
            return False, str(e)
    
    def send_custom_email(self, trainer, recipient, subject, message_text, html_content=None):
        """
        Send custom email.
        
        Args:
            trainer: Trainer instance
            recipient: Email address
            subject: Email subject
            message_text: Plain text message
            html_content: HTML content (optional)
        
        Returns:
            tuple: (success: bool, result: str or error message)
        """
        if not self.client:
            return False, "SendGrid API key not configured"
        
        if not html_content:
            html_content = f"<p>{message_text}</p>"
        
        message = Mail(
            from_email=self.from_email,
            to_emails=recipient,
            subject=subject,
            html_content=html_content
        )
        
        try:
            response = self.client.send(message)
            
            Notification.objects.create(
                trainer=trainer,
                notification_type='email',
                recipient=recipient,
                subject=subject,
                message=message_text,
                status='sent',
                sent_at=timezone.now()
            )
            
            return True, response.status_code
        except Exception as e:
            Notification.objects.create(
                trainer=trainer,
                notification_type='email',
                recipient=recipient,
                subject=subject,
                message=message_text,
                status='failed',
                failed_reason=str(e)
            )
            return False, str(e)
    
    @staticmethod
    def _render_booking_confirmation_template(context):
        """Render booking confirmation email template."""
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4CAF50;">Booking Confirmed!</h2>
                <p>Hi {context['client_name']},</p>
                <p>Your training session with <strong>{context['trainer_name']}</strong> has been confirmed.</p>
                <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Date:</strong> {context['date']}</p>
                    <p><strong>Time:</strong> {context['time']}</p>
                    <p><strong>Duration:</strong> {context['duration']} minutes</p>
                    {f"<p><strong>Location:</strong> {context['location']}</p>" if context.get('location') else ''}
                </div>
                <p>We look forward to seeing you!</p>
                <p>Best regards,<br>{context['trainer_name']}</p>
            </div>
        </body>
        </html>
        """
    
    @staticmethod
    def _render_booking_reminder_template(context):
        """Render booking reminder email template."""
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #FF9800;">Reminder: Upcoming Session</h2>
                <p>Hi {context['client_name']},</p>
                <p>This is a reminder that you have a session with <strong>{context['trainer_name']}</strong> in {context['hours_before']} hours.</p>
                <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Date:</strong> {context['date']}</p>
                    <p><strong>Time:</strong> {context['time']}</p>
                    {f"<p><strong>Location:</strong> {context['location']}</p>" if context.get('location') else ''}
                </div>
                <p>See you soon!</p>
                <p>Best regards,<br>{context['trainer_name']}</p>
            </div>
        </body>
        </html>
        """
    
    @staticmethod
    def _render_payment_receipt_template(context):
        """Render payment receipt email template."""
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2196F3;">Payment Receipt</h2>
                <p>Hi {context['trainer_name']},</p>
                <p>Thank you for your payment. Here's your receipt:</p>
                <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Amount:</strong> {context['currency']} {context['amount']}</p>
                    <p><strong>Transaction ID:</strong> {context['transaction_id']}</p>
                    <p><strong>Date:</strong> {context['date']}</p>
                </div>
                <p>Best regards,<br>TrainerHub</p>
            </div>
        </body>
        </html>
        """


# Create singleton instance
email_service = EmailService()

