"""
Frontend views for HTMX - Template-based views that work alongside DRF API.
DRF endpoints remain available for future React Native app.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

