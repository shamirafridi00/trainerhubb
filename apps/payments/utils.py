"""
Utility functions for revenue calculations and reporting.
"""
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import ClientPayment


def get_revenue_by_period(trainer, start_date, end_date):
    """
    Calculate total revenue for a trainer within a date range.
    
    Args:
        trainer: Trainer instance
        start_date: Start date (datetime or date)
        end_date: End date (datetime or date)
    
    Returns:
        dict: {
            'total': Decimal,
            'count': int,
            'by_method': {method: amount},
            'by_currency': {currency: amount}
        }
    """
    from apps.clients.models import Client
    
    client_ids = Client.objects.filter(trainer=trainer).values_list('id', flat=True)
    
    payments = ClientPayment.objects.filter(
        client_id__in=client_ids,
        payment_date__gte=start_date,
        payment_date__lte=end_date
    )
    
    total = payments.aggregate(Sum('amount'))['amount__sum'] or 0
    count = payments.count()
    
    # Revenue by payment method
    by_method = {}
    for method, _ in ClientPayment.PAYMENT_METHODS:
        method_total = payments.filter(payment_method=method).aggregate(Sum('amount'))['amount__sum'] or 0
        if method_total > 0:
            by_method[method] = float(method_total)
    
    # Revenue by currency
    by_currency = {}
    for currency in payments.values_list('currency', flat=True).distinct():
        currency_total = payments.filter(currency=currency).aggregate(Sum('amount'))['amount__sum'] or 0
        if currency_total > 0:
            by_currency[currency] = float(currency_total)
    
    return {
        'total': float(total),
        'count': count,
        'by_method': by_method,
        'by_currency': by_currency,
    }


def get_revenue_summary(trainer):
    """
    Get revenue summary for a trainer (this month, last month, all time).
    
    Returns:
        dict: {
            'this_month': {...},
            'last_month': {...},
            'all_time': {...},
            'unpaid_clients': {
                'count': int,
                'total_amount': Decimal
            }
        }
    """
    now = timezone.now().date()
    this_month_start = now.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = this_month_start - timedelta(days=1)
    
    this_month = get_revenue_by_period(trainer, this_month_start, now)
    last_month = get_revenue_by_period(trainer, last_month_start, last_month_end)
    # For all time, use a very early date
    all_time_start = timezone.now().date().replace(year=2000, month=1, day=1)
    all_time = get_revenue_by_period(trainer, all_time_start, now)
    
    # Unpaid clients
    from apps.clients.models import Client
    unpaid_clients = Client.objects.filter(
        trainer=trainer,
        payment_status__in=['unpaid', 'partial']
    )
    unpaid_count = unpaid_clients.count()
    unpaid_total = sum(float(client.total_paid or 0) for client in unpaid_clients)
    
    return {
        'this_month': this_month,
        'last_month': last_month,
        'all_time': all_time,
        'unpaid_clients': {
            'count': unpaid_count,
            'total_amount': unpaid_total,
        }
    }


def get_recent_payments(trainer, limit=10):
    """
    Get recent payments for a trainer.
    
    Args:
        trainer: Trainer instance
        limit: Number of payments to return
    
    Returns:
        QuerySet: Recent ClientPayment objects
    """
    from apps.clients.models import Client
    
    client_ids = Client.objects.filter(trainer=trainer).values_list('id', flat=True)
    
    return ClientPayment.objects.filter(
        client_id__in=client_ids
    ).select_related('client', 'recorded_by').order_by('-payment_date', '-created_at')[:limit]

