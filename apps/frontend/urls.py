"""
Frontend URL configuration for HTMX views.
"""
from django.urls import path
from . import views

app_name = 'frontend'

urlpatterns = [
    path('', views.landing, name='landing'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('bookings/', views.bookings_list, name='bookings_list'),
    path('clients/', views.clients_list, name='clients_list'),
    path('packages/', views.packages_list, name='packages_list'),
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('settings/', views.settings, name='settings'),
]

