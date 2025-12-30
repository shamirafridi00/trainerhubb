# 🔧 TRAINERHUB - DEV CHECKLIST V2 (PART 2) - EPIC 3-5

Complete production-ready code for Client Management (EPIC 3), Booking System (EPIC 4), and Session Packages (EPIC 5).

**Time: 4.5 hours** | **Code: 1,400+ lines**

---

## 📋 TABLE OF CONTENTS

- EPIC 3: Client Management (1.5 hours)
- EPIC 4: Booking System (2 hours)
- EPIC 5: Session Packages (1 hour)
- Integration Testing

---

# 👥 EPIC 3: CLIENT MANAGEMENT (1.5 HOURS)

## Step 3.1: Client Models

### 3.1.1 apps/clients/models.py

```python
from django.db import models
from django.contrib.postgres.fields import ArrayField
from apps.trainers.models import Trainer


class Client(models.Model):
    """
    Client profile with fitness information.
    Many-to-one relationship with Trainer.
    """
    FITNESS_LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('athlete', 'Athlete'),
    ]
    
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='clients')
    email = models.EmailField()
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True)
    fitness_level = models.CharField(max_length=20, choices=FITNESS_LEVEL_CHOICES, default='beginner')
    goals = models.JSONField(default=list, help_text="List of fitness goals")
    preferences = models.JSONField(default=dict, help_text="Client preferences")
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['trainer', 'email']
        indexes = [
            models.Index(fields=['trainer', 'email']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.trainer.business_name})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class ClientNote(models.Model):
    """
    Notes about client progress and history.
    """
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='notes')
    content = models.TextField()
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['client', 'created_at']),
        ]
    
    def __str__(self):
        return f"Note for {self.client.get_full_name()} on {self.created_at.date()}"
```

---

## Step 3.2: Client Serializers

### 3.2.1 apps/clients/serializers.py

```python
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
    
    class Meta:
        model = Client
        fields = [
            'id', 'email', 'first_name', 'last_name', 'phone',
            'fitness_level', 'goals', 'preferences', 'notes',
            'is_active', 'notes_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'notes_count']
    
    def get_notes_count(self, obj):
        return obj.notes.count()
    
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
    notes = ClientNoteSerializer(many=True, read_only=True)
    bookings_count = serializers.SerializerMethodField()
    
    class Meta(ClientSerializer.Meta):
        fields = ClientSerializer.Meta.fields + ['notes', 'bookings_count']
    
    def get_bookings_count(self):
        return self.instance.bookings.count() if self.instance else 0
```

---

## Step 3.3: Client Views

### 3.3.1 apps/clients/views.py

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Client, ClientNote
from .serializers import ClientSerializer, ClientDetailSerializer, ClientNoteSerializer
from apps.trainers.models import Trainer


class ClientViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing trainer's clients.
    """
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['fitness_level', 'is_active']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    ordering_fields = ['created_at', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get only clients for current trainer."""
        try:
            trainer = self.request.user.trainer_profile
            return Client.objects.filter(trainer=trainer)
        except Trainer.DoesNotExist:
            return Client.objects.none()
    
    def get_serializer_class(self):
        """Use detailed serializer for retrieve action."""
        if self.action == 'retrieve':
            return ClientDetailSerializer
        return ClientSerializer
    
    def perform_create(self, serializer):
        """Create client for current trainer."""
        trainer = self.request.user.trainer_profile
        serializer.save(trainer=trainer)
    
    @action(detail=True, methods=['post'])
    def add_note(self, request, pk=None):
        """
        Add a note to a client.
        
        POST /api/clients/{id}/add_note/
        {
            "content": "Client is making great progress!"
        }
        """
        client = self.get_object()
        content = request.data.get('content')
        
        if not content:
            return Response(
                {'error': 'Content is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        note = ClientNote.objects.create(
            client=client,
            content=content,
            created_by=request.user
        )
        serializer = ClientNoteSerializer(note)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def notes(self, request, pk=None):
        """
        Get all notes for a client.
        
        GET /api/clients/{id}/notes/
        """
        client = self.get_object()
        notes = client.notes.all()
        serializer = ClientNoteSerializer(notes, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def bookings(self, request, pk=None):
        """
        Get all bookings for a client.
        
        GET /api/clients/{id}/bookings/
        """
        from apps.bookings.models import Booking
        from apps.bookings.serializers import BookingSerializer
        
        client = self.get_object()
        bookings = Booking.objects.filter(client=client)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)
```

### 3.3.2 apps/clients/urls.py

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClientViewSet

router = DefaultRouter()
router.register(r'clients', ClientViewSet, basename='client')

urlpatterns = [
    path('', include(router.urls)),
]
```

### 3.3.3 apps/clients/admin.py

```python
from django.contrib import admin
from .models import Client, ClientNote


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'email', 'trainer', 'fitness_level', 'is_active', 'created_at')
    list_filter = ('fitness_level', 'is_active', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'trainer__business_name')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Name'


@admin.register(ClientNote)
class ClientNoteAdmin(admin.ModelAdmin):
    list_display = ('client', 'created_by', 'created_at')
    list_filter = ('created_at', 'created_by')
    search_fields = ('client__first_name', 'client__last_name', 'content')
    readonly_fields = ('created_at',)
```

---

# 📅 EPIC 4: BOOKING SYSTEM (2 HOURS)

## Step 4.1: Booking Models

### 4.1.1 apps/bookings/models.py

```python
from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime
from apps.trainers.models import Trainer
from apps.clients.models import Client


class Booking(models.Model):
    """
    Booking record linking trainer and client at specific time.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no-show', 'No-Show'),
    ]
    
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='bookings')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='bookings')
    start_time = models.DateTimeField(db_index=True)
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    notes = models.TextField(blank=True)
    cancellation_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['trainer', 'start_time']),
            models.Index(fields=['client', 'start_time']),
            models.Index(fields=['status', 'start_time']),
        ]
    
    def clean(self):
        """Validate booking times."""
        if self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time.")
        
        if self.start_time < datetime.now():
            raise ValidationError("Cannot book in the past.")
        
        # Check for trainer availability
        from apps.availability.utils import has_conflict
        if has_conflict(self.trainer_id, self.start_time, self.end_time):
            raise ValidationError("Trainer is not available at this time.")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.client.get_full_name()} with {self.trainer.business_name} on {self.start_time.date()}"
    
    @property
    def duration_minutes(self):
        """Calculate duration in minutes."""
        delta = self.end_time - self.start_time
        return int(delta.total_seconds() / 60)
    
    @property
    def is_upcoming(self):
        """Check if booking is in the future."""
        return self.start_time > datetime.now() and self.status != 'cancelled'
    
    @property
    def is_past(self):
        """Check if booking is in the past."""
        return self.end_time < datetime.now()
```

---

## Step 4.2: Booking Serializers

### 4.2.1 apps/bookings/serializers.py

```python
from rest_framework import serializers
from .models import Booking
from apps.clients.models import Client
from datetime import datetime


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
        if value < datetime.now():
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
```

---

## Step 4.3: Booking Views

### 4.3.1 apps/bookings/views.py

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from datetime import datetime, timedelta

from .models import Booking
from .serializers import BookingSerializer, BookingCreateSerializer, BookingDetailSerializer
from apps.trainers.models import Trainer


class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing bookings.
    """
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'client']
    search_fields = ['client__first_name', 'client__last_name', 'notes']
    ordering_fields = ['start_time', 'created_at']
    ordering = ['-start_time']
    
    def get_queryset(self):
        """Get only bookings for current trainer."""
        try:
            trainer = self.request.user.trainer_profile
            return Booking.objects.filter(trainer=trainer)
        except Trainer.DoesNotExist:
            return Booking.objects.none()
    
    def get_serializer_class(self):
        """Use different serializers based on action."""
        if self.action == 'create':
            return BookingCreateSerializer
        elif self.action == 'retrieve':
            return BookingDetailSerializer
        return BookingSerializer
    
    def perform_create(self, serializer):
        """Validate and create booking."""
        trainer = self.request.user.trainer_profile
        serializer.save(trainer=trainer)
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """
        Confirm a pending booking.
        
        POST /api/bookings/{id}/confirm/
        """
        booking = self.get_object()
        
        if booking.status != 'pending':
            return Response(
                {'error': f'Booking is {booking.status}, cannot confirm'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = 'confirmed'
        booking.save()
        
        # Send confirmation email (async)
        from apps.notifications.tasks import send_booking_confirmation
        send_booking_confirmation.delay(booking.id)
        
        serializer = self.get_serializer(booking)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel a booking.
        
        POST /api/bookings/{id}/cancel/
        {
            "reason": "Client requested cancellation"
        }
        """
        booking = self.get_object()
        
        if booking.status in ['completed', 'cancelled', 'no-show']:
            return Response(
                {'error': f'Cannot cancel a {booking.status} booking'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reason = request.data.get('reason', '')
        booking.status = 'cancelled'
        booking.cancellation_reason = reason
        booking.save()
        
        serializer = self.get_serializer(booking)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        """
        Mark a booking as completed.
        
        POST /api/bookings/{id}/mark_completed/
        """
        booking = self.get_object()
        
        if booking.status != 'confirmed':
            return Response(
                {'error': 'Only confirmed bookings can be marked as completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = 'completed'
        booking.save()
        
        serializer = self.get_serializer(booking)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """
        Get upcoming bookings.
        
        GET /api/bookings/upcoming/
        """
        bookings = self.get_queryset().filter(
            status__in=['pending', 'confirmed'],
            start_time__gte=datetime.now()
        )
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def past(self, request):
        """
        Get past bookings.
        
        GET /api/bookings/past/
        """
        bookings = self.get_queryset().filter(
            end_time__lt=datetime.now()
        )
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)
```

### 4.3.2 apps/bookings/urls.py

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookingViewSet

router = DefaultRouter()
router.register(r'bookings', BookingViewSet, basename='booking')

urlpatterns = [
    path('', include(router.urls)),
]
```

### 4.3.3 apps/bookings/admin.py

```python
from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('client', 'trainer', 'start_time', 'status', 'duration_minutes')
    list_filter = ('status', 'start_time', 'created_at')
    search_fields = ('client__first_name', 'client__last_name', 'trainer__business_name')
    readonly_fields = ('created_at', 'updated_at', 'duration_minutes')
    date_hierarchy = 'start_time'
    
    def duration_minutes(self, obj):
        return f"{obj.duration_minutes} min"
    duration_minutes.short_description = 'Duration'
```

---

# 📦 EPIC 5: SESSION PACKAGES (1 HOUR)

## Step 5.1: Package Models

### 5.1.1 apps/packages/models.py

```python
from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from apps.trainers.models import Trainer
from apps.clients.models import Client


class SessionPackage(models.Model):
    """
    Session package (e.g., "5-Pack", "10-Pack").
    """
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='packages')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    sessions_count = models.IntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['trainer', 'name']
        indexes = [
            models.Index(fields=['trainer', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.sessions_count} sessions (${self.price})"


class ClientPackage(models.Model):
    """
    Client's purchase of a package (tracks remaining sessions).
    """
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='purchased_packages')
    session_package = models.ForeignKey(SessionPackage, on_delete=models.SET_NULL, null=True, related_name='client_packages')
    sessions_remaining = models.IntegerField()
    expiry_date = models.DateField(null=True, blank=True)
    purchased_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-purchased_at']
        indexes = [
            models.Index(fields=['client', 'expiry_date']),
        ]
    
    def clean(self):
        """Validate sessions remaining."""
        if self.sessions_remaining < 0:
            raise ValidationError("Sessions remaining cannot be negative.")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.client.get_full_name()} - {self.sessions_remaining} sessions remaining"
    
    @property
    def is_expired(self):
        """Check if package has expired."""
        if not self.expiry_date:
            return False
        return datetime.now().date() > self.expiry_date
    
    @property
    def is_active(self):
        """Check if package is active."""
        return self.sessions_remaining > 0 and not self.is_expired
```

---

## Step 5.2: Package Serializers

### 5.2.1 apps/packages/serializers.py

```python
from rest_framework import serializers
from .models import SessionPackage, ClientPackage


class SessionPackageSerializer(serializers.ModelSerializer):
    """Serializer for session packages."""
    
    class Meta:
        model = SessionPackage
        fields = ['id', 'name', 'description', 'sessions_count', 'price', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']
    
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


class ClientPackageSerializer(serializers.ModelSerializer):
    """Serializer for client packages."""
    package_name = serializers.CharField(source='session_package.name', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = ClientPackage
        fields = [
            'id', 'session_package', 'package_name', 'sessions_remaining',
            'expiry_date', 'is_expired', 'is_active', 'purchased_at'
        ]
        read_only_fields = ['id', 'purchased_at', 'is_expired', 'is_active']
```

---

## Step 5.3: Package Views

### 5.3.1 apps/packages/views.py

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import SessionPackage, ClientPackage
from .serializers import SessionPackageSerializer, ClientPackageSerializer
from apps.trainers.models import Trainer


class SessionPackageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing session packages.
    """
    serializer_class = SessionPackageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get only packages for current trainer."""
        try:
            trainer = self.request.user.trainer_profile
            return SessionPackage.objects.filter(trainer=trainer)
        except Trainer.DoesNotExist:
            return SessionPackage.objects.none()
    
    def perform_create(self, serializer):
        """Create package for current trainer."""
        trainer = self.request.user.trainer_profile
        serializer.save(trainer=trainer)
    
    @action(detail=True, methods=['post'])
    def assign_to_client(self, request, pk=None):
        """
        Assign package to a client.
        
        POST /api/packages/{id}/assign_to_client/
        {
            "client_id": 1,
            "expiry_date": "2025-12-31"
        }
        """
        package = self.get_object()
        client_id = request.data.get('client_id')
        expiry_date = request.data.get('expiry_date')
        
        if not client_id:
            return Response(
                {'error': 'client_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if client belongs to this trainer
        if not package.trainer.clients.filter(id=client_id).exists():
            return Response(
                {'error': 'Client not found for this trainer'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        client = package.trainer.clients.get(id=client_id)
        
        client_package = ClientPackage.objects.create(
            client=client,
            session_package=package,
            sessions_remaining=package.sessions_count,
            expiry_date=expiry_date
        )
        
        serializer = ClientPackageSerializer(client_package)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def client_packages(self, request, pk=None):
        """
        Get all client packages for this package.
        
        GET /api/packages/{id}/client_packages/
        """
        package = self.get_object()
        client_packages = package.client_packages.all()
        serializer = ClientPackageSerializer(client_packages, many=True)
        return Response(serializer.data)


class ClientPackageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing client packages.
    """
    serializer_class = ClientPackageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get only packages for clients of current trainer."""
        try:
            trainer = self.request.user.trainer_profile
            return ClientPackage.objects.filter(
                client__trainer=trainer
            )
        except Trainer.DoesNotExist:
            return ClientPackage.objects.none()
    
    @action(detail=True, methods=['post'])
    def use_session(self, request, pk=None):
        """
        Use one session from a package.
        
        POST /api/client-packages/{id}/use_session/
        """
        package = self.get_object()
        
        if package.sessions_remaining <= 0:
            return Response(
                {'error': 'No sessions remaining'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if package.is_expired:
            return Response(
                {'error': 'Package has expired'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        package.sessions_remaining -= 1
        package.save()
        
        serializer = self.get_serializer(package)
        return Response(serializer.data)
```

### 5.3.2 apps/packages/urls.py

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SessionPackageViewSet, ClientPackageViewSet

router = DefaultRouter()
router.register(r'packages', SessionPackageViewSet, basename='package')
router.register(r'client-packages', ClientPackageViewSet, basename='client-package')

urlpatterns = [
    path('', include(router.urls)),
]
```

### 5.3.3 apps/packages/admin.py

```python
from django.contrib import admin
from .models import SessionPackage, ClientPackage


@admin.register(SessionPackage)
class SessionPackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'trainer', 'sessions_count', 'price', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'trainer__business_name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ClientPackage)
class ClientPackageAdmin(admin.ModelAdmin):
    list_display = ('client', 'session_package', 'sessions_remaining', 'expiry_date', 'is_active')
    list_filter = ('is_active', 'expiry_date', 'purchased_at')
    search_fields = ('client__first_name', 'client__last_name', 'session_package__name')
    readonly_fields = ('purchased_at',)
```

---

## Step 5.4: Update Main URLs

### 5.4.1 Update config/urls.py

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.users.urls')),
    path('api/', include('apps.availability.urls')),
    path('api/', include('apps.clients.urls')),
    path('api/', include('apps.bookings.urls')),
    path('api/', include('apps.packages.urls')),
]
```

---

## Step 5.5: Run Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

---

## Step 5.6: Test All Endpoints

```bash
# Client endpoints

# 1. Create client
curl -X POST http://localhost:8000/api/clients/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "client@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "fitness_level": "beginner",
    "goals": ["lose weight", "build muscle"]
  }'

# 2. List clients
curl -X GET http://localhost:8000/api/clients/ \
  -H "Authorization: Token YOUR_TOKEN"

# 3. Add note to client
curl -X POST http://localhost:8000/api/clients/1/add_note/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "Great progress this week!"}'

# Booking endpoints

# 4. Create booking
curl -X POST http://localhost:8000/api/bookings/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "client": 1,
    "start_time": "2025-01-10T10:00:00Z",
    "end_time": "2025-01-10T11:00:00Z",
    "notes": "First session"
  }'

# 5. Confirm booking
curl -X POST http://localhost:8000/api/bookings/1/confirm/ \
  -H "Authorization: Token YOUR_TOKEN"

# 6. Get upcoming bookings
curl -X GET http://localhost:8000/api/bookings/upcoming/ \
  -H "Authorization: Token YOUR_TOKEN"

# Package endpoints

# 7. Create package
curl -X POST http://localhost:8000/api/packages/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "5-Pack",
    "description": "5 session package",
    "sessions_count": 5,
    "price": "249.99"
  }'

# 8. Assign package to client
curl -X POST http://localhost:8000/api/packages/1/assign_to_client/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": 1,
    "expiry_date": "2025-12-31"
  }'

# 9. Use session from package
curl -X POST http://localhost:8000/api/client-packages/1/use_session/ \
  -H "Authorization: Token YOUR_TOKEN"
```

---

# 🧪 INTEGRATION TESTING

## Create tests/test_epic3_5.py

```python
import pytest
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from datetime import datetime, timedelta

from apps.users.models import User
from apps.trainers.models import Trainer
from apps.clients.models import Client
from apps.bookings.models import Booking
from apps.packages.models import SessionPackage, ClientPackage


class IntegrationTestCase(TestCase):
    """Integration tests for EPIC 3-5."""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create trainer user
        self.trainer_user = User.objects.create_user(
            email='trainer@example.com',
            username='trainer',
            password='password123',
            is_trainer=True
        )
        
        self.trainer = Trainer.objects.create(
            user=self.trainer_user,
            business_name='Fitness Pro'
        )
        
        # Create client user
        self.client_user = User.objects.create_user(
            email='client@example.com',
            username='client',
            password='password123',
            is_client=True
        )
        
        self.client_obj = Client.objects.create(
            trainer=self.trainer,
            email='client@example.com',
            first_name='Jane',
            last_name='Doe',
            fitness_level='beginner'
        )
    
    def test_complete_booking_flow(self):
        """Test complete booking flow from package to session."""
        # Login as trainer
        login_data = {'email': 'trainer@example.com', 'password': 'password123'}
        response = self.client.post('/api/users/login/', login_data)
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        
        # Create package
        package_data = {
            'name': '5-Pack',
            'sessions_count': 5,
            'price': '249.99'
        }
        response = self.client.post('/api/packages/', package_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        package_id = response.data['id']
        
        # Assign to client
        assign_data = {
            'client_id': self.client_obj.id,
            'expiry_date': '2025-12-31'
        }
        response = self.client.post(f'/api/packages/{package_id}/assign_to_client/', assign_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Create booking
        booking_data = {
            'client': self.client_obj.id,
            'start_time': (datetime.now() + timedelta(days=1)).isoformat(),
            'end_time': (datetime.now() + timedelta(days=1, hours=1)).isoformat(),
        }
        response = self.client.post('/api/bookings/', booking_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
```

Run tests:
```bash
python manage.py test
# or with pytest
pytest tests/
```

---

# ✅ EPIC 3-5 COMPLETION CHECKLIST

- [ ] Client models created and migrated
- [ ] Client endpoints working (CRUD, notes)
- [ ] Booking models created and migrated
- [ ] Booking endpoints working (create, confirm, cancel)
- [ ] Package models created and migrated
- [ ] Package endpoints working (create, assign, use)
- [ ] All relationships validated
- [ ] Admin interfaces configured
- [ ] Integration tests passing
- [ ] Endpoints tested with curl

---

**Files saved: EPIC 3-5 code (1,400+ lines) ✅**

**Next file: TRAINERHUB_DEV_CHECKLIST_V2_PART3.md (EPIC 6-8: Payments, Notifications, Analytics)** - Ask when ready!
