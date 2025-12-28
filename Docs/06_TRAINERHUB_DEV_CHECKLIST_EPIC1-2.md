# 🔧 TRAINERHUB - DEV CHECKLIST V2 (DETAILED) - EPIC 1-2

Complete step-by-step development guide with PRODUCTION-READY CODE for User Authentication (EPIC 1) and Trainer Availability (EPIC 2).

**Time: 3.5 hours** | **Code: 1,200+ lines**

---

## 📋 TABLE OF CONTENTS

- EPIC 1: User Authentication (2 hours)
- EPIC 2: Trainer Availability (1.5 hours)
- Testing & Validation
- Deployment Checklist

---

# 🔐 EPIC 1: USER AUTHENTICATION (2 HOURS)

## Step 1.1: Project Setup

### 1.1.1 Create Project Structure

```bash
# Create project directory
mkdir trainerhub
cd trainerhub

# Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install Django
pip install django==5.0 djangorestframework==3.14.0 python-decouple==3.8 psycopg2-binary==2.9.9

# Create project
django-admin startproject config .

# Create apps directory
mkdir apps

# Create apps
python manage.py startapp users apps/users
python manage.py startapp trainers apps/trainers
python manage.py startapp availability apps/availability
python manage.py startapp clients apps/clients
python manage.py startapp bookings apps/bookings
python manage.py startapp packages apps/packages
python manage.py startapp payments apps/payments
python manage.py startapp notifications apps/notifications
python manage.py startapp analytics apps/analytics
```

### 1.1.2 Create .env File

```env
# .env
DEBUG=True
SECRET_KEY=django-insecure-your-secret-key-here-change-in-production
ENVIRONMENT=development
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=trainerhub
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# Email (SendGrid)
SENDGRID_API_KEY=SG.xxxxx

# SMS (Twilio)
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx
TWILIO_PHONE_NUMBER=+1234567890

# Payments (Paddle)
PADDLE_VENDOR_ID=12345
PADDLE_API_KEY=xxxxx
```

### 1.1.3 Create requirements.txt

```
Django==5.0
djangorestframework==3.14.0
python-decouple==3.8
psycopg2-binary==2.9.9
django-filter==23.5
django-cors-headers==4.3.1
djangorestframework-simplejwt==5.3.2
celery==5.3.4
redis==5.0.1
sendgrid==6.11.0
twilio==8.10.0
requests==2.31.0
gunicorn==21.2.0
whitenoise==6.6.0
Pillow==10.1.0
pytest==7.4.3
pytest-django==4.7.0
```

---

## Step 1.2: Django Settings Configuration

### 1.2.1 config/settings.py (Complete)

```python
import os
from pathlib import Path
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

# Security
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost', cast=Csv())
ENVIRONMENT = config('ENVIRONMENT', default='production')

# Apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'django_filters',
    
    # Local apps
    'apps.users',
    'apps.trainers',
    'apps.clients',
    'apps.availability',
    'apps.bookings',
    'apps.packages',
    'apps.payments',
    'apps.notifications',
    'apps.analytics',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.authentication.AuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.sqlite3'),
        'NAME': config('DB_NAME', default=str(BASE_DIR / 'db.sqlite3')),
        'USER': config('DB_USER', default=''),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default=''),
        'PORT': config('DB_PORT', default=''),
        'CONN_MAX_AGE': 600,
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model
AUTH_USER_MODEL = 'users.User'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}

# CORS
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:8000',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:8000',
]

# Security settings for production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Celery Configuration
CELERY_BROKER_URL = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
```

---

## Step 1.3: Custom User Model

### 1.3.1 apps/users/models.py

```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom user model with email as primary authentication field.
    """
    email = models.EmailField(unique=True, db_index=True)
    phone_number = models.CharField(max_length=20, blank=True)
    is_trainer = models.BooleanField(default=False)
    is_client = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
```

### 1.3.2 apps/users/serializers.py

```python
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password', 'password_confirm']
    
    def validate_email(self, value):
        """Validate email is unique and valid format."""
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("Email already registered.")
        return value.lower()
    
    def validate_username(self, value):
        """Validate username is unique."""
        if User.objects.filter(username=value.lower()).exists():
            raise serializers.ValidationError("Username already taken.")
        return value.lower()
    
    def validate(self, data):
        """Validate passwords match."""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        return data
    
    def create(self, validated_data):
        """Create user with hashed password."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            **validated_data,
            password=password
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
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 
                  'phone_number', 'is_trainer', 'is_client', 'is_verified', 'created_at']
        read_only_fields = ['id', 'created_at', 'is_verified']


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
```

### 1.3.3 apps/users/views.py

