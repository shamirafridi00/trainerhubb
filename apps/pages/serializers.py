from rest_framework import serializers
from .models import PageTemplate, Page, PageSection


class PageSectionSerializer(serializers.ModelSerializer):
    """Serializer for page sections"""
    
    class Meta:
        model = PageSection
        fields = [
            'id', 'section_type', 'order', 'content', 'is_visible',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PageSerializer(serializers.ModelSerializer):
    """Serializer for pages"""
    sections = PageSectionSerializer(many=True, read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    public_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Page
        fields = [
            'id', 'trainer', 'title', 'slug', 'template', 'template_name',
            'content', 'is_published', 'published_at',
            'seo_title', 'seo_description', 'seo_keywords',
            'custom_domain', 'public_url', 'sections',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'trainer', 'created_at', 'updated_at', 'public_url']
    
    def get_public_url(self, obj):
        """Get public URL for published pages"""
        if obj.is_published:
            return obj.get_public_url()
        return None
    
    def validate_slug(self, value):
        """Validate slug format"""
        if not value.replace('-', '').replace('_', '').isalnum():
            raise serializers.ValidationError(
                "Slug can only contain letters, numbers, hyphens, and underscores."
            )
        return value


class PageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating pages"""
    
    class Meta:
        model = Page
        fields = ['title', 'slug', 'template', 'content', 'seo_title', 'seo_description', 'seo_keywords']
    
    def validate_slug(self, value):
        """Validate slug format"""
        if not value.replace('-', '').replace('_', '').isalnum():
            raise serializers.ValidationError(
                "Slug can only contain letters, numbers, hyphens, and underscores."
            )
        return value


class PageTemplateSerializer(serializers.ModelSerializer):
    """Serializer for page templates"""
    
    class Meta:
        model = PageTemplate
        fields = [
            'id', 'name', 'slug', 'description', 'thumbnail',
            'category', 'is_premium', 'template_data', 'available_for_plans',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

