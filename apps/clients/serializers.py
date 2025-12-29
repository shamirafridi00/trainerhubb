from rest_framework import serializers
from .models import Client, ClientNote


class ClientNoteSerializer(serializers.ModelSerializer):
    """Serializer for client notes."""
    created_by_name = serializers.CharField(
        source='created_by.get_full_name',
        read_only=True
    )
    
    class Meta:
        model = ClientNote
        fields = ['id', 'content', 'created_by_name', 'created_at']
        read_only_fields = ['id', 'created_at', 'created_by_name']


class ClientSerializer(serializers.ModelSerializer):
    """Serializer for client profiles."""
    notes_count = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Client
        fields = [
            'id', 'trainer', 'email', 'first_name', 'last_name', 'full_name', 'phone',
            'fitness_level', 'goals', 'preferences', 'notes',
            'is_active', 'notes_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'trainer', 'created_at', 'updated_at', 'notes_count', 'full_name']
    
    def get_notes_count(self, obj):
        return obj.client_notes.count()
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def validate_email(self, value):
        """Validate email format."""
        if not value:
            raise serializers.ValidationError("Email is required.")
        return value.lower()
    
    def validate_fitness_level(self, value):
        """Validate fitness level."""
        valid_levels = [choice[0] for choice in Client.FITNESS_LEVEL_CHOICES]
        if value not in valid_levels:
            raise serializers.ValidationError(f"Invalid fitness level. Choose from: {', '.join(valid_levels)}")
        return value


class ClientDetailSerializer(ClientSerializer):
    """Extended serializer with related data."""
    notes = ClientNoteSerializer(many=True, read_only=True, source='client_notes')
    bookings_count = serializers.SerializerMethodField()
    
    class Meta(ClientSerializer.Meta):
        fields = ClientSerializer.Meta.fields + ['notes', 'bookings_count']
    
    def get_bookings_count(self, obj):
        # Will be implemented in Epic 4 when bookings are created
        return 0

