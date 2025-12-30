"""
Export utilities for admin panel.
Generate CSV and Excel exports of trainer data.
"""
import csv
import io
from datetime import datetime
from django.http import HttpResponse


def export_trainers_csv(trainers):
    """
    Export trainers to CSV format.
    
    Args:
        trainers: QuerySet of Trainer objects
        
    Returns:
        HttpResponse with CSV file
    """
    response = HttpResponse(content_type='text/csv')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="trainers_export_{timestamp}.csv"'
    
    writer = csv.writer(response)
    
    # Header row
    writer.writerow([
        'ID',
        'Business Name',
        'Email',
        'User Active',
        'Is Verified',
        'Location',
        'Timezone',
        'Rating',
        'Total Sessions',
        'Total Clients',
        'Total Bookings',
        'Subscription Plan',
        'Subscription Status',
        'Custom Domain',
        'Created At',
        'Updated At'
    ])
    
    # Data rows
    for trainer in trainers:
        # Get subscription info
        try:
            from apps.payments.models import Subscription
            subscription = Subscription.objects.filter(trainer=trainer).first()
            sub_plan = subscription.plan if subscription else 'free'
            sub_status = subscription.status if subscription else 'free'
        except:
            sub_plan = 'free'
            sub_status = 'free'
        
        # Get custom domain
        try:
            from apps.payments.models import CustomDomain
            domain = CustomDomain.objects.filter(trainer=trainer, status='active').first()
            custom_domain = domain.domain if domain else ''
        except:
            custom_domain = ''
        
        # Get counts
        total_clients = trainer.clients.filter(is_active=True).count()
        total_bookings = trainer.bookings.count()
        
        writer.writerow([
            trainer.id,
            trainer.business_name,
            trainer.user.email,
            'Yes' if trainer.user.is_active else 'No',
            'Yes' if trainer.is_verified else 'No',
            trainer.location,
            trainer.timezone,
            trainer.rating,
            trainer.total_sessions,
            total_clients,
            total_bookings,
            sub_plan,
            sub_status,
            custom_domain,
            trainer.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            trainer.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return response


def export_trainer_detail_csv(trainer):
    """
    Export detailed trainer information including clients and bookings.
    
    Args:
        trainer: Trainer object
        
    Returns:
        HttpResponse with CSV file
    """
    response = HttpResponse(content_type='text/csv')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"trainer_{trainer.id}_{trainer.business_name.replace(' ', '_')}_{timestamp}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    writer = csv.writer(response)
    
    # Trainer info section
    writer.writerow(['TRAINER INFORMATION'])
    writer.writerow(['Field', 'Value'])
    writer.writerow(['ID', trainer.id])
    writer.writerow(['Business Name', trainer.business_name])
    writer.writerow(['Email', trainer.user.email])
    writer.writerow(['Location', trainer.location])
    writer.writerow(['Timezone', trainer.timezone])
    writer.writerow(['Rating', trainer.rating])
    writer.writerow(['Total Sessions', trainer.total_sessions])
    writer.writerow(['Is Verified', 'Yes' if trainer.is_verified else 'No'])
    writer.writerow(['Account Active', 'Yes' if trainer.user.is_active else 'No'])
    writer.writerow([])
    
    # Clients section
    writer.writerow(['CLIENTS'])
    writer.writerow(['ID', 'Name', 'Email', 'Phone', 'Fitness Level', 'Created'])
    for client in trainer.clients.filter(is_active=True)[:100]:
        writer.writerow([
            client.id,
            client.get_full_name(),
            client.email,
            client.phone,
            client.fitness_level,
            client.created_at.strftime('%Y-%m-%d')
        ])
    writer.writerow([])
    
    # Bookings section
    writer.writerow(['RECENT BOOKINGS'])
    writer.writerow(['ID', 'Client', 'Start Time', 'End Time', 'Status', 'Duration (min)'])
    for booking in trainer.bookings.order_by('-start_time')[:100]:
        writer.writerow([
            booking.id,
            booking.client.get_full_name(),
            booking.start_time.strftime('%Y-%m-%d %H:%M'),
            booking.end_time.strftime('%Y-%m-%d %H:%M'),
            booking.status,
            booking.duration_minutes
        ])
    
    return response


def export_platform_stats_csv(stats_data):
    """
    Export platform statistics to CSV.
    
    Args:
        stats_data: Dictionary of platform statistics
        
    Returns:
        HttpResponse with CSV file
    """
    response = HttpResponse(content_type='text/csv')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="platform_stats_{timestamp}.csv"'
    
    writer = csv.writer(response)
    
    writer.writerow(['PLATFORM STATISTICS'])
    writer.writerow(['Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow([])
    
    writer.writerow(['Metric', 'Value'])
    writer.writerow(['Total Trainers', stats_data.get('total_trainers', 0)])
    writer.writerow(['Active Trainers', stats_data.get('active_trainers', 0)])
    writer.writerow(['Total Clients', stats_data.get('total_clients', 0)])
    writer.writerow(['Total Bookings', stats_data.get('total_bookings', 0)])
    writer.writerow(['New Signups This Month', stats_data.get('new_signups_this_month', 0)])
    writer.writerow(['Monthly Revenue', f"${stats_data.get('total_revenue_this_month', 0)}"])
    writer.writerow(['MRR', f"${stats_data.get('mrr', 0)}"])
    writer.writerow(['Churn Rate', f"{stats_data.get('churn_rate', 0)}%"])
    writer.writerow([])
    
    # Subscription breakdown
    writer.writerow(['SUBSCRIPTION BREAKDOWN'])
    writer.writerow(['Plan', 'Count'])
    for plan, count in stats_data.get('subscription_breakdown', {}).items():
        writer.writerow([plan.capitalize(), count])
    
    return response

