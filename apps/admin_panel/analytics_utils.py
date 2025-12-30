"""
Analytics utilities for Epic 0.4: Analytics Dashboard
Provides data aggregation functions for charts and visualizations.
"""
from django.db.models import Count, Sum, Q, Avg
from django.utils import timezone
from datetime import timedelta, datetime
from collections import defaultdict
from decimal import Decimal

from apps.trainers.models import Trainer
from apps.clients.models import Client
from apps.bookings.models import Booking


def get_revenue_trends(days=30, group_by='day'):
    """
    Get revenue trends over time.
    
    Args:
        days: Number of days to look back (default: 30)
        group_by: 'day' or 'month' for grouping
    
    Returns:
        List of dicts with date and revenue amount
        Format: [{'date': '2024-01-01', 'revenue': 1500.00}, ...]
    """
    try:
        from apps.payments.models import Payment, Subscription
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Get all completed payments in the date range
        payments = Payment.objects.filter(
            status='completed',
            created_at__gte=start_date,
            created_at__lte=end_date
        ).order_by('created_at')
        
        # Group by day or month
        revenue_by_period = defaultdict(Decimal)
        
        for payment in payments:
            if group_by == 'day':
                key = payment.created_at.date().isoformat()
            else:  # month
                key = payment.created_at.strftime('%Y-%m')
            
            revenue_by_period[key] += payment.amount
        
        # Convert to list sorted by date
        result = [
            {'date': date, 'revenue': float(amount)}
            for date, amount in sorted(revenue_by_period.items())
        ]
        
        return result
        
    except Exception as e:
        # If payments app not available, return empty list
        return []


def get_signup_trends(days=30, group_by='day'):
    """
    Get trainer signup trends over time.
    
    Args:
        days: Number of days to look back (default: 30)
        group_by: 'day' or 'month' for grouping
    
    Returns:
        List of dicts with date and signup count
        Format: [{'date': '2024-01-01', 'signups': 5}, ...]
    """
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    # Get all trainers created in the date range
    trainers = Trainer.objects.filter(
        created_at__gte=start_date,
        created_at__lte=end_date
    ).order_by('created_at')
    
    # Group by day or month
    signups_by_period = defaultdict(int)
    
    for trainer in trainers:
        if group_by == 'day':
            key = trainer.created_at.date().isoformat()
        else:  # month
            key = trainer.created_at.strftime('%Y-%m')
        
        signups_by_period[key] += 1
    
    # Convert to list sorted by date
    result = [
        {'date': date, 'signups': count}
        for date, count in sorted(signups_by_period.items())
    ]
    
    return result


def get_active_users_over_time(days=30, group_by='day'):
    """
    Get active users (trainers) count over time.
    Active = trainers with at least one booking in the period.
    
    Args:
        days: Number of days to look back (default: 30)
        group_by: 'day' or 'month' for grouping
    
    Returns:
        List of dicts with date and active user count
        Format: [{'date': '2024-01-01', 'active_users': 45}, ...]
    """
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    # Get bookings grouped by date
    bookings = Booking.objects.filter(
        start_time__gte=start_date,
        start_time__lte=end_date
    ).order_by('start_time')
    
    # Group by day or month and count unique trainers
    active_users_by_period = defaultdict(set)
    
    for booking in bookings:
        if group_by == 'day':
            key = booking.start_time.date().isoformat()
        else:  # month
            key = booking.start_time.strftime('%Y-%m')
        
        active_users_by_period[key].add(booking.trainer_id)
    
    # Convert to list sorted by date
    result = [
        {'date': date, 'active_users': len(trainer_ids)}
        for date, trainer_ids in sorted(active_users_by_period.items())
    ]
    
    return result


def get_geographic_distribution():
    """
    Get geographic distribution of trainers.
    
    Returns:
        List of dicts with location and trainer count
        Format: [{'location': 'New York, NY', 'count': 15}, ...]
    """
    # Get trainers with location data
    trainers = Trainer.objects.exclude(
        Q(location__isnull=True) | Q(location='')
    ).values('location').annotate(
        count=Count('id')
    ).order_by('-count')
    
    result = [
        {'location': item['location'], 'count': item['count']}
        for item in trainers
    ]
    
    return result


