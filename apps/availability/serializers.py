from rest_framework import serializers
from .models import AvailabilitySlot, TrainerBreak
from apps.trainers.models import Trainer


class AvailabilitySlotSerializer(serializers.ModelSerializer):
    """Serializer for availability slots."""
    day_display = serializers.CharField(source='get_day_of_week_display', read_only=True)
    
    class Meta:
        model = AvailabilitySlot
        fields = ['id', 'trainer', 'day_of_week', 'day_display', 'start_time', 'end_time', 'is_recurring', 'is_active', 'created_at']
        read_only_fields = ['id', 'trainer', 'created_at']
    
    def validate(self, data):
        """Validate time slots."""
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        
        # Use instance values if not provided in data
        if start_time is None and self.instance:
            start_time = self.instance.start_time
        if end_time is None and self.instance:
            end_time = self.instance.end_time
        
        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError("End time must be after start time.")
        return data
    
    def create(self, validated_data):
        """Create availability slot, handle unique constraint gracefully."""
        try:
            return super().create(validated_data)
        except Exception as e:
            # Check if it's a unique constraint violation
            if 'unique' in str(e).lower() or 'already exists' in str(e).lower():
                # Try to get existing slot
                trainer = validated_data.get('trainer')
                day_of_week = validated_data.get('day_of_week')
                start_time = validated_data.get('start_time')
                end_time = validated_data.get('end_time')
                
                if trainer and day_of_week is not None and start_time and end_time:
                    try:
                        existing = AvailabilitySlot.objects.get(
                            trainer=trainer,
                            day_of_week=day_of_week,
                            start_time=start_time,
                            end_time=end_time
                        )
                        # Update existing slot instead
                        for key, value in validated_data.items():
                            setattr(existing, key, value)
                        existing.save()
                        return existing
                    except AvailabilitySlot.DoesNotExist:
                        pass
            
            raise


class TrainerBreakSerializer(serializers.ModelSerializer):
    """Serializer for trainer breaks/vacation."""
    
    class Meta:
        model = TrainerBreak
        fields = ['id', 'trainer', 'start_date', 'end_date', 'reason', 'created_at']
        read_only_fields = ['id', 'trainer', 'created_at']
    
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

