from rest_framework import serializers
from django.utils import timezone
from .models import Booking
from apps.clients.models import Client


class BookingSerializer(serializers.ModelSerializer):
    """Serializer for bookings."""
    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    trainer_name = serializers.CharField(source='trainer.business_name', read_only=True)
    duration_minutes = serializers.IntegerField(read_only=True)
    is_upcoming = serializers.BooleanField(read_only=True)
    is_past = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'trainer', 'trainer_name', 'client', 'client_name',
            'start_time', 'end_time', 'status', 'notes', 'duration_minutes',
            'is_upcoming', 'is_past', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'duration_minutes', 'is_upcoming', 'is_past']
    
    def validate_start_time(self, value):
        """Validate start time is in the future."""
        if value < timezone.now():
            raise serializers.ValidationError("Cannot book in the past.")
        return value
    
    def validate(self, data):
        """Validate booking times and availability."""
        start = data.get('start_time')
        end = data.get('end_time')
        
        if start >= end:
            raise serializers.ValidationError("End time must be after start time.")
        
        # Check for conflicts
        from apps.availability.utils import has_conflict
        trainer = data.get('trainer')
        
        if has_conflict(trainer.id, start, end):
            raise serializers.ValidationError("Trainer is not available at this time.")
        
        return data


class BookingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating bookings."""
    
    class Meta:
        model = Booking
        fields = ['client', 'start_time', 'end_time', 'notes']
    
    def create(self, validated_data):
        """Create booking with current trainer."""
        trainer = self.context['request'].user.trainer_profile
        validated_data['trainer'] = trainer
        return super().create(validated_data)


class BookingDetailSerializer(BookingSerializer):
    """Extended serializer with additional details."""
    
    class Meta(BookingSerializer.Meta):
        fields = BookingSerializer.Meta.fields + ['cancellation_reason']

