"""
Domain Management Serializers
"""
from rest_framework import serializers
from .domain_models import CustomDomain, DomainVerificationLog


class CustomDomainSerializer(serializers.ModelSerializer):
    """
    Serializer for custom domain.
    """
    trainer_id = serializers.IntegerField(source='trainer.id', read_only=True)
    trainer_name = serializers.CharField(source='trainer.business_name', read_only=True)
    trainer_email = serializers.EmailField(source='trainer.user.email', read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    is_verified = serializers.BooleanField(read_only=True)
    ssl_is_valid = serializers.BooleanField(read_only=True)
    needs_ssl_renewal = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = CustomDomain
        fields = [
            'id', 'trainer_id', 'trainer_name', 'trainer_email',
            'domain', 'status', 'verification_token', 'verification_method',
            'dns_verified_at', 'last_verification_attempt', 'verification_attempts',
            'ssl_status', 'ssl_provisioned_at', 'ssl_expires_at', 'ssl_provider',
            'approved_by', 'approved_at', 'rejection_reason',
            'is_active', 'is_verified', 'ssl_is_valid', 'needs_ssl_renewal',
            'created_at', 'updated_at', 'activated_at'
        ]
        read_only_fields = [
            'verification_token', 'dns_verified_at', 'last_verification_attempt',
            'verification_attempts', 'ssl_status', 'ssl_provisioned_at', 'ssl_expires_at',
            'approved_by', 'approved_at', 'created_at', 'updated_at', 'activated_at'
        ]


class DomainVerificationLogSerializer(serializers.ModelSerializer):
    """
    Serializer for domain verification logs.
    """
    domain_name = serializers.CharField(source='domain.domain', read_only=True)
    
    class Meta:
        model = DomainVerificationLog
        fields = [
            'id', 'domain', 'domain_name', 'verification_type',
            'status', 'details', 'error_message', 'created_at'
        ]
        read_only_fields = fields


class DomainRequestSerializer(serializers.Serializer):
    """
    Serializer for domain request from trainer.
    """
    domain = serializers.CharField(max_length=255)
    verification_method = serializers.ChoiceField(
        choices=['cname', 'txt'],
        default='cname'
    )
    
    def validate_domain(self, value):
        """Validate domain format and availability."""
        import re
        
        # Basic domain validation
        domain_regex = re.compile(
            r'^(?:[a-zA-Z0-9]'  # First character of the domain
            r'(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+'  # Sub domain + hostname
            r'[a-zA-Z]{2,}$'  # First level TLD
        )
        
        if not domain_regex.match(value):
            raise serializers.ValidationError("Invalid domain format")
        
        # Check if domain already exists
        if CustomDomain.objects.filter(domain=value).exists():
            raise serializers.ValidationError("Domain already registered")
        
        return value.lower()


class DomainApprovalSerializer(serializers.Serializer):
    """
    Serializer for admin domain approval/rejection.
    """
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    reason = serializers.CharField(required=False, allow_blank=True)


class DomainVerifySerializer(serializers.Serializer):
    """
    Serializer for manual domain verification trigger.
    """
    force = serializers.BooleanField(default=False)

