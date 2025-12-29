"""
Celery tasks for sending notifications asynchronously.
These tasks run in the background to avoid blocking the main application.
"""
from celery import shared_task
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q

from .email_service import email_service
from .sms_service import sms_service
from apps.bookings.models import Booking


@shared_task
def send_booking_confirmation(booking_id):
    """
    Send confirmation email and SMS for booking.
    
    This task is called when a booking is confirmed.
    It sends both email and SMS (if phone available) notifications.
    
    Args:
        booking_id: ID of the booking to send confirmation for
    """
    try:
        booking = Booking.objects.select_related('client', 'trainer').get(id=booking_id)
        
        # Send email confirmation
        # Note: email_service already creates Notification record
        email_service.send_booking_confirmation(
            booking.client.email,
            booking,
            trainer=booking.trainer
        )
        
        # Send SMS confirmation if phone available
        if booking.client.phone:
            # Note: sms_service already creates Notification record
            sms_service.send_confirmation(
                booking.client.phone,
                booking,
                trainer=booking.trainer
            )
            
    except Booking.DoesNotExist:
        print(f"Booking {booking_id} not found")
    except Exception as e:
        print(f"Error sending booking confirmation for {booking_id}: {str(e)}")


@shared_task
def send_booking_reminders():
    """
    Send reminders for bookings in 24 hours.
    
    This task runs daily (scheduled via Celery Beat) to send
    reminders for bookings happening tomorrow.
    """
    try:
        # Calculate tomorrow's date range
        tomorrow = timezone.now() + timedelta(hours=24)
        start_of_day = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = tomorrow.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Get bookings happening tomorrow that are pending or confirmed
        bookings = Booking.objects.filter(
            start_time__gte=start_of_day,
            start_time__lte=end_of_day,
            status__in=['pending', 'confirmed']
        ).select_related('client', 'trainer')
        
        sent_count = 0
        for booking in bookings:
            try:
                # Send email reminder
                # Note: email_service already creates Notification record
                email_service.send_booking_reminder(
                    booking.client.email,
                    booking,
                    hours_before=24,
                    trainer=booking.trainer
                )
                
                # Send SMS reminder if phone available
                if booking.client.phone:
                    # Note: sms_service already creates Notification record
                    sms_service.send_booking_reminder(
                        booking.client.phone,
                        booking,
                        hours_before=24,
                        trainer=booking.trainer
                    )
                
                sent_count += 1
            except Exception as e:
                print(f"Error sending reminder for booking {booking.id}: {str(e)}")
        
        print(f"Sent {sent_count} booking reminders for tomorrow")
        
    except Exception as e:
        print(f"Error in send_booking_reminders task: {str(e)}")


@shared_task
def send_hour_reminders():
    """
    Send reminders for bookings in 1 hour.
    
    This task runs every 30 minutes (scheduled via Celery Beat) to send
    last-minute reminders for bookings happening soon.
    """
    try:
        # Calculate time range for bookings in the next hour
        now = timezone.now()
        in_one_hour = now + timedelta(hours=1)
        start = in_one_hour.replace(minute=0, second=0, microsecond=0)
        end = start + timedelta(hours=1)
        
        # Get bookings happening in the next hour that are pending or confirmed
        bookings = Booking.objects.filter(
            start_time__gte=start,
            start_time__lte=end,
            status__in=['pending', 'confirmed']
        ).select_related('client', 'trainer')
        
        sent_count = 0
        for booking in bookings:
            try:
                # Send SMS reminder (more urgent, so SMS preferred)
                if booking.client.phone:
                    # Note: sms_service already creates Notification record
                    sms_service.send_booking_reminder(
                        booking.client.phone,
                        booking,
                        hours_before=1,
                        trainer=booking.trainer
                    )
                    sent_count += 1
                
                # Also send email reminder
                email_service.send_booking_reminder(
                    booking.client.email,
                    booking,
                    hours_before=1,
                    trainer=booking.trainer
                )
                
            except Exception as e:
                print(f"Error sending 1-hour reminder for booking {booking.id}: {str(e)}")
        
        print(f"Sent {sent_count} 1-hour booking reminders")
        
    except Exception as e:
        print(f"Error in send_hour_reminders task: {str(e)}")


@shared_task
def send_payment_receipt(payment_id):
    """
    Send payment receipt email to trainer.
    
    This task is called when a payment is completed.
    
    Args:
        payment_id: ID of the payment to send receipt for
    """
    try:
        from apps.payments.models import Payment
        
        payment = Payment.objects.select_related(
            'subscription', 'subscription__trainer'
        ).get(id=payment_id)
        
        trainer = payment.subscription.trainer
        trainer_email = trainer.user.email
        
        # Note: email_service already creates Notification record
        email_service.send_payment_receipt(
            trainer_email,
            payment,
            trainer=trainer
        )
        
    except Payment.DoesNotExist:
        print(f"Payment {payment_id} not found")
    except Exception as e:
        print(f"Error sending payment receipt for {payment_id}: {str(e)}")


@shared_task
def retry_failed_notifications():
    """
    Retry sending failed notifications.
    
    This task runs periodically to retry notifications that failed.
    Only retries notifications that failed in the last 24 hours.
    """
    try:
        from .models import Notification
        
        # Get failed notifications from the last 24 hours
        yesterday = timezone.now() - timedelta(hours=24)
        failed_notifications = Notification.objects.filter(
            status='failed',
            created_at__gte=yesterday
        ).select_related('trainer')
        
        retry_count = 0
        for notification in failed_notifications:
            try:
                # Retry based on notification type
                if notification.notification_type == 'email':
                    # For email, we'd need to store the original context
                    # For now, just mark as pending for manual review
                    notification.status = 'pending'
                    notification.failed_reason = ''
                    notification.save()
                    retry_count += 1
                elif notification.notification_type == 'sms':
                    # Similar for SMS
                    notification.status = 'pending'
                    notification.failed_reason = ''
                    notification.save()
                    retry_count += 1
                    
            except Exception as e:
                print(f"Error retrying notification {notification.id}: {str(e)}")
        
        print(f"Retried {retry_count} failed notifications")
        
    except Exception as e:
        print(f"Error in retry_failed_notifications task: {str(e)}")