```python
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

from .models import User
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
    ChangePasswordSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user registration, login, and profile management.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """Allow unauthenticated users for registration and login."""
        if self.action in ['register', 'login']:
            return [AllowAny()]
        return super().get_permissions()
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """
        User registration endpoint.
        
        POST /api/users/register/
        {
            "email": "trainer@example.com",
            "username": "trainer123",
            "first_name": "John",
            "last_name": "Doe",
            "password": "securepassword123",
            "password_confirm": "securepassword123"
        }
        """
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = Token.objects.create(user=user)
            return Response({
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        """
        User login endpoint.
        
        POST /api/users/login/
        {
            "email": "trainer@example.com",
            "password": "securepassword123"
        }
        """
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'token': token.key,
                'is_trainer': user.is_trainer,
                'is_client': user.is_client
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """
        User logout endpoint (delete token).
        
        POST /api/users/logout/
        """
        request.user.auth_token.delete()
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        Get current user profile.
        
        GET /api/users/me/
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        """
        Change user password.
        
        POST /api/users/change-password/
        {
            "old_password": "currentpassword",
            "new_password": "newpassword123",
            "new_password_confirm": "newpassword123"
        }
        """
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'Password changed successfully'},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['patch'], permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        """
        Update user profile.
        
        PATCH /api/users/update-profile/
        {
            "first_name": "Jane",
            "last_name": "Smith",
            "phone_number": "+1234567890"
        }
        """
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

### 1.3.4 apps/users/urls.py

```python
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = router.urls
```

---

## Step 1.4: Update Main URLs

### 1.4.1 config/urls.py

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.users.urls')),
]
```

---

## Step 1.5: Admin Configuration

### 1.5.1 apps/users/admin.py

```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom user admin with email as primary field.
    """
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_trainer', 'is_client', 'is_active')
    list_filter = ('is_active', 'is_trainer', 'is_client', 'is_verified', 'created_at')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_trainer', 'is_client', 'is_verified', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )
```

---

## Step 1.6: Database Migrations

```bash
# Create migrations for custom user model
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

---

## Step 1.7: Test Authentication Endpoints

```bash
# Start development server
python manage.py runserver

# In another terminal, test with curl:

# 1. Register
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "trainer@example.com",
    "username": "trainer123",
    "first_name": "John",
    "last_name": "Doe",
    "password": "securepass123",
    "password_confirm": "securepass123"
  }'

# 2. Login
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "trainer@example.com",
    "password": "securepass123"
  }'

# 3. Get current user (use token from login response)
curl -X GET http://localhost:8000/api/users/me/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"

# 4. Change password
curl -X POST http://localhost:8000/api/users/change-password/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "securepass123",
    "new_password": "newpass456",
    "new_password_confirm": "newpass456"
  }'
```

---

# 📅 EPIC 2: TRAINER AVAILABILITY (1.5 HOURS)

## Step 2.1: Create Trainer Model

### 2.1.1 apps/trainers/models.py

```python
from django.db import models
from apps.users.models import User