def get_revenue_by_plan():
    """
    Get revenue breakdown by subscription plan.
    Note: Plan information may need to be inferred from Paddle subscription data.
    
    Returns:
        List of dicts with plan and revenue
        Format: [{'plan': 'pro', 'revenue': 5000.00}, ...]
    """
    try:
        from apps.payments.models import Payment, Subscription
        
        # Get all completed payments
        payments = Payment.objects.filter(
            status='completed'
        ).select_related('subscription')
        
        # Since Subscription model doesn't have a plan field,
        # we'll group by subscription status or return total revenue
        # In production, plan info would come from Paddle API
        revenue_by_status = defaultdict(Decimal)
        
        for payment in payments:
            status = payment.subscription.status if payment.subscription else 'unknown'
            revenue_by_status[status] += payment.amount
        
        # Convert to list
        result = [
            {'plan': status, 'revenue': float(amount)}
            for status, amount in sorted(revenue_by_status.items())
        ]
        
        return result
        
    except Exception:
        return []


def get_booking_trends(days=30, group_by='day'):
    """
    Get booking trends over time.
    
    Args:
        days: Number of days to look back (default: 30)
        group_by: 'day' or 'month' for grouping
    
    Returns:
        List of dicts with date and booking count
        Format: [{'date': '2024-01-01', 'bookings': 25}, ...]
    """
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    # Get all bookings in the date range
    bookings = Booking.objects.filter(
        start_time__gte=start_date,
        start_time__lte=end_date
    ).order_by('start_time')
    
    # Group by day or month
    bookings_by_period = defaultdict(int)
    
    for booking in bookings:
        if group_by == 'day':
            key = booking.start_time.date().isoformat()
        else:  # month
            key = booking.start_time.strftime('%Y-%m')
        
        bookings_by_period[key] += 1
    
    # Convert to list sorted by date
    result = [
        {'date': date, 'bookings': count}
        for date, count in sorted(bookings_by_period.items())
    ]
    
    return result


def get_client_growth_trends(days=30, group_by='day'):
    """
    Get client growth trends over time.
    
    Args:
        days: Number of days to look back (default: 30)
        group_by: 'day' or 'month' for grouping
    
    Returns:
        List of dicts with date and new client count
        Format: [{'date': '2024-01-01', 'new_clients': 10}, ...]
    """
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    # Get all clients created in the date range
    clients = Client.objects.filter(
        created_at__gte=start_date,
        created_at__lte=end_date,
        is_active=True
    ).order_by('created_at')
    
    # Group by day or month
    clients_by_period = defaultdict(int)
    
    for client in clients:
        if group_by == 'day':
            key = client.created_at.date().isoformat()
        else:  # month
            key = client.created_at.strftime('%Y-%m')
        
        clients_by_period[key] += 1
    
    # Convert to list sorted by date
    result = [
        {'date': date, 'new_clients': count}
        for date, count in sorted(clients_by_period.items())
    ]
    
    return result


def get_top_performing_trainers(limit=10):
    """
    Get top performing trainers by revenue or bookings.
    
    Args:
        limit: Number of trainers to return (default: 10)
    
    Returns:
        List of dicts with trainer info and metrics
    """
    try:
        from apps.payments.models import Payment, Subscription
        
        # Get trainers with their revenue
        # Note: Using select_related and prefetch_related for optimization
        trainers = Trainer.objects.select_related('user').prefetch_related(
            'subscription__payments'
        ).annotate(
            total_revenue=Sum(
                'subscription__payments__amount',
                filter=Q(subscription__payments__status='completed')
            ),
            total_bookings=Count('bookings')
        ).order_by('-total_revenue')[:limit]
        
        result = []
        for trainer in trainers:
            result.append({
                'trainer_id': trainer.id,
                'business_name': trainer.business_name,
                'email': trainer.user.email,
                'total_revenue': float(trainer.total_revenue or 0),
                'total_bookings': trainer.total_bookings or 0,
                'location': trainer.location or 'N/A'
            })
        
        return result
        
    except Exception:
        # Fallback to bookings only
        trainers = Trainer.objects.annotate(
            total_bookings=Count('bookings')
        ).order_by('-total_bookings')[:limit]
        
        result = []
        for trainer in trainers:
            result.append({
                'trainer_id': trainer.id,
                'business_name': trainer.business_name,
                'email': trainer.user.email,
                'total_revenue': 0.0,
                'total_bookings': trainer.total_bookings or 0,
                'location': trainer.location or 'N/A'
            })
        
        return result

