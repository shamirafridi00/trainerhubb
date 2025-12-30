"""
Public API views for booking without authentication.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from apps.trainers.models import Trainer
from apps.clients.models import Client
from apps.bookings.models import Booking
from apps.bookings.serializers import BookingSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def create_public_booking(request, trainer_slug):
    """
    Create a booking from a public page without authentication.
    Creates or retrieves the client based on email.
    """
    trainer = Trainer.objects.filter(user__username=trainer_slug).first()
    if not trainer:
        trainer = Trainer.objects.filter(user__email__startswith=trainer_slug).first()
    
    if not trainer:
        return Response(
            {'detail': 'Trainer not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Validate required fields
    required_fields = ['name', 'email', 'booking_date', 'booking_time']
    for field in required_fields:
        if not request.data.get(field):
            return Response(
                {'detail': f'{field} is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Get or create client
    email = request.data['email']
    name = request.data['name']
    phone = request.data.get('phone', '')
    
    client, created = Client.objects.get_or_create(
        trainer=trainer,
        email=email,
        defaults={
            'name': name,
            'phone_number': phone,
        }
    )
    
    # If client exists but name/phone changed, update them
    if not created:
        client.name = name
        if phone:
            client.phone_number = phone
        client.save()
    
    # Create booking
    booking_date = request.data['booking_date']
    booking_time = request.data['booking_time']
    notes = request.data.get('notes', '')
    
    # Parse time to create datetime
    from datetime import datetime, time as dt_time
    booking_datetime = datetime.strptime(
        f"{booking_date} {booking_time}",
        "%Y-%m-%d %H:%M"
    )
    
    booking = Booking.objects.create(
        trainer=trainer,
        client=client,
        booking_date=booking_date,
        start_time=dt_time.fromisoformat(booking_time),
        end_time=dt_time(
            hour=(datetime.strptime(booking_time, "%H:%M").hour + 1) % 24,
            minute=datetime.strptime(booking_time, "%H:%M").minute
        ),
        status='pending',
        notes=notes,
    )
    
    # TODO: Send confirmation email to client
    # TODO: Send notification email to trainer
    
    serializer = BookingSerializer(booking)
    return Response({
        'detail': 'Booking created successfully',
        'booking': serializer.data
    }, status=status.HTTP_201_CREATED)

