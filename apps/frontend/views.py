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
from apps.trainers.models import Trainer


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
def packages_list(request):
    """Packages list page."""
    return render(request, 'pages/packages/list.html')


@login_required
def analytics_dashboard(request):
    """Analytics dashboard page."""
    return render(request, 'pages/analytics/dashboard.html')


@login_required
def notifications_list(request):
    """Notifications list page."""
    return render(request, 'pages/notifications/list.html')


@login_required
def settings(request):
    """Settings page."""
    return render(request, 'pages/settings/index.html')


def logout(request):
    """Logout view."""
    auth_logout(request)
    return redirect('users:login')

