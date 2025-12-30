from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import models

from .models import PageTemplate, Page, PageSection
from .serializers import (
    PageTemplateSerializer, PageSerializer, PageCreateSerializer, PageSectionSerializer
)
from apps.payments.permissions import check_usage_limit


class PageTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for page templates (read-only)"""
    queryset = PageTemplate.objects.all()
    serializer_class = PageTemplateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter templates by trainer's plan"""
        queryset = super().get_queryset()
        
        # Get trainer's subscription plan
        if hasattr(self.request.user, 'trainer_profile'):
            trainer = self.request.user.trainer_profile
            try:
                from apps.payments.models import Subscription
                subscription = Subscription.objects.get(trainer=trainer)
                plan = subscription.plan
            except:
                plan = 'free'
            
            # Filter by available plans
            queryset = queryset.filter(
                models.Q(available_for_plans__contains=[plan]) |
                models.Q(available_for_plans__contains=['all'])
            )
        
        return queryset


class PageViewSet(viewsets.ModelViewSet):
    """ViewSet for managing trainer pages"""
    permission_classes = [IsAuthenticated]
    serializer_class = PageSerializer
    
    def get_queryset(self):
        """Filter to current trainer's pages"""
        if hasattr(self.request.user, 'trainer_profile'):
            return Page.objects.filter(trainer=self.request.user.trainer_profile)
        return Page.objects.none()
    
    def get_serializer_class(self):
        """Use different serializer for create"""
        if self.action == 'create':
            return PageCreateSerializer
        return PageSerializer
    
    def perform_create(self, serializer):
        """Set trainer and check usage limits"""
        if not hasattr(self.request.user, 'trainer_profile'):
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'error': 'User is not a trainer'})
        
        trainer = self.request.user.trainer_profile
        
        # Check page usage limit
        can_create, current_count, limit = check_usage_limit(trainer, 'pages')
        if not can_create:
            raise serializers.ValidationError({
                'error': 'Usage limit reached',
                'detail': f'You have reached your limit of {limit} pages. Upgrade your plan to add more.',
                'current_count': current_count,
                'limit': limit
            })
        
        serializer.save(trainer=trainer)
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish a page"""
        page = self.get_object()
        
        # Validate page has at least one section
        if not page.sections.exists():
            return Response(
                {'error': 'Page must have at least one section before publishing'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        page.is_published = True
        if not page.published_at:
            page.published_at = timezone.now()
        page.save()
        
        serializer = self.get_serializer(page)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def unpublish(self, request, pk=None):
        """Unpublish a page"""
        page = self.get_object()
        page.is_published = False
        page.save()
        
        serializer = self.get_serializer(page)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get', 'post'], url_path='sections')
    def manage_sections(self, request, pk=None):
        """Manage sections for a page"""
        page = self.get_object()
        
        if request.method == 'GET':
            sections = page.sections.all()
            serializer = PageSectionSerializer(sections, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = PageSectionSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(page=page)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['patch', 'delete'], url_path='sections/(?P<section_id>[^/.]+)')
    def manage_section(self, request, pk=None, section_id=None):
        """Update or delete a specific section"""
        page = self.get_object()
        
        try:
            section = page.sections.get(id=section_id)
        except PageSection.DoesNotExist:
            return Response(
                {'error': 'Section not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if request.method == 'PATCH':
            serializer = PageSectionSerializer(section, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == 'DELETE':
            section.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
