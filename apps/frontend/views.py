"""
Frontend views for HTMX - Template-based views that work alongside DRF API.
DRF endpoints remain available for future React Native app.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout


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

