"""
Django signals for triggering workflows
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.bookings.models import Booking
from apps.clients.models import Client
from apps.payments.models import ClientPayment
from apps.packages.models import ClientPackage
from .services import trigger_workflow


@receiver(post_save, sender=Booking)
def booking_saved(sender, instance, created, **kwargs):
    """Trigger workflows when booking is created or updated."""
    if created:
        # Booking created
        event_data = {
            'id': instance.id,
            'booking_id': instance.id,
            'client_id': instance.client.id,
            'trainer_id': instance.trainer.id,
            'client_name': f"{instance.client.first_name} {instance.client.last_name}".strip(),
            'client_email': instance.client.email,
            'client_phone': instance.client.phone_number,
            'trainer_name': instance.trainer.business_name,
            'booking_date': instance.booking_date.strftime('%Y-%m-%d'),
            'booking_time': instance.start_time.strftime('%H:%M'),
            'booking_location': instance.location or '',
        }
        trigger_workflow('booking_created', event_data)
    else:
        # Booking updated - check if status changed
        if instance.tracker.has_changed('status'):
            old_status = instance.tracker.previous('status')
            new_status = instance.status
            
            event_data = {
                'id': instance.id,
                'booking_id': instance.id,
                'client_id': instance.client.id,
                'client_name': f"{instance.client.first_name} {instance.client.last_name}".strip(),
                'client_email': instance.client.email,
                'trainer_name': instance.trainer.business_name,
                'booking_date': instance.booking_date.strftime('%Y-%m-%d'),
                'booking_time': instance.start_time.strftime('%H:%M'),
                'old_status': old_status,
                'new_status': new_status,
            }
            
            if new_status == 'confirmed':
                trigger_workflow('booking_confirmed', event_data)
            elif new_status == 'cancelled':
                event_data['cancellation_reason'] = instance.notes or 'No reason provided'
                trigger_workflow('booking_cancelled', event_data)


@receiver(post_save, sender=Client)
def client_saved(sender, instance, created, **kwargs):
    """Trigger workflows when client is created."""
    if created:
        event_data = {
            'id': instance.id,
            'client_id': instance.id,
            'trainer_id': instance.trainer.id,
            'client_name': f"{instance.first_name} {instance.last_name}".strip(),
            'client_email': instance.email,
            'client_phone': instance.phone,
            'trainer_name': instance.trainer.business_name,
        }
        trigger_workflow('client_created', event_data)


@receiver(post_save, sender=ClientPayment)
def payment_saved(sender, instance, created, **kwargs):
    """Trigger workflows when payment is recorded."""
    if created:
        event_data = {
            'id': instance.id,
            'payment_id': instance.id,
            'client_id': instance.client.id,
            'trainer_id': instance.client.trainer.id,
            'client_name': f"{instance.client.first_name} {instance.client.last_name}".strip(),
            'client_email': instance.client.email,
            'trainer_name': instance.client.trainer.business_name,
            'payment_amount': str(instance.amount),
            'payment_method': instance.payment_method,
            'payment_date': instance.payment_date.strftime('%Y-%m-%d'),
            'reference_id': instance.reference_id or '',
        }
        trigger_workflow('payment_received', event_data)


@receiver(post_save, sender=ClientPackage)
def package_saved(sender, instance, created, **kwargs):
    """Trigger workflows when client purchases a package."""
    if created:
        event_data = {
            'id': instance.id,
            'package_id': instance.id,
            'client_id': instance.client.id,
            'trainer_id': instance.client.trainer.id,
            'client_name': f"{instance.client.first_name} {instance.client.last_name}".strip(),
            'client_email': instance.client.email,
            'trainer_name': instance.client.trainer.business_name,
            'package_name': instance.package.name,
            'package_price': str(instance.package.price),
            'sessions_included': instance.package.sessions_included or 0,
        }
        trigger_workflow('package_purchased', event_data)

