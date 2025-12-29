from rest_framework import serializers
from .models import SessionPackage, ClientPackage


class SessionPackageSerializer(serializers.ModelSerializer):
    """Serializer for session packages."""
    
    class Meta:
        model = SessionPackage
        fields = ['id', 'name', 'description', 'sessions_count', 'price', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_sessions_count(self, value):
        """Validate sessions count is positive."""
        if value <= 0:
            raise serializers.ValidationError("Sessions count must be greater than 0.")
        return value
    
    def validate_price(self, value):
        """Validate price is positive."""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0.")
        return value
    
    def create(self, validated_data):
        """Create package, handle unique constraint gracefully."""
        trainer = validated_data.get('trainer')
        name = validated_data.get('name')
        
        # Check if package with same name already exists for this trainer
        if trainer and name:
            try:
                existing = SessionPackage.objects.get(trainer=trainer, name=name)
                # Update existing package instead of creating new one
                for key, value in validated_data.items():
                    setattr(existing, key, value)
                existing.save()
                return existing
            except SessionPackage.DoesNotExist:
                pass
        
        return super().create(validated_data)


class ClientPackageSerializer(serializers.ModelSerializer):
    """Serializer for client packages."""
    package_name = serializers.CharField(source='session_package.name', read_only=True)
    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = ClientPackage
        fields = [
            'id', 'client', 'client_name', 'session_package', 'package_name', 
            'sessions_remaining', 'expiry_date', 'is_expired', 'is_active', 'purchased_at'
        ]
        read_only_fields = ['id', 'purchased_at', 'is_expired', 'is_active', 'client_name', 'package_name']
    
    def validate_sessions_remaining(self, value):
        """Validate sessions remaining is not negative."""
        if value < 0:
            raise serializers.ValidationError("Sessions remaining cannot be negative.")
        return value

