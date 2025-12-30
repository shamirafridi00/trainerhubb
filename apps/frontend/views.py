"""
Frontend views for HTMX - Template-based views that work alongside DRF API.
DRF endpoints remain available for future React Native app.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout, authenticate, login as auth_login
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Q
from django.contrib import messages
from datetime import datetime, timedelta

from apps.bookings.models import Booking
from apps.clients.models import Client, ClientNote
from apps.packages.models import SessionPackage, ClientPackage
from apps.payments.models import Payment, Subscription
from apps.notifications.models import Notification
from apps.trainers.models import Trainer
from django.db.models import Sum, Count, Avg, Q
from datetime import timedelta


def get_or_create_trainer_profile(user):
    """
    Get or create trainer profile for a user.
    Creates a default trainer profile if one doesn't exist.
    """
    try:
        return user.trainer_profile
    except Trainer.DoesNotExist:
        # Create a default trainer profile
        business_name = user.get_full_name() or f"{user.email}'s Fitness Business"
        trainer = Trainer.objects.create(
            user=user,
            business_name=business_name,
            bio='',
            location='',
            timezone='UTC',
            is_verified=False
        )
        return trainer


def landing(request):
    """Landing page for unauthenticated users."""
    if request.user.is_authenticated:
        return redirect('frontend:dashboard')
    return render(request, 'pages/landing.html')


def register(request):
    """Registration page for new users."""
    if request.user.is_authenticated:
        return redirect('frontend:dashboard')
    
    if request.method == 'POST':
        from apps.users.serializers import UserRegistrationSerializer
        
        # Prepare data
        data = {
            'email': request.POST.get('email'),
            'username': request.POST.get('username'),
            'first_name': request.POST.get('first_name'),
            'last_name': request.POST.get('last_name'),
            'password': request.POST.get('password'),
            'password_confirm': request.POST.get('password_confirm'),
        }
        
        # Validate and create user using serializer
        serializer = UserRegistrationSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            # Log the user in
            auth_login(request, user)
            return redirect('frontend:dashboard')
        else:
            # Show validation errors
            error_msg = 'Registration failed. Please check your information.'
            if serializer.errors:
                # Get first error message
                first_error = list(serializer.errors.values())[0]
                if isinstance(first_error, list):
                    error_msg = first_error[0]
                else:
                    error_msg = str(first_error)
            messages.error(request, error_msg)
    
    return render(request, 'pages/auth/register.html')


def login(request):
    """Login page."""
    if request.user.is_authenticated:
        return redirect('frontend:dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Authenticate using email as username
        user = authenticate(request, username=email, password=password)
        if user:
            auth_login(request, user)
            return redirect('frontend:dashboard')
        else:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'pages/auth/login.html')


@login_required
def dashboard(request):
    """Main dashboard page."""
    return render(request, 'pages/dashboard.html')


@login_required
def dashboard_stats(request):
    """Dashboard stats partial for HTMX."""
    trainer = get_or_create_trainer_profile(request.user)
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
    elif total_bookings > 0 and last_month_bookings == 0:
        booking_change = 100  # New bookings this month
    
    client_change = 0
    if last_month_clients > 0:
        client_change = round(((total_clients - last_month_clients) / last_month_clients) * 100, 1)
    elif total_clients > 0 and last_month_clients == 0:
        client_change = 100  # New clients this month
    
    stats = [
        {
            'label': 'Total Bookings',
            'value': total_bookings,
            'color': 'indigo',
            'icon': 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z',
            'change': booking_change,
            'change_abs': abs(booking_change) if booking_change is not None else None
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
            'change': client_change,
            'change_abs': abs(client_change) if client_change is not None else None
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
        bookings = Booking.objects.filter(
            trainer=trainer,
            status__in=['pending', 'confirmed'],
            start_time__gte=timezone.now()
        ).select_related('client').order_by('start_time')[:5]
    except (Trainer.DoesNotExist, AttributeError):
        bookings = []
    except Exception as e:
        # Log error but don't crash
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in bookings_upcoming_partial: {e}")
        bookings = []
    
    return render(request, 'partials/bookings/upcoming.html', {'bookings': bookings})


@login_required
def clients_recent_partial(request):
    """Recent clients partial for dashboard."""
    try:
        trainer = request.user.trainer_profile
        clients = Client.objects.filter(trainer=trainer).order_by('-created_at')[:5]
    except (Trainer.DoesNotExist, AttributeError):
        clients = []
    except Exception as e:
        # Log error but don't crash
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in clients_recent_partial: {e}")
        clients = []
    
    return render(request, 'partials/clients/recent.html', {'clients': clients})


@login_required
def analytics_revenue_chart(request):
    """Revenue chart partial for dashboard."""
    try:
        trainer = request.user.trainer_profile
    except (Trainer.DoesNotExist, AttributeError):
        return render(request, 'partials/analytics/revenue_chart.html', {
            'total_revenue': 0,
            'monthly_revenue': 0,
            'average_booking_value': 0,
            'monthly_data': []
        })
    
    try:
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
    except Exception as e:
        # Log error but return empty data
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in analytics_revenue_chart: {e}")
        return render(request, 'partials/analytics/revenue_chart.html', {
            'total_revenue': 0,
            'monthly_revenue': 0,
            'average_booking_value': 0,
            'monthly_data': []
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
    trainer = get_or_create_trainer_profile(request.user)
    clients = Client.objects.filter(trainer=trainer, is_active=True).order_by('first_name', 'last_name')
    return render(request, 'partials/bookings/form.html', {'clients': clients})


@login_required
@require_http_methods(["POST"])
def bookings_create(request):
    """Create booking via HTMX."""
    import logging
    logger = logging.getLogger(__name__)
    
    # Get or create trainer profile
    trainer = get_or_create_trainer_profile(request.user)
    
    # Get form data
    client_id = request.POST.get('client', '').strip()
    start_time_str = request.POST.get('start_time', '').strip()
    duration_minutes_str = request.POST.get('duration_minutes', '60').strip()
    notes = request.POST.get('notes', '').strip()
    
    # Preserve form data for error messages
    form_data = {
        'client': client_id,
        'start_time': start_time_str,
        'duration_minutes': duration_minutes_str,
        'notes': notes
    }
    
    # Get clients list for form
    clients = Client.objects.filter(trainer=trainer, is_active=True).order_by('first_name', 'last_name')
    
    # Validate required fields
    if not client_id:
        return render(request, 'partials/bookings/form.html', {
            'clients': clients,
            'form_data': form_data,
            'error': 'Please select a client.'
        })
    
    if not start_time_str:
        return render(request, 'partials/bookings/form.html', {
            'clients': clients,
            'form_data': form_data,
            'error': 'Start date and time are required.'
        })
    
    # Validate duration
    try:
        duration_minutes = int(duration_minutes_str)
        if duration_minutes < 15:
            return render(request, 'partials/bookings/form.html', {
                'clients': clients,
                'form_data': form_data,
                'error': 'Duration must be at least 15 minutes.'
            })
    except ValueError:
        return render(request, 'partials/bookings/form.html', {
            'clients': clients,
            'form_data': form_data,
            'error': 'Duration must be a valid number.'
        })
    
    try:
        # Get client
        client = Client.objects.get(id=client_id, trainer=trainer)
        
        # Parse datetime-local format (YYYY-MM-DDTHH:MM)
        try:
            start_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            # Try with seconds if provided
            try:
                start_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M:%S')
            except ValueError:
                return render(request, 'partials/bookings/form.html', {
                    'clients': clients,
                    'form_data': form_data,
                    'error': 'Invalid date/time format. Please use the date picker.'
                })
        
        # Make timezone-aware
        if timezone.is_naive(start_time):
            start_time = timezone.make_aware(start_time)
        
        # Check if booking is in the past
        if start_time < timezone.now():
            return render(request, 'partials/bookings/form.html', {
                'clients': clients,
                'form_data': form_data,
                'error': 'Cannot create a booking in the past.'
            })
        
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
        
        logger.info(f'Booking created: {booking.id} - {client.get_full_name()} at {start_time} by trainer {trainer.id}')
        
        # Trigger notification asynchronously (non-blocking, fail-fast if Redis unavailable)
        # Use threading to avoid blocking the request if Celery/Redis is down
        import threading
        def send_notification_async():
            try:
                from apps.notifications.tasks import send_booking_confirmation
                # Try to send via Celery, but fail fast if Redis is unavailable
                try:
                    send_booking_confirmation.delay(booking.id)
                except Exception as celery_error:
                    # If Celery fails (Redis down), skip notification silently
                    logger.debug(f'Celery unavailable, skipping notification: {str(celery_error)}')
            except Exception as e:
                logger.debug(f'Could not send booking confirmation notification: {str(e)}')
        
        # Start notification in background thread (non-blocking)
        notification_thread = threading.Thread(target=send_notification_async, daemon=True)
        notification_thread.start()
        
        # Check if request is from dashboard
        hx_target = request.headers.get('HX-Target', '')
        if hx_target == 'bookings-list':
            return bookings_list_partial(request)
        
        # Return success message that will close modal
        return render(request, 'partials/bookings/form_success.html', {'message': 'Booking created successfully!'})
        
    except Client.DoesNotExist:
        return render(request, 'partials/bookings/form.html', {
            'clients': clients,
            'form_data': form_data,
            'error': 'Selected client not found.'
        })
    except Exception as e:
        logger.error(f'Error creating booking: {str(e)}', exc_info=True)
        error_msg = str(e)
        return render(request, 'partials/bookings/form.html', {
            'clients': clients,
            'form_data': form_data,
            'error': f'Error creating booking: {error_msg}'
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
        
        # Trigger notification asynchronously (non-blocking)
        import threading
        def send_notification_async():
            try:
                from apps.notifications.tasks import send_booking_confirmation
                try:
                    send_booking_confirmation.delay(booking.id)
                except Exception:
                    pass  # Silently fail if Redis/Celery unavailable
            except Exception:
                pass
        
        notification_thread = threading.Thread(target=send_notification_async, daemon=True)
        notification_thread.start()
    
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
    trainer = get_or_create_trainer_profile(request.user)
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
    import logging
    logger = logging.getLogger(__name__)
    
    # Get or create trainer profile
    trainer = get_or_create_trainer_profile(request.user)
    
    # Validate required fields
    first_name = request.POST.get('first_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()
    email = request.POST.get('email', '').strip()
    
    # Preserve form data for error messages
    form_data = {
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'phone': request.POST.get('phone', ''),
        'fitness_level': request.POST.get('fitness_level', 'beginner'),
        'notes': request.POST.get('notes', ''),
    }
    
    if not first_name or not last_name or not email:
        return render(request, 'partials/clients/form.html', {
            'client': None,
            'form_data': form_data,
            'error': 'First name, last name, and email are required.'
        })
    
    try:
        # Check if client with this email already exists for this trainer
        if Client.objects.filter(trainer=trainer, email=email).exists():
            return render(request, 'partials/clients/form.html', {
                'client': None,
                'form_data': form_data,
                'error': f'A client with email {email} already exists in your client list.'
            })
        
        client = Client.objects.create(
            trainer=trainer,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=request.POST.get('phone', ''),
            fitness_level=request.POST.get('fitness_level', 'beginner'),
            notes=request.POST.get('notes', ''),
            is_active=True
        )
        
        logger.info(f'Client created: {client.id} - {client.first_name} {client.last_name} by trainer {trainer.id}')
        
        # Check if request is from dashboard
        hx_target = request.headers.get('HX-Target', '')
        if hx_target == 'clients-list':
            return clients_list_partial(request)
        
        return render(request, 'partials/clients/form_success.html', {'message': 'Client created successfully!'})
    except Exception as e:
        logger.error(f'Error creating client: {str(e)}', exc_info=True)
        error_msg = str(e)
        if 'unique constraint' in error_msg.lower() or 'duplicate' in error_msg.lower():
            error_msg = f'A client with email {email} already exists.'
        return render(request, 'partials/clients/form.html', {
            'client': None,
            'form_data': form_data,
            'error': f'Error creating client: {error_msg}'
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
    trainer = get_or_create_trainer_profile(request.user)
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
    import logging
    logger = logging.getLogger(__name__)
    
    # Get or create trainer profile
    trainer = get_or_create_trainer_profile(request.user)
    
    # Validate required fields
    name = request.POST.get('name', '').strip()
    sessions_count = request.POST.get('sessions_count', '').strip()
    price = request.POST.get('price', '').strip()
    
    # Preserve form data for error messages
    form_data = {
        'name': name,
        'description': request.POST.get('description', ''),
        'sessions_count': sessions_count,
        'price': price,
        'is_active': request.POST.get('is_active') == 'on'
    }
    
    # Validate required fields
    if not name:
        return render(request, 'partials/packages/form.html', {
            'package': None,
            'form_data': form_data,
            'error': 'Package name is required.'
        })
    
    if not sessions_count:
        return render(request, 'partials/packages/form.html', {
            'package': None,
            'form_data': form_data,
            'error': 'Sessions count is required.'
        })
    
    if not price:
        return render(request, 'partials/packages/form.html', {
            'package': None,
            'form_data': form_data,
            'error': 'Price is required.'
        })
    
    # Validate numeric fields
    try:
        sessions_count_int = int(sessions_count)
        if sessions_count_int < 1:
            return render(request, 'partials/packages/form.html', {
                'package': None,
                'form_data': form_data,
                'error': 'Sessions count must be at least 1.'
            })
    except ValueError:
        return render(request, 'partials/packages/form.html', {
            'package': None,
            'form_data': form_data,
            'error': 'Sessions count must be a valid number.'
        })
    
    try:
        price_float = float(price)
        if price_float < 0:
            return render(request, 'partials/packages/form.html', {
                'package': None,
                'form_data': form_data,
                'error': 'Price cannot be negative.'
            })
    except ValueError:
        return render(request, 'partials/packages/form.html', {
            'package': None,
            'form_data': form_data,
            'error': 'Price must be a valid number.'
        })
    
    try:
        # Check if package with this name already exists for this trainer
        if SessionPackage.objects.filter(trainer=trainer, name=name).exists():
            return render(request, 'partials/packages/form.html', {
                'package': None,
                'form_data': form_data,
                'error': f'A package with name "{name}" already exists.'
            })
        
        package = SessionPackage.objects.create(
            trainer=trainer,
            name=name,
            description=request.POST.get('description', ''),
            sessions_count=sessions_count_int,
            price=price_float,
            is_active=request.POST.get('is_active') == 'on'
        )
        
        logger.info(f'Package created: {package.id} - {package.name} by trainer {trainer.id}')
        
        # Check if request is from dashboard
        hx_target = request.headers.get('HX-Target', '')
        if hx_target == 'packages-list':
            return packages_list_partial(request)
        
        return render(request, 'partials/packages/form_success.html', {'message': 'Package created successfully!'})
    except Exception as e:
        logger.error(f'Error creating package: {str(e)}', exc_info=True)
        error_msg = str(e)
        if 'unique constraint' in error_msg.lower() or 'duplicate' in error_msg.lower():
            error_msg = f'A package with name "{name}" already exists.'
        return render(request, 'partials/packages/form.html', {
            'package': None,
            'form_data': form_data,
            'error': f'Error creating package: {error_msg}'
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


# Client detail and management views
@login_required
def clients_detail_page(request, client_id):
    """Client detail page."""
    client = get_object_or_404(Client, id=client_id, trainer=request.user.trainer_profile)
    return render(request, 'pages/clients/detail.html', {'client': client})


@login_required
def clients_packages_partial(request, client_id):
    """Client packages partial."""
    client = get_object_or_404(Client, id=client_id, trainer=request.user.trainer_profile)
    client_packages = ClientPackage.objects.filter(client=client).select_related('session_package').order_by('-purchased_at')
    return render(request, 'partials/clients/packages.html', {'client_packages': client_packages})


@login_required
def clients_notes_partial(request, client_id):
    """Client notes partial."""
    client = get_object_or_404(Client, id=client_id, trainer=request.user.trainer_profile)
    notes = ClientNote.objects.filter(client=client).select_related('created_by').order_by('-created_at')[:20]
    return render(request, 'partials/clients/notes.html', {'notes': notes})


@login_required
def clients_bookings_partial(request, client_id):
    """Client recent bookings partial."""
    client = get_object_or_404(Client, id=client_id, trainer=request.user.trainer_profile)
    bookings = Booking.objects.filter(client=client).order_by('-start_time')[:5]
    return render(request, 'partials/bookings/upcoming.html', {'bookings': bookings})


@login_required
def clients_assign_package_form(request, client_id):
    """Assign package form."""
    client = get_object_or_404(Client, id=client_id, trainer=request.user.trainer_profile)
    packages = SessionPackage.objects.filter(trainer=client.trainer, is_active=True)
    return render(request, 'partials/clients/assign_package_form.html', {'client': client, 'packages': packages})


@login_required
@require_http_methods(["POST"])
def clients_assign_package(request, client_id):
    """Assign package to client."""
    client = get_object_or_404(Client, id=client_id, trainer=request.user.trainer_profile)
    package_id = request.POST.get('package')
    expiry_date_str = request.POST.get('expiry_date')
    
    try:
        package = SessionPackage.objects.get(id=package_id, trainer=client.trainer)
        expiry_date = None
        if expiry_date_str:
            expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
        
        ClientPackage.objects.create(
            client=client,
            session_package=package,
            sessions_remaining=package.sessions_count,
            expiry_date=expiry_date
        )
        
        return clients_packages_partial(request, client_id)
    except SessionPackage.DoesNotExist:
        return render(request, 'partials/clients/assign_package_form.html', {
            'client': client,
            'packages': SessionPackage.objects.filter(trainer=client.trainer, is_active=True),
            'error': 'Package not found'
        })


@login_required
def clients_add_note_form(request, client_id):
    """Add note form."""
    client = get_object_or_404(Client, id=client_id, trainer=request.user.trainer_profile)
    return render(request, 'partials/clients/add_note_form.html', {'client': client})


@login_required
@require_http_methods(["POST"])
def clients_add_note(request, client_id):
    """Add note to client."""
    client = get_object_or_404(Client, id=client_id, trainer=request.user.trainer_profile)
    content = request.POST.get('content')
    
    if content:
        ClientNote.objects.create(
            client=client,
            content=content,
            created_by=request.user
        )
        return clients_notes_partial(request, client_id)
    
    return render(request, 'partials/clients/add_note_form.html', {
        'client': client,
        'error': 'Note content is required'
    })


# Analytics views
@login_required
def analytics_summary(request):
    """Analytics summary stats."""
    try:
        trainer = request.user.trainer_profile
    except Trainer.DoesNotExist:
        return render(request, 'partials/analytics/summary.html', {'stats': []})
    
    bookings = Booking.objects.filter(trainer=trainer)
    clients = Client.objects.filter(trainer=trainer)
    payments = Payment.objects.filter(subscription__trainer=trainer, status='completed')
    
    stats = [
        {
            'label': 'Total Revenue',
            'value': f"${payments.aggregate(Sum('amount'))['amount__sum'] or 0:,.2f}",
            'color': 'pink',
            'icon': 'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
        },
        {
            'label': 'Total Bookings',
            'value': bookings.count(),
            'color': 'indigo',
            'icon': 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z',
        },
        {
            'label': 'Total Clients',
            'value': clients.count(),
            'color': 'purple',
            'icon': 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z',
        },
        {
            'label': 'Active Packages',
            'value': ClientPackage.objects.filter(client__trainer=trainer, sessions_remaining__gt=0).count(),
            'color': 'green',
            'icon': 'M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4',
        },
    ]
    
    return render(request, 'partials/analytics/summary.html', {'stats': stats})


@login_required
def analytics_bookings_chart(request):
    """Bookings statistics chart."""
    try:
        trainer = request.user.trainer_profile
    except Trainer.DoesNotExist:
        return render(request, 'partials/analytics/bookings_chart.html', {
            'total_bookings': 0,
            'completed_bookings': 0,
            'upcoming_bookings': 0,
            'status_breakdown': []
        })
    
    bookings = Booking.objects.filter(trainer=trainer)
    total_bookings = bookings.count()
    completed_bookings = bookings.filter(status='completed').count()
    upcoming_bookings = bookings.filter(status__in=['pending', 'confirmed'], start_time__gte=timezone.now()).count()
    
    # Status breakdown
    status_counts = bookings.values('status').annotate(count=Count('id')).order_by('-count')
    total = sum(s['count'] for s in status_counts)
    
    status_breakdown = []
    for status_data in status_counts:
        percentage = (status_data['count'] / total * 100) if total > 0 else 0
        status_breakdown.append({
            'status': status_data['status'],
            'count': status_data['count'],
            'percentage': round(percentage, 1)
        })
    
    return render(request, 'partials/analytics/bookings_chart.html', {
        'total_bookings': total_bookings,
        'completed_bookings': completed_bookings,
        'upcoming_bookings': upcoming_bookings,
        'status_breakdown': status_breakdown
    })


@login_required
def analytics_clients_metrics(request):
    """Client metrics."""
    try:
        trainer = request.user.trainer_profile
    except Trainer.DoesNotExist:
        return render(request, 'partials/analytics/clients_metrics.html', {
            'total_clients': 0,
            'active_clients': 0,
            'new_clients': 0,
            'last_month_clients': 0,
            'avg_sessions_per_client': 0
        })
    
    now = timezone.now()
    this_month = now.date().replace(day=1)
    last_month = (this_month - timedelta(days=1)).replace(day=1)
    
    clients = Client.objects.filter(trainer=trainer)
    total_clients = clients.count()
    active_clients = clients.filter(is_active=True).count()
    new_clients = clients.filter(created_at__gte=this_month).count()
    last_month_clients = clients.filter(created_at__gte=last_month, created_at__lt=this_month).count()
    
    # Average sessions per client
    completed_bookings = Booking.objects.filter(trainer=trainer, status='completed')
    avg_sessions_per_client = 0
    if total_clients > 0:
        avg_sessions_per_client = completed_bookings.count() / total_clients
    
    return render(request, 'partials/analytics/clients_metrics.html', {
        'total_clients': total_clients,
        'active_clients': active_clients,
        'new_clients': new_clients,
        'last_month_clients': last_month_clients,
        'avg_sessions_per_client': avg_sessions_per_client
    })


# Settings views
@login_required
def settings_profile_form(request):
    """Profile settings form."""
    user = request.user
    return render(request, 'partials/settings/profile_form.html', {'user': user})


@login_required
@require_http_methods(["POST"])
def settings_profile_update(request):
    """Update profile."""
    user = request.user
    user.first_name = request.POST.get('first_name', user.first_name)
    user.last_name = request.POST.get('last_name', user.last_name)
    user.email = request.POST.get('email', user.email)
    user.save()
    
    return settings_profile_form(request)


@login_required
def settings_subscription_info(request):
    """Subscription information."""
    try:
        trainer = request.user.trainer_profile
        subscription = Subscription.objects.filter(trainer=trainer, status='active').first()
    except Trainer.DoesNotExist:
        subscription = None
    
    return render(request, 'partials/settings/subscription_info.html', {'subscription': subscription})


@login_required
def settings_notifications_form(request):
    """Notification preferences form."""
    try:
        trainer = request.user.trainer_profile
    except Trainer.DoesNotExist:
        trainer = None
    
    return render(request, 'partials/settings/notifications_form.html', {'trainer': trainer})


def logout(request):
    """Logout view."""
    auth_logout(request)
    return redirect('frontend:login')

