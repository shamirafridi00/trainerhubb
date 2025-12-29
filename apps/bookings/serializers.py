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
            'is_upcoming', 'is_past', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'trainer', 'created_at', 'updated_at', 'duration_minutes', 'is_upcoming', 'is_past']
    
    def validate_start_time(self, value):
        """Validate start time is in the future for new bookings."""
        # Only validate for new bookings (not updates)
        if not self.instance and value < timezone.now():
            raise serializers.ValidationError("Cannot book in the past.")
        return value
    
    def validate(self, data):
        """Validate booking times and availability."""
        start = data.get('start_time', self.instance.start_time if self.instance else None)
        end = data.get('end_time', self.instance.end_time if self.instance else None)
        
        if start and end and start >= end:
            raise serializers.ValidationError("End time must be after start time.")
        
        # Check for conflicts only for pending/confirmed bookings
        status = data.get('status', self.instance.status if self.instance else 'pending')
        if status in ['pending', 'confirmed']:
            from apps.availability.utils import has_conflict
            trainer = data.get('trainer', self.instance.trainer if self.instance else None)
            
            if trainer and start and end:
                if has_conflict(trainer.id, start, end):
                    raise serializers.ValidationError("Trainer is not available at this time.")
        
        return data


class BookingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating bookings."""
    
    class Meta:
        model = Booking
        fields = ['client', 'start_time', 'end_time', 'notes']
    
    def validate_start_time(self, value):
        """Validate start time is in the future."""
        if value < timezone.now():
            raise serializers.ValidationError("Cannot book in the past.")
        return value
    
    def validate(self, data):
        """Validate booking times."""
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError("End time must be after start time.")
        return data
    
    def create(self, validated_data):
        """Create booking with current trainer."""
        trainer = self.context['request'].user.trainer_profile
        validated_data['trainer'] = trainer
        return super().create(validated_data)


class BookingDetailSerializer(BookingSerializer):
    """Extended serializer with additional details."""
    
    class Meta(BookingSerializer.Meta):
        fields = BookingSerializer.Meta.fields + ['cancellation_reason']