class Trainer(models.Model):
    """
    Trainer profile with business information.
    OneToOne relationship with User.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='trainer_profile')
    business_name = models.CharField(max_length=255)
    bio = models.TextField(blank=True)
    expertise = models.JSONField(default=list, help_text="List of specialties")
    location = models.CharField(max_length=255, blank=True)
    timezone = models.CharField(max_length=50, default='UTC')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_sessions = models.IntegerField(default=0)
    paddle_customer_id = models.CharField(max_length=255, blank=True, unique=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.business_name} ({self.user.email})"
```

### 2.1.2 apps/availability/models.py

```python
from django.db import models
from django.core.exceptions import ValidationError
from apps.trainers.models import Trainer
from datetime import datetime, time


class AvailabilitySlot(models.Model):
    """
    Recurring availability slots (e.g., Monday 9am-5pm).
    """
    DAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='availability_slots')
    day_of_week = models.IntegerField(choices=DAY_CHOICES)  # 0=Monday, 6=Sunday
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_recurring = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['day_of_week', 'start_time']
        unique_together = ['trainer', 'day_of_week', 'start_time', 'end_time']
        indexes = [
            models.Index(fields=['trainer', 'day_of_week']),
        ]
    
    def clean(self):
        """Validate that end_time is after start_time."""
        if self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time.")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.get_day_of_week_display()} {self.start_time}-{self.end_time}"


class TrainerBreak(models.Model):
    """
    Time off/vacation for trainer (overrides availability).
    """
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='breaks')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['trainer', 'start_date']),
        ]
    
    def clean(self):
        """Validate that end_date is after start_date."""
        if self.start_date >= self.end_date:
            raise ValidationError("End date must be after start date.")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.trainer.business_name} break: {self.start_date.date()}-{self.end_date.date()}"
```

---

## Step 2.2: Create Availability Serializers

### 2.2.1 apps/availability/serializers.py

```python
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
```

---

## Step 2.3: Create Availability Views

### 2.3.1 apps/availability/utils.py

```python
from datetime import datetime, timedelta, time
from .models import AvailabilitySlot, TrainerBreak


def get_available_slots(trainer_id, start_date, end_date, duration_minutes=60):
    """
    Calculate available time slots for a trainer.
    
    Args:
        trainer_id: ID of the trainer
        start_date: Start date (date object)
        end_date: End date (date object)
        duration_minutes: Duration of each slot in minutes (default 60)
    
    Returns:
        Dictionary with available slots by date
    """
    from apps.trainers.models import Trainer
    
    try:
        trainer = Trainer.objects.get(id=trainer_id)
    except Trainer.DoesNotExist:
        return {}
    
    # Get all trainer breaks in this period
    breaks = TrainerBreak.objects.filter(
        trainer=trainer,
        start_date__lte=end_date,
        end_date__gte=start_date
    )
    
    available_slots = {}
    current_date = start_date
    
    while current_date <= end_date:
        # Check if this date is within a break
        is_on_break = any(
            break_period.start_date.date() <= current_date <= break_period.end_date.date()
            for break_period in breaks
        )
        
        if is_on_break:
            current_date += timedelta(days=1)
            continue
        
        # Get availability slots for this day of week
        day_of_week = current_date.weekday()
        slots = AvailabilitySlot.objects.filter(
            trainer=trainer,
            day_of_week=day_of_week,
            is_active=True
        )
        
        day_slots = []
        for slot in slots:
            # Generate 60-minute slots within the availability window
            current_time = datetime.combine(current_date, slot.start_time)
            end_time = datetime.combine(current_date, slot.end_time)
            
            while current_time + timedelta(minutes=duration_minutes) <= end_time:
                day_slots.append(current_time.time())
                current_time += timedelta(minutes=duration_minutes)
        
        if day_slots:
            available_slots[current_date.isoformat()] = day_slots
        
        current_date += timedelta(days=1)
    
    return available_slots


def has_conflict(trainer_id, start_datetime, end_datetime):
    """
    Check if booking time conflicts with existing bookings.
    
    Args:
        trainer_id: ID of the trainer
        start_datetime: Start datetime of proposed booking
        end_datetime: End datetime of proposed booking
    
    Returns:
        Boolean indicating if there's a conflict
    """
    from apps.bookings.models import Booking
    
    conflicts = Booking.objects.filter(
        trainer_id=trainer_id,
        status__in=['pending', 'confirmed'],
        start_time__lt=end_datetime,
        end_time__gt=start_datetime
    )
    
    return conflicts.exists()
```

### 2.3.2 apps/availability/views.py

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, timedelta
from django.utils import timezone

from .models import AvailabilitySlot, TrainerBreak
from .serializers import AvailabilitySlotSerializer, TrainerBreakSerializer, AvailableSlotsSerializer
from .utils import get_available_slots
from apps.trainers.models import Trainer


class AvailabilitySlotViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing trainer availability slots.
    """
    serializer_class = AvailabilitySlotSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get only availability slots for current trainer."""
        try:
            trainer = self.request.user.trainer_profile
            return AvailabilitySlot.objects.filter(trainer=trainer)
        except Trainer.DoesNotExist:
            return AvailabilitySlot.objects.none()
    
    def perform_create(self, serializer):
        """Create availability slot for current trainer."""
        trainer = self.request.user.trainer_profile
        serializer.save(trainer=trainer)
    
    @action(detail=False, methods=['get'])
    def available_slots(self, request):
        """
        Get available slots for a trainer within date range.
        
        GET /api/availability/available-slots/?trainer_id=1&start_date=2025-01-01&end_date=2025-01-31
        
        Query params:
            trainer_id: ID of trainer (required)
            start_date: Start date in YYYY-MM-DD format (required)
            end_date: End date in YYYY-MM-DD format (required)
            duration: Slot duration in minutes (optional, default 60)
        """
        trainer_id = request.query_params.get('trainer_id')
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        duration = int(request.query_params.get('duration', 60))
        
        # Validate required parameters
        if not all([trainer_id, start_date_str, end_date_str]):
            return Response(
                {'error': 'trainer_id, start_date, and end_date are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        available = get_available_slots(int(trainer_id), start_date, end_date, duration)
        
        return Response({
            'trainer_id': trainer_id,
            'start_date': start_date_str,
            'end_date': end_date_str,
            'available_slots': available
        })


class TrainerBreakViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing trainer breaks/vacation.
    """
    serializer_class = TrainerBreakSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get only breaks for current trainer."""
        try:
            trainer = self.request.user.trainer_profile
            return TrainerBreak.objects.filter(trainer=trainer)
        except Trainer.DoesNotExist:
            return TrainerBreak.objects.none()
    
    def perform_create(self, serializer):
        """Create break for current trainer."""
        trainer = self.request.user.trainer_profile
        serializer.save(trainer=trainer)
```

### 2.3.3 apps/availability/urls.py

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AvailabilitySlotViewSet, TrainerBreakViewSet

router = DefaultRouter()
router.register(r'availability-slots', AvailabilitySlotViewSet, basename='availability-slot')
router.register(r'breaks', TrainerBreakViewSet, basename='trainer-break')

urlpatterns = [
    path('', include(router.urls)),
]
```

---

## Step 2.4: Update Main URLs

### 2.4.1 Update config/urls.py

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.users.urls')),
    path('api/', include('apps.availability.urls')),
]
```

---

## Step 2.5: Admin Configuration

### 2.5.1 apps/trainers/admin.py

```python
from django.contrib import admin
from .models import Trainer


@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'user', 'rating', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'rating', 'created_at')
    search_fields = ('business_name', 'user__email')
    ordering = ('-created_at',)
```

### 2.5.2 apps/availability/admin.py

```python
from django.contrib import admin
from .models import AvailabilitySlot, TrainerBreak


@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(admin.ModelAdmin):
    list_display = ('trainer', 'get_day_display', 'start_time', 'end_time', 'is_active')
    list_filter = ('day_of_week', 'is_active', 'created_at')
    search_fields = ('trainer__business_name', 'trainer__user__email')
    ordering = ('trainer', 'day_of_week', 'start_time')
    
    def get_day_display(self, obj):
        return obj.get_day_of_week_display()
    get_day_display.short_description = 'Day'


@admin.register(TrainerBreak)
class TrainerBreakAdmin(admin.ModelAdmin):
    list_display = ('trainer', 'start_date', 'end_date', 'reason')
    list_filter = ('start_date', 'created_at')
    search_fields = ('trainer__business_name', 'trainer__user__email', 'reason')
    ordering = ('-start_date',)
```

---

## Step 2.6: Run Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

---

## Step 2.7: Test Availability Endpoints

```bash
# Set your trainer profile first
# Then test availability endpoints:

# 1. Create availability slot (Monday 9am-5pm)
curl -X POST http://localhost:8000/api/availability-slots/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "day_of_week": 0,
    "start_time": "09:00:00",
    "end_time": "17:00:00",
    "is_recurring": true,
    "is_active": true
  }'

# 2. Get available slots
curl -X GET "http://localhost:8000/api/availability-slots/available_slots/?trainer_id=1&start_date=2025-01-01&end_date=2025-01-31" \
  -H "Authorization: Token YOUR_TOKEN"

# 3. Create trainer break (vacation)
curl -X POST http://localhost:8000/api/breaks/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2025-01-15T00:00:00Z",
    "end_date": "2025-01-20T23:59:59Z",
    "reason": "Holiday vacation"
  }'

# 4. List availability slots
curl -X GET http://localhost:8000/api/availability-slots/ \
  -H "Authorization: Token YOUR_TOKEN"

# 5. Update availability slot
curl -X PATCH http://localhost:8000/api/availability-slots/1/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "end_time": "18:00:00"
  }'
```

---

# 🧪 TESTING & VALIDATION

## Create test file: apps/users/tests.py

```python
import pytest
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import User


class UserAuthenticationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/users/register/'
        self.login_url = '/api/users/login/'
    
    def test_user_registration(self):
        """Test user registration."""
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
    
    def test_user_login(self):
        """Test user login."""
        # Create user first
        User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        # Login
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
```

Run tests:
```bash
python manage.py test apps.users.tests
# or with pytest
pytest
```

---

# ✅ EPIC 1-2 COMPLETION CHECKLIST

- [ ] User model created and migrated
- [ ] Registration endpoint working
- [ ] Login endpoint working
- [ ] Token authentication working
- [ ] Trainer model created
- [ ] Availability slots working
- [ ] Trainer breaks working
- [ ] Available slots calculation working
- [ ] All endpoints tested
- [ ] Admin interface configured
- [ ] Tests passing

---

**Next file: TRAINERHUB_DEV_CHECKLIST_V2_PART2.md (EPIC 3-5: Clients, Bookings, Packages)** - Ask when ready!
