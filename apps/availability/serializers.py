from rest_framework import serializers
from .models import AvailabilitySlot, TrainerBreak
from apps.trainers.models import Trainer


class AvailabilitySlotSerializer(serializers.ModelSerializer):
    """Serializer for availability slots."""
    day_display = serializers.CharField(source='get_day_of_week_display', read_only=True)
    
    class Meta:
        model = AvailabilitySlot
        fields = ['id', 'trainer', 'day_of_week', 'day_display', 'start_time', 'end_time', 'is_recurring', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate(self, data):
        """Validate time slots."""
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError("End time must be after start time.")
        return data


class TrainerBreakSerializer(serializers.ModelSerializer):
    """Serializer for trainer breaks/vacation."""
    
    class Meta:
        model = TrainerBreak
        fields = ['id', 'trainer', 'start_date', 'end_date', 'reason', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate(self, data):
        """Validate dates."""
        if data['start_date'] >= data['end_date']:
            raise serializers.ValidationError("End date must be after start date.")
        return data


class AvailableSlotsSerializer(serializers.Serializer):
    """Serializer for available slots query response."""
    trainer_id = serializers.IntegerField()
    date = serializers.DateField()
    available_slots = serializers.ListField(child=serializers.TimeField())
    total = serializers.IntegerField()

