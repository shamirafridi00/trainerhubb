"""
Serializers for Trainer and White-Label Settings
"""
from rest_framework import serializers
from .models import Trainer, WhiteLabelSettings, PaymentLinks


class TrainerSerializer(serializers.ModelSerializer):
    """Serializer for Trainer model."""
    email = serializers.EmailField(source='user.email', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Trainer
        fields = [
            'id', 'user', 'email', 'username', 'business_name', 'bio',
            'expertise', 'location', 'timezone', 'rating', 'total_sessions',
            'is_verified', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'rating', 'total_sessions', 'is_verified', 'created_at', 'updated_at']


class WhiteLabelSettingsSerializer(serializers.ModelSerializer):
    """Serializer for White-Label Settings."""
    
    class Meta:
        model = WhiteLabelSettings
        fields = [
            'id', 'trainer', 'remove_branding', 'custom_logo', 'custom_favicon',
            'primary_color', 'secondary_color', 'accent_color',
            'text_color', 'background_color', 'font_family',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'trainer', 'created_at', 'updated_at']
    
    def validate_custom_logo(self, value):
        """Validate logo file size."""
        if value and value.size > 500 * 1024:  # 500KB
            raise serializers.ValidationError("Logo file size must be less than 500KB")
        return value
    
    def validate_custom_favicon(self, value):
        """Validate favicon file size."""
        if value and value.size > 100 * 1024:  # 100KB
            raise serializers.ValidationError("Favicon file size must be less than 100KB")
        return value
    
    def validate_primary_color(self, value):
        """Validate hex color format."""
        if not value.startswith('#') or len(value) != 7:
            raise serializers.ValidationError("Color must be in hex format (#RRGGBB)")
        return value
    
    def validate_secondary_color(self, value):
        """Validate hex color format."""
        if not value.startswith('#') or len(value) != 7:
            raise serializers.ValidationError("Color must be in hex format (#RRGGBB)")
        return value
    
    def validate_accent_color(self, value):
        """Validate hex color format."""
        if not value.startswith('#') or len(value) != 7:
            raise serializers.ValidationError("Color must be in hex format (#RRGGBB)")
        return value


class PaymentLinksSerializer(serializers.ModelSerializer):
    """Serializer for Payment Links configuration."""
    available_methods = serializers.SerializerMethodField()
    
    class Meta:
        model = PaymentLinks
        fields = [
            'id', 'stripe_link', 'paypal_link', 'venmo_username', 'zelle_email',
            'cashapp_username', 'bank_name', 'account_holder_name', 
            'account_number_last4', 'routing_number', 'custom_links',
            'show_on_public_pages', 'payment_instructions', 'available_methods',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'available_methods']
    
    def get_available_methods(self, obj):
        """Get list of available payment methods."""
        return obj.get_available_methods()
    
    def validate_custom_links(self, value):
        """Validate custom links structure."""
        if not isinstance(value, list):
            raise serializers.ValidationError("custom_links must be a list")
        
        for link in value:
            if not isinstance(link, dict):
                raise serializers.ValidationError("Each link must be a dictionary")
            if 'label' not in link or 'url' not in link:
                raise serializers.ValidationError("Each link must have 'label' and 'url' fields")
        
        return value

