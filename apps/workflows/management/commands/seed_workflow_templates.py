"""
Management command to seed pre-built workflow templates
"""
from django.core.management.base import BaseCommand
from apps.workflows.models import WorkflowTemplate


class Command(BaseCommand):
    help = 'Seed pre-built workflow templates'

    def handle(self, *args, **options):
        self.stdout.write('Seeding workflow templates...')
        
        templates = [
            {
                'name': 'Booking Confirmation Email',
                'description': 'Automatically send a confirmation email when a new booking is created',
                'category': 'booking',
                'icon': 'calendar-check',
                'trigger_type': 'booking_created',
                'trigger_delay_minutes': 0,
                'trigger_conditions': {},
                'actions_config': [
                    {
                        'action_type': 'send_email',
                        'action_data': {
                            'recipient': '',  # Will use client email
                            'subject': 'Booking Confirmed - {{booking_date}}',
                            'body': '''Hi {{client_name}},

Your booking has been confirmed!

📅 Date: {{booking_date}}
🕐 Time: {{booking_time}} - {{booking_end_time}}
📍 Location: {{booking_location}}
💼 Service: {{booking_service}}

We look forward to seeing you!

Best regards,
{{trainer_name}}'''
                        },
                        'order': 0
                    }
                ]
            },
            {
                'name': '24-Hour Booking Reminder',
                'description': 'Send a reminder email 24 hours before a booking',
                'category': 'reminder',
                'icon': 'bell',
                'trigger_type': 'booking_reminder',
                'trigger_delay_minutes': -1440,  # 24 hours before
                'trigger_conditions': {},
                'actions_config': [
                    {
                        'action_type': 'send_email',
                        'action_data': {
                            'recipient': '',
                            'subject': 'Reminder: Your session tomorrow',
                            'body': '''Hi {{client_name}},

Just a friendly reminder about your upcoming session:

📅 Tomorrow: {{booking_date}}
🕐 Time: {{booking_time}}
📍 Location: {{booking_location}}

See you soon!

{{trainer_name}}'''
                        },
                        'order': 0
                    }
                ]
            },
            {
                'name': 'Payment Received Confirmation',
                'description': 'Send a thank you email when payment is received',
                'category': 'payment',
                'icon': 'dollar-sign',
                'trigger_type': 'payment_received',
                'trigger_delay_minutes': 0,
                'trigger_conditions': {},
                'actions_config': [
                    {
                        'action_type': 'send_email',
                        'action_data': {
                            'recipient': '',
                            'subject': 'Payment Received - Thank You!',
                            'body': '''Hi {{client_name}},

Thank you for your payment!

💰 Amount: {{payment_amount}}
💳 Payment Method: {{payment_method}}

Your payment has been successfully processed.

Best regards,
{{trainer_name}}'''
                        },
                        'order': 0
                    }
                ]
            },
            {
                'name': 'Welcome New Client',
                'description': 'Send a welcome email to new clients',
                'category': 'client',
                'icon': 'user-plus',
                'trigger_type': 'client_created',
                'trigger_delay_minutes': 0,
                'trigger_conditions': {},
                'actions_config': [
                    {
                        'action_type': 'send_email',
                        'action_data': {
                            'recipient': '',
                            'subject': 'Welcome to {{trainer_name}}!',
                            'body': '''Hi {{client_name}},

Welcome! We're excited to have you as a client.

I'm looking forward to helping you achieve your fitness goals. Feel free to reach out if you have any questions.

To get started, book your first session at your convenience.

Best regards,
{{trainer_name}}
{{trainer_email}}
{{trainer_phone}}'''
                        },
                        'order': 0
                    }
                ]
            },
            {
                'name': 'Booking Cancellation Notice',
                'description': 'Notify client when a booking is cancelled',
                'category': 'booking',
                'icon': 'x-circle',
                'trigger_type': 'booking_cancelled',
                'trigger_delay_minutes': 0,
                'trigger_conditions': {},
                'actions_config': [
                    {
                        'action_type': 'send_email',
                        'action_data': {
                            'recipient': '',
                            'subject': 'Booking Cancelled - {{booking_date}}',
                            'body': '''Hi {{client_name}},

This is to confirm that your booking has been cancelled:

📅 Date: {{booking_date}}
🕐 Time: {{booking_time}}
📍 Location: {{booking_location}}

If you'd like to reschedule, please book a new session at your convenience.

Best regards,
{{trainer_name}}'''
                        },
                        'order': 0
                    }
                ]
            },
            {
                'name': 'Package Purchase Thank You',
                'description': 'Thank clients for purchasing a package',
                'category': 'payment',
                'icon': 'package',
                'trigger_type': 'package_purchased',
                'trigger_delay_minutes': 0,
                'trigger_conditions': {},
                'actions_config': [
                    {
                        'action_type': 'send_email',
                        'action_data': {
                            'recipient': '',
                            'subject': 'Thank You for Your Package Purchase!',
                            'body': '''Hi {{client_name}},

Thank you for purchasing a package!

📦 Package: {{package_name}}
🎯 Sessions: {{package_sessions}}

You can now book your sessions at your convenience. I'm excited to work with you!

Best regards,
{{trainer_name}}'''
                        },
                        'order': 0
                    }
                ]
            },
            {
                'name': 'Pre-Session SMS Reminder',
                'description': 'Send an SMS reminder 2 hours before a session',
                'category': 'reminder',
                'icon': 'message-square',
                'trigger_type': 'booking_reminder',
                'trigger_delay_minutes': -120,  # 2 hours before
                'trigger_conditions': {},
                'actions_config': [
                    {
                        'action_type': 'send_sms',
                        'action_data': {
                            'recipient': '',
                            'message': 'Hi {{client_name}}! Reminder: Session today at {{booking_time}} - {{booking_location}}. See you soon! - {{trainer_name}}'
                        },
                        'order': 0
                    }
                ]
            },
            {
                'name': 'Booking Confirmed Status Update',
                'description': 'Automatically update booking status to confirmed and send email',
                'category': 'booking',
                'icon': 'check-square',
                'trigger_type': 'booking_created',
                'trigger_delay_minutes': 0,
                'trigger_conditions': {},
                'actions_config': [
                    {
                        'action_type': 'update_status',
                        'action_data': {
                            'model_type': 'booking',
                            'status': 'confirmed'
                        },
                        'order': 0
                    },
                    {
                        'action_type': 'send_email',
                        'action_data': {
                            'recipient': '',
                            'subject': 'Booking Confirmed!',
                            'body': 'Hi {{client_name}}, Your booking for {{booking_date}} at {{booking_time}} is confirmed!'
                        },
                        'order': 1
                    }
                ]
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for template_data in templates:
            template, created = WorkflowTemplate.objects.update_or_create(
                name=template_data['name'],
                defaults=template_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created: {template.name}'))
            else:
                updated_count += 1
                self.stdout.write(f'  Updated: {template.name}')
        
        self.stdout.write(self.style.SUCCESS(
            f'\nSeeding complete! Created: {created_count}, Updated: {updated_count}'
        ))

