"""
Frontend URL configuration for HTMX views.
"""
from django.urls import path
from . import views

app_name = 'frontend'

urlpatterns = [
    path('', views.landing, name='landing'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Dashboard
    path('dashboard/stats/', views.dashboard_stats, name='dashboard_stats'),
    path('dashboard/bookings-upcoming/', views.bookings_upcoming_partial, name='bookings_upcoming_partial'),
    path('dashboard/clients-recent/', views.clients_recent_partial, name='clients_recent_partial'),
    path('dashboard/revenue-chart/', views.analytics_revenue_chart, name='analytics_revenue_chart'),
    
    # Bookings
    path('bookings/', views.bookings_list, name='bookings_list'),
    path('bookings/partial/', views.bookings_list_partial, name='bookings_list_partial'),
    path('bookings/create-form/', views.bookings_create_form, name='bookings_create_form'),
    path('bookings/create/', views.bookings_create, name='bookings_create'),
    path('bookings/<int:booking_id>/', views.bookings_detail, name='bookings_detail'),
    path('bookings/<int:booking_id>/confirm/', views.bookings_confirm, name='bookings_confirm'),
    path('bookings/<int:booking_id>/cancel/', views.bookings_cancel, name='bookings_cancel'),
    path('bookings/<int:booking_id>/mark-completed/', views.bookings_mark_completed, name='bookings_mark_completed'),
    
    # Clients
    path('clients/', views.clients_list, name='clients_list'),
    path('clients/partial/', views.clients_list_partial, name='clients_list_partial'),
    path('clients/create-form/', views.clients_create_form, name='clients_create_form'),
    path('clients/create/', views.clients_create, name='clients_create'),
    path('clients/<int:client_id>/', views.clients_detail, name='clients_detail'),
    path('clients/<int:client_id>/edit-form/', views.clients_edit_form, name='clients_edit_form'),
    path('clients/<int:client_id>/update/', views.clients_update, name='clients_update'),
    
    # Packages
    path('packages/', views.packages_list, name='packages_list'),
    path('packages/partial/', views.packages_list_partial, name='packages_list_partial'),
    path('packages/create-form/', views.packages_create_form, name='packages_create_form'),
    path('packages/create/', views.packages_create, name='packages_create'),
    path('packages/<int:package_id>/edit-form/', views.packages_edit_form, name='packages_edit_form'),
    path('packages/<int:package_id>/update/', views.packages_update, name='packages_update'),
    
    # Analytics
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    
    # Notifications
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/partial/', views.notifications_list_partial, name='notifications_list_partial'),
    path('notifications/<int:notification_id>/mark-read/', views.notifications_mark_read, name='notifications_mark_read'),
    
    # Settings
    path('settings/', views.settings, name='settings'),
]

