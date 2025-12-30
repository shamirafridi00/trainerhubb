"""
Serializers for User authentication and management.
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Creates user in both Django and optionally syncs with Supabase.
    """
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8, required=False)
    username = serializers.CharField(required=False, allow_blank=True)
    business_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    phone_number = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password', 'password_confirm', 'business_name', 'phone_number']
    
    def validate_email(self, value):
        """Validate email is unique and valid format."""
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("Email already registered.")
        return value.lower()
    
    def validate_username(self, value):
        """Validate username is unique or generate from email."""
        if value:
            if User.objects.filter(username=value.lower()).exists():
                raise serializers.ValidationError("Username already taken.")
            return value.lower()
        return value
    
    def validate(self, data):
        """Validate passwords match and generate username if not provided."""
        # Generate username from email if not provided
        if not data.get('username'):
            email_local = data['email'].split('@')[0]
            base_username = email_local.lower().replace('.', '_').replace('-', '_')
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            data['username'] = username
        
        # Validate password confirmation
        password_confirm = data.get('password_confirm') or data.get('password')
        if data['password'] != password_confirm:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        
        return data
    
    def create(self, validated_data):
        """Create user with hashed password."""
        validated_data.pop('password_confirm', None)
        business_name = validated_data.pop('business_name', None)
        phone_number = validated_data.pop('phone_number', None)
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            **validated_data,
            password=password,
            is_trainer=True  # All registrations are trainers
        )
        
        # Set phone number if provided
        if phone_number:
            user.phone_number = phone_number
            user.save()
        
        # Create trainer profile automatically
        from apps.trainers.models import Trainer
        trainer_business_name = business_name or user.get_full_name() or f"{user.email}'s Fitness Business"
        
        Trainer.objects.create(
            user=user,
            business_name=trainer_business_name,
            bio='',
            location='',
            timezone='UTC',
            is_verified=False
        )
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        """Authenticate user."""
        email = data.get('email').lower()
        password = data.get('password')
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password.")
        
        if not user.check_password(password):
            raise serializers.ValidationError("Invalid email or password.")
        
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")
        
        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile.
    """
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', 'full_name',
            'phone_number', 'is_trainer', 'is_client', 'is_verified', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'is_verified']
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing password.
    """
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    def validate_old_password(self, value):
        """Validate old password."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value
    
    def validate(self, data):
        """Validate new passwords match."""
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError("New passwords do not match.")
        return data
    
    def save(self):
        """Update password."""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user

