"""
Frontend views for HTMX - Template-based views that work alongside DRF API.
DRF endpoints remain available for future React Native app.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta

from apps.bookings.models import Booking
from apps.clients.models import Client
from apps.packages.models import SessionPackage
from apps.payments.models import Payment
from apps.notifications.models import Notification
from apps.trainers.models import Trainer
from django.db.models import Sum, Count
from datetime import timedelta


def landing(request):
    """Landing page for unauthenticated users."""
    if request.user.is_authenticated:
        return redirect('frontend:dashboard')
    return render(request, 'pages/landing.html')


@login_required
def dashboard(request):
    """Main dashboard page."""
    return render(request, 'pages/dashboard.html')


@login_required
def dashboard_stats(request):
    """Dashboard stats partial for HTMX."""
    try:
        trainer = request.user.trainer_profile
    except Trainer.DoesNotExist:
        return render(request, 'partials/dashboard/stats.html', {'stats': []})
    
    now = timezone.now()
    today = now.date()
    this_month = today.replace(day=1)
    last_month = (this_month - timedelta(days=1)).replace(day=1)
    
    # Get stats
    bookings = Booking.objects.filter(trainer=trainer)
    clients = Client.objects.filter(trainer=trainer)
    payments = Payment.objects.filter(subscription__trainer=trainer, status='completed')
    
    # Calculate current month stats
    total_bookings = bookings.count()
    upcoming_bookings = bookings.filter(
        status__in=['pending', 'confirmed'],
        start_time__gte=now
    ).count()
    total_clients = clients.count()
    total_revenue = payments.aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Calculate last month for comparison
    last_month_bookings = bookings.filter(
        created_at__gte=last_month,
        created_at__lt=this_month
    ).count()
    
    last_month_clients = clients.filter(
        created_at__gte=last_month,
        created_at__lt=this_month
    ).count()
    
    # Calculate percentage changes
    booking_change = 0
    if last_month_bookings > 0:
        booking_change = round(((total_bookings - last_month_bookings) / last_month_bookings) * 100, 1)
    
    client_change = 0
    if last_month_clients > 0:
        client_change = round(((total_clients - last_month_clients) / last_month_clients) * 100, 1)
    
    stats = [
        {
            'label': 'Total Bookings',
            'value': total_bookings,
            'color': 'indigo',
            'icon': 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z',
            'change': booking_change
        },
        {
            'label': 'Upcoming',
            'value': upcoming_bookings,
            'color': 'green',
            'icon': 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z',
        },
        {
            'label': 'Total Clients',
            'value': total_clients,
            'color': 'purple',
            'icon': 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z',
            'change': client_change
        },
        {
            'label': 'Total Revenue',
            'value': f"${total_revenue:,.2f}",
            'color': 'pink',
            'icon': 'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
        },
    ]
    
    return render(request, 'partials/dashboard/stats.html', {'stats': stats})


@login_required
def bookings_upcoming_partial(request):
    """Upcoming bookings partial for dashboard."""
    try:
        trainer = request.user.trainer_profile
    except Trainer.DoesNotExist:
        return render(request, 'partials/bookings/upcoming.html', {'bookings': []})
    
    bookings = Booking.objects.filter(
        trainer=trainer,
        status__in=['pending', 'confirmed'],
        start_time__gte=timezone.now()
    ).select_related('client').order_by('start_time')[:5]
    
    return render(request, 'partials/bookings/upcoming.html', {'bookings': bookings})


@login_required
def clients_recent_partial(request):
    """Recent clients partial for dashboard."""
    try:
        trainer = request.user.trainer_profile
    except Trainer.DoesNotExist:
        return render(request, 'partials/clients/recent.html', {'clients': []})
    
    clients = Client.objects.filter(trainer=trainer).order_by('-created_at')[:5]
    
    return render(request, 'partials/clients/recent.html', {'clients': clients})


@login_required
def analytics_revenue_chart(request):
    """Revenue chart partial for dashboard."""
    try:
        trainer = request.user.trainer_profile
    except Trainer.DoesNotExist:
        return render(request, 'partials/analytics/revenue_chart.html', {
            'total_revenue': 0,
            'monthly_revenue': 0,
            'average_booking_value': 0,
            'monthly_data': []
        })
    
    now = timezone.now()
    this_month = now.date().replace(day=1)
    
    # Get payment data
    payments = Payment.objects.filter(subscription__trainer=trainer, status='completed')
    total_revenue = payments.aggregate(Sum('amount'))['amount__sum'] or 0
    monthly_revenue = payments.filter(created_at__gte=this_month).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Calculate average booking value
    bookings = Booking.objects.filter(trainer=trainer, status='completed')
    average_booking_value = 0
    if bookings.exists():
        average_booking_value = float(total_revenue) / bookings.count()
    
    # Get last 6 months of revenue data
    monthly_data = []
    max_revenue = 0
    
    for i in range(6):
        month_start = (this_month - timedelta(days=30*i)).replace(day=1)
        if i > 0:
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        else:
            month_end = now.date()
        
        month_revenue = payments.filter(
            created_at__date__gte=month_start,
            created_at__date__lte=month_end
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        if month_revenue > max_revenue:
            max_revenue = float(month_revenue)
        
        monthly_data.append({
            'month': month_start.strftime('%B %Y'),
            'month_short': month_start.strftime('%b'),
            'revenue': float(month_revenue)
        })
    
    # Reverse to show oldest first
    monthly_data.reverse()
    
    # Calculate percentages for bar chart
    for data in monthly_data:
        if max_revenue > 0:
            data['percentage'] = int((data['revenue'] / max_revenue) * 100)
        else:
            data['percentage'] = 0
    
    return render(request, 'partials/analytics/revenue_chart.html', {
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
        'average_booking_value': average_booking_value,
        'monthly_data': monthly_data
    })


@login_required
def bookings_list(request):
    """Bookings list page."""
    return render(request, 'pages/bookings/list.html')


@login_required
def bookings_list_partial(request):
    """Bookings list partial for HTMX."""
    try:
        trainer = request.user.trainer_profile
    except Trainer.DoesNotExist:
        return render(request, 'partials/bookings/list.html', {'bookings': []})
    
    bookings = Booking.objects.filter(trainer=trainer).select_related('client').order_by('-start_time')
    
    # Filters
    status = request.GET.get('status')
    if status:
        bookings = bookings.filter(status=status)
    
    date_str = request.GET.get('date')
    if date_str:
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            bookings = bookings.filter(start_time__date=date)
        except ValueError:
            pass
    
    # Limit to recent bookings for performance
    bookings = bookings[:50]
    
    return render(request, 'partials/bookings/list.html', {'bookings': bookings})


@login_required
def bookings_create_form(request):
    """Booking creation form partial for HTMX modal."""
    try:
        trainer = request.user.trainer_profile
        clients = Client.objects.filter(trainer=trainer, is_active=True).order_by('first_name', 'last_name')
    except Trainer.DoesNotExist:
        clients = Client.objects.none()
    
    return render(request, 'partials/bookings/form.html', {'clients': clients})


@login_required
@require_http_methods(["POST"])
def bookings_create(request):
    """Create booking via HTMX."""
    try:
        trainer = request.user.trainer_profile
    except Trainer.DoesNotExist:
        return JsonResponse({'error': 'Trainer profile not found'}, status=400)
    
    client_id = request.POST.get('client')
    start_time_str = request.POST.get('start_time')
    duration_minutes = int(request.POST.get('duration_minutes', 60))
    notes = request.POST.get('notes', '')
    
    if not all([client_id, start_time_str]):
        return render(request, 'partials/bookings/form.html', {
            'clients': Client.objects.filter(trainer=trainer, is_active=True),
            'error': 'Client and start time are required'
        })
    
    try:
        client = Client.objects.get(id=client_id, trainer=trainer)
        # Parse datetime-local format (YYYY-MM-DDTHH:MM)
        try:
            start_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            # Try with seconds if provided
            start_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M:%S')
        
        # Make timezone-aware
        if timezone.is_naive(start_time):
            start_time = timezone.make_aware(start_time)
        
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        # Create booking
        booking = Booking.objects.create(
            trainer=trainer,
            client=client,
            start_time=start_time,
            end_time=end_time,
            notes=notes,
            status='pending'
        )
        
        # Trigger notification asynchronously
        from apps.notifications.tasks import send_booking_confirmation
        send_booking_confirmation.delay(booking.id)
        
        # Return updated list
        return bookings_list_partial(request)
    except Client.DoesNotExist:
        return render(request, 'partials/bookings/form.html', {
            'clients': Client.objects.filter(trainer=trainer, is_active=True),
            'error': 'Client not found'
        })
    except Exception as e:
        return render(request, 'partials/bookings/form.html', {
            'clients': Client.objects.filter(trainer=trainer, is_active=True),
            'error': str(e)
        })


@login_required
def bookings_detail(request, booking_id):
    """Booking detail partial for HTMX modal."""
    booking = get_object_or_404(Booking, id=booking_id, trainer=request.user.trainer_profile)
    return render(request, 'partials/bookings/detail.html', {'booking': booking})


@login_required
@require_http_methods(["POST"])
def bookings_confirm(request, booking_id):
    """Confirm booking via HTMX."""
    booking = get_object_or_404(Booking, id=booking_id, trainer=request.user.trainer_profile)
    
    if booking.status == 'pending':
        booking.status = 'confirmed'
        booking.save()
        
        # Trigger notification asynchronously
        from apps.notifications.tasks import send_booking_confirmation
        send_booking_confirmation.delay(booking.id)
    
    # Return updated list
    return bookings_list_partial(request)


@login_required
@require_http_methods(["POST"])
def bookings_cancel(request, booking_id):
    """Cancel booking via HTMX."""
    booking = get_object_or_404(Booking, id=booking_id, trainer=request.user.trainer_profile)
    
    if booking.status not in ['completed', 'cancelled']:
        booking.status = 'cancelled'
        booking.cancellation_reason = request.POST.get('reason', 'Cancelled by trainer')
        booking.save()
    
    # Return updated list
    return bookings_list_partial(request)


@login_required
@require_http_methods(["POST"])
def bookings_mark_completed(request, booking_id):
    """Mark booking as completed via HTMX."""
    booking = get_object_or_404(Booking, id=booking_id, trainer=request.user.trainer_profile)
    
    if booking.status == 'confirmed':
        booking.status = 'completed'
        booking.save()
    
    # Return updated list
    return bookings_list_partial(request)


@login_required
def clients_list(request):
    """Clients list page."""
    return render(request, 'pages/clients/list.html')


@login_required
def clients_list_partial(request):
    """Clients list partial for HTMX."""
    try:
        trainer = request.user.trainer_profile
    except Trainer.DoesNotExist:
        return render(request, 'partials/clients/list.html', {'clients': []})
    
    clients = Client.objects.filter(trainer=trainer).order_by('-created_at')
    
    # Filters
    fitness_level = request.GET.get('fitness_level')
    if fitness_level:
        clients = clients.filter(fitness_level=fitness_level)
    
    is_active = request.GET.get('is_active')
    if is_active == 'true':
        clients = clients.filter(is_active=True)
    elif is_active == 'false':
        clients = clients.filter(is_active=False)
    
    return render(request, 'partials/clients/list.html', {'clients': clients})


@login_required
def clients_create_form(request):
    """Client creation form partial for HTMX modal."""
    return render(request, 'partials/clients/form.html', {'client': None})


@login_required
@require_http_methods(["POST"])
def clients_create(request):
    """Create client via HTMX."""
    try:
        trainer = request.user.trainer_profile
    except Trainer.DoesNotExist:
        return JsonResponse({'error': 'Trainer profile not found'}, status=400)
    
    try:
        client = Client.objects.create(
            trainer=trainer,
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone', ''),
            fitness_level=request.POST.get('fitness_level', 'beginner'),
            notes=request.POST.get('notes', ''),
            is_active=True
        )
        return clients_list_partial(request)
    except Exception as e:
        return render(request, 'partials/clients/form.html', {
            'client': None,
            'error': str(e)
        })


@login_required
def clients_detail(request, client_id):
    """Client detail partial for HTMX modal."""
    client = get_object_or_404(Client, id=client_id, trainer=request.user.trainer_profile)
    return render(request, 'partials/clients/detail.html', {'client': client})


@login_required
def clients_edit_form(request, client_id):
    """Client edit form partial for HTMX modal."""
    client = get_object_or_404(Client, id=client_id, trainer=request.user.trainer_profile)
    return render(request, 'partials/clients/form.html', {'client': client})


@login_required
@require_http_methods(["POST"])
def clients_update(request, client_id):
    """Update client via HTMX."""
    client = get_object_or_404(Client, id=client_id, trainer=request.user.trainer_profile)
    
    client.first_name = request.POST.get('first_name')
    client.last_name = request.POST.get('last_name')
    client.email = request.POST.get('email')
    client.phone = request.POST.get('phone', '')
    client.fitness_level = request.POST.get('fitness_level', 'beginner')
    client.notes = request.POST.get('notes', '')
    client.is_active = request.POST.get('is_active') == 'on'
    client.save()
    
    return clients_list_partial(request)


@login_required
def packages_list(request):
    """Packages list page."""
    return render(request, 'pages/packages/list.html')


@login_required
def packages_list_partial(request):
    """Packages list partial for HTMX."""
    try:
        trainer = request.user.trainer_profile
    except Trainer.DoesNotExist:
        return render(request, 'partials/packages/list.html', {'packages': []})
    
    packages = SessionPackage.objects.filter(trainer=trainer).order_by('-created_at')
    
    is_active = request.GET.get('is_active')
    if is_active == 'true':
        packages = packages.filter(is_active=True)
    elif is_active == 'false':
        packages = packages.filter(is_active=False)
    
    return render(request, 'partials/packages/list.html', {'packages': packages})


@login_required
def packages_create_form(request):
    """Package creation form partial for HTMX modal."""
    return render(request, 'partials/packages/form.html', {'package': None})


@login_required
@require_http_methods(["POST"])
def packages_create(request):
    """Create package via HTMX."""
    try:
        trainer = request.user.trainer_profile
    except Trainer.DoesNotExist:
        return JsonResponse({'error': 'Trainer profile not found'}, status=400)
    
    try:
        package = SessionPackage.objects.create(
            trainer=trainer,
            name=request.POST.get('name'),
            description=request.POST.get('description', ''),
            sessions_count=int(request.POST.get('sessions_count', 1)),
            price=float(request.POST.get('price', 0)),
            is_active=request.POST.get('is_active') == 'on'
        )
        return packages_list_partial(request)
    except Exception as e:
        return render(request, 'partials/packages/form.html', {
            'package': None,
            'error': str(e)
        })


@login_required
def packages_edit_form(request, package_id):
    """Package edit form partial for HTMX modal."""
    package = get_object_or_404(SessionPackage, id=package_id, trainer=request.user.trainer_profile)
    return render(request, 'partials/packages/form.html', {'package': package})


@login_required
@require_http_methods(["POST"])
def packages_update(request, package_id):
    """Update package via HTMX."""
    package = get_object_or_404(SessionPackage, id=package_id, trainer=request.user.trainer_profile)
    
    package.name = request.POST.get('name')
    package.description = request.POST.get('description', '')
    package.sessions_count = int(request.POST.get('sessions_count', 1))
    package.price = float(request.POST.get('price', 0))
    package.is_active = request.POST.get('is_active') == 'on'
    package.save()
    
    return packages_list_partial(request)


@login_required
def analytics_dashboard(request):
    """Analytics dashboard page."""
    return render(request, 'pages/analytics/dashboard.html')


@login_required
def notifications_list(request):
    """Notifications list page."""
    return render(request, 'pages/notifications/list.html')


@login_required
def notifications_list_partial(request):
    """Notifications list partial for HTMX."""
    try:
        trainer = request.user.trainer_profile
        notifications = Notification.objects.filter(trainer=trainer).order_by('-created_at')[:50]
    except Trainer.DoesNotExist:
        notifications = Notification.objects.none()
    return render(request, 'partials/notifications/list.html', {'notifications': notifications})


@login_required
@require_http_methods(["POST"])
def notifications_mark_read(request, notification_id):
    """Mark notification as read via HTMX."""
    try:
        trainer = request.user.trainer_profile
        notification = get_object_or_404(Notification, id=notification_id, trainer=trainer)
        # Note: Notification model doesn't have is_read field, but we can mark as sent
        if notification.status == 'pending':
            notification.status = 'sent'
            notification.save()
    except Trainer.DoesNotExist:
        pass
    return notifications_list_partial(request)


@login_required
def settings(request):
    """Settings page."""
    return render(request, 'pages/settings/index.html')


def logout(request):
    """Logout view."""
    auth_logout(request)
    return redirect('users:login')

