"""
Trainer Views
Handles trainer profile and white-label settings management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Trainer, WhiteLabelSettings, PaymentLinks
from .serializers import TrainerSerializer, WhiteLabelSettingsSerializer, PaymentLinksSerializer
from apps.payments.permissions import RequiresFeature
from apps.payments.decorators import require_feature


class TrainerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing trainer profiles.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TrainerSerializer
    
    def get_queryset(self):
        """Filter to current user's trainer profile."""
        if hasattr(self.request.user, 'trainer_profile'):
            return Trainer.objects.filter(id=self.request.user.trainer_profile.id)
        return Trainer.objects.none()
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Get current trainer's profile.
        
        GET /api/trainers/me/
        """
        if not hasattr(request.user, 'trainer_profile'):
            return Response(
                {'error': 'User is not a trainer'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(request.user.trainer_profile)
        return Response(serializer.data)


class WhiteLabelSettingsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing white-label settings (Business tier only).
    """
    permission_classes = [IsAuthenticated]
    serializer_class = WhiteLabelSettingsSerializer
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        """Filter to current user's white-label settings."""
        if hasattr(self.request.user, 'trainer_profile'):
            return WhiteLabelSettings.objects.filter(
                trainer=self.request.user.trainer_profile
            )
        return WhiteLabelSettings.objects.none()
    
    @action(detail=False, methods=['get', 'put', 'patch'])
    @require_feature('white_label')
    def current(self, request):
        """
        Get or update current trainer's white-label settings.
        Requires Business tier subscription.
        
        GET /api/trainers/whitelabel/current/
        PUT /api/trainers/whitelabel/current/
        PATCH /api/trainers/whitelabel/current/
        """
        if not hasattr(request.user, 'trainer_profile'):
            return Response(
                {'error': 'User is not a trainer'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        trainer = request.user.trainer_profile
        
        # Get or create white-label settings
        settings, created = WhiteLabelSettings.objects.get_or_create(
            trainer=trainer
        )
        
        if request.method == 'GET':
            serializer = self.get_serializer(settings)
            return Response(serializer.data)
        
        # Update settings
        serializer = self.get_serializer(
            settings,
            data=request.data,
            partial=(request.method == 'PATCH')
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    @require_feature('white_label')
    def upload_logo(self, request):
        """
        Upload custom logo.
        Requires Business tier subscription.
        
        POST /api/trainers/whitelabel/upload-logo/
        """
        if not hasattr(request.user, 'trainer_profile'):
            return Response(
                {'error': 'User is not a trainer'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        trainer = request.user.trainer_profile
        settings, created = WhiteLabelSettings.objects.get_or_create(
            trainer=trainer
        )
        
        if 'logo' not in request.FILES:
            return Response(
                {'error': 'No logo file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        logo_file = request.FILES['logo']
        
        # Validate file size
        if logo_file.size > 500 * 1024:  # 500KB
            return Response(
                {'error': 'Logo file size must be less than 500KB'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate file type
        allowed_types = ['image/png', 'image/jpeg', 'image/svg+xml']
        if logo_file.content_type not in allowed_types:
            return Response(
                {'error': 'Logo must be PNG, JPG, or SVG'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        settings.custom_logo = logo_file
        settings.save()
        
        serializer = self.get_serializer(settings)
        return Response(serializer.data)
    
    @action(detail=False, methods=['delete'])
    def remove_logo(self, request):
        """
        Remove custom logo.
        
        DELETE /api/trainers/whitelabel/remove-logo/
        """
        if not hasattr(request.user, 'trainer_profile'):
            return Response(
                {'error': 'User is not a trainer'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        trainer = request.user.trainer_profile
        
        try:
            settings = WhiteLabelSettings.objects.get(trainer=trainer)
            settings.custom_logo.delete()
            settings.save()
            return Response({'message': 'Logo removed'})
        except WhiteLabelSettings.DoesNotExist:
            return Response(
                {'error': 'No white-label settings found'},
                status=status.HTTP_404_NOT_FOUND
            )


class PaymentLinksViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing payment links configuration.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentLinksSerializer
    
    def get_queryset(self):
        """Filter to current user's payment links."""
        if hasattr(self.request.user, 'trainer_profile'):
            return PaymentLinks.objects.filter(
                trainer=self.request.user.trainer_profile
            )
        return PaymentLinks.objects.none()
    
    @action(detail=False, methods=['get', 'put', 'patch'])
    def current(self, request):
        """
        Get or update current trainer's payment links.
        
        GET /api/trainers/payment-links/current/
        PUT /api/trainers/payment-links/current/
        PATCH /api/trainers/payment-links/current/
        """
        if not hasattr(request.user, 'trainer_profile'):
            return Response(
                {'error': 'User is not a trainer'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        trainer = request.user.trainer_profile
        
        # Get or create payment links
        payment_links, created = PaymentLinks.objects.get_or_create(
            trainer=trainer
        )
        
        if request.method == 'GET':
            serializer = self.get_serializer(payment_links)
            return Response(serializer.data)
        
        # Update payment links
        serializer = self.get_serializer(
            payment_links,
            data=request.data,
            partial=(request.method == 'PATCH')
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
