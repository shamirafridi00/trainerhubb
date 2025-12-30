"""
Public API views for serving trainer pages without authentication.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch

from apps.trainers.models import Trainer, PaymentLinks
from apps.trainers.serializers import TrainerSerializer, PaymentLinksSerializer
from apps.pages.models import Page, PageSection
from apps.pages.serializers import PageSerializer, PageSectionSerializer
from apps.availability.models import AvailabilitySlot
from apps.availability.serializers import AvailabilitySlotSerializer


class PublicPageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public API endpoint for viewing published pages.
    No authentication required.
    """
    serializer_class = PageSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """Get published pages for the detected trainer."""
        trainer_slug = self.kwargs.get('trainer_slug')
        
        if trainer_slug:
            # Find trainer by username or email prefix
            trainer = Trainer.objects.filter(
                user__username=trainer_slug
            ).first()
            
            if not trainer:
                trainer = Trainer.objects.filter(
                    user__email__startswith=trainer_slug
                ).first()
            
            if trainer:
                return Page.objects.filter(
                    trainer=trainer,
                    is_published=True
                ).prefetch_related(
                    Prefetch('sections', queryset=PageSection.objects.filter(is_visible=True).order_by('order'))
                ).order_by('-published_at')
        
        return Page.objects.none()
    
    def retrieve(self, request, *args, **kwargs):
        """Get a specific page by slug."""
        trainer_slug = kwargs.get('trainer_slug')
        page_slug = kwargs.get('pk')  # We'll use slug as pk for public pages
        
        # Find trainer
        trainer = Trainer.objects.filter(user__username=trainer_slug).first()
        if not trainer:
            trainer = Trainer.objects.filter(user__email__startswith=trainer_slug).first()
        
        if not trainer:
            return Response(
                {'detail': 'Trainer not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Find page
        page = get_object_or_404(
            Page,
            trainer=trainer,
            slug=page_slug,
            is_published=True
        )
        
        # Apply white-label settings if available
        white_label_settings = getattr(trainer, 'whitelabel_settings', None)
        
        serializer = self.get_serializer(page)
        response_data = serializer.data
        
        # Add white-label settings to response
        if white_label_settings:
            response_data['white_label'] = {
                'remove_branding': white_label_settings.remove_branding,
                'custom_logo': white_label_settings.custom_logo.url if white_label_settings.custom_logo else None,
                'primary_color': white_label_settings.primary_color,
                'secondary_color': white_label_settings.secondary_color,
                'accent_color': white_label_settings.accent_color,
                'text_color': white_label_settings.text_color,
                'background_color': white_label_settings.background_color,
                'font_family': white_label_settings.font_family,
                'favicon': white_label_settings.favicon.url if white_label_settings.favicon else None,
                'custom_css': white_label_settings.custom_css,
            }
        
        return Response(response_data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_trainer_profile(request, trainer_slug):
    """
    Get trainer's public profile information.
    No authentication required.
    """
    trainer = Trainer.objects.filter(user__username=trainer_slug).first()
    if not trainer:
        trainer = Trainer.objects.filter(user__email__startswith=trainer_slug).first()
    
    if not trainer:
        return Response(
            {'detail': 'Trainer not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Return only public information
    return Response({
        'business_name': trainer.business_name,
        'bio': trainer.bio,
        'expertise': trainer.expertise,
        'location': trainer.location,
        'rating': trainer.rating,
        'total_sessions': trainer.total_sessions,
        'is_verified': trainer.is_verified,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def get_trainer_availability(request, trainer_slug):
    """
    Get trainer's availability slots for booking.
    No authentication required.
    """
    trainer = Trainer.objects.filter(user__username=trainer_slug).first()
    if not trainer:
        trainer = Trainer.objects.filter(user__email__startswith=trainer_slug).first()
    
    if not trainer:
        return Response(
            {'detail': 'Trainer not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get availability for the trainer
    availabilities = AvailabilitySlot.objects.filter(
        trainer=trainer,
        is_available=True
    ).order_by('day_of_week', 'start_time')
    
    serializer = AvailabilitySlotSerializer(availabilities, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def submit_contact_form(request, trainer_slug):
    """
    Submit a contact form inquiry to the trainer.
    No authentication required.
    """
    trainer = Trainer.objects.filter(user__username=trainer_slug).first()
    if not trainer:
        trainer = Trainer.objects.filter(user__email__startswith=trainer_slug).first()
    
    if not trainer:
        return Response(
            {'detail': 'Trainer not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Validate required fields
    required_fields = ['name', 'email', 'subject', 'message']
    for field in required_fields:
        if not request.data.get(field):
            return Response(
                {'detail': f'{field} is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # TODO: Send email to trainer with contact form data
    # For now, just return success
    # This will be implemented in Epic 6.4
    
    return Response({
        'detail': 'Message sent successfully',
        'data': {
            'name': request.data.get('name'),
            'email': request.data.get('email'),
            'subject': request.data.get('subject'),
            'message': request.data.get('message'),
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_payment_methods(request, trainer_slug):
    """
    Get payment methods configured by the trainer.
    No authentication required.
    """
    trainer = Trainer.objects.filter(user__username=trainer_slug).first()
    if not trainer:
        trainer = Trainer.objects.filter(user__email__startswith=trainer_slug).first()
    
    if not trainer:
        return Response(
            {'detail': 'Trainer not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get payment links if they exist
    try:
        payment_links = PaymentLinks.objects.get(trainer=trainer)
        serializer = PaymentLinksSerializer(payment_links)
        return Response(serializer.data)
    except PaymentLinks.DoesNotExist:
        return Response({
            'show_on_public_pages': False,
            'available_methods': []
        })

