"""
Celery configuration for TrainerHub
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('trainerhubb')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat schedule for periodic tasks
app.conf.beat_schedule = {
    'send-24h-booking-reminders': {
        'task': 'apps.notifications.tasks.send_booking_reminders',
        'schedule': crontab(hour=10, minute=0),  # Daily at 10 AM
    },
    'send-1h-booking-reminders': {
        'task': 'apps.notifications.tasks.send_hour_reminders',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
}

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

