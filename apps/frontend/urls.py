"""
Frontend URL configuration for HTMX views.
"""
from django.urls import path
from . import views

app_name = 'frontend'

urlpatterns = [
    path('', views.landing, name='landing'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Bookings
    path('bookings/', views.bookings_list, name='bookings_list'),
    path('bookings/partial/', views.bookings_list_partial, name='bookings_list_partial'),
    path('bookings/create-form/', views.bookings_create_form, name='bookings_create_form'),
    path('bookings/create/', views.bookings_create, name='bookings_create'),
    path('bookings/<int:booking_id>/', views.bookings_detail, name='bookings_detail'),
    path('bookings/<int:booking_id>/confirm/', views.bookings_confirm, name='bookings_confirm'),
    path('bookings/<int:booking_id>/cancel/', views.bookings_cancel, name='bookings_cancel'),
    path('bookings/<int:booking_id>/mark-completed/', views.bookings_mark_completed, name='bookings_mark_completed'),
    
    # Other pages
    path('clients/', views.clients_list, name='clients_list'),
    path('packages/', views.packages_list, name='packages_list'),
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('settings/', views.settings, name='settings'),
]

