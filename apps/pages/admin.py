from django.contrib import admin
from .models import PageTemplate, Page, PageSection


@admin.register(PageTemplate)
class PageTemplateAdmin(admin.ModelAdmin):
    """Admin interface for page templates"""
    list_display = ['name', 'category', 'is_premium', 'created_at']
    list_filter = ['category', 'is_premium', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    """Admin interface for pages"""
    list_display = ['title', 'trainer', 'slug', 'is_published', 'published_at', 'created_at']
    list_filter = ['is_published', 'created_at', 'published_at']
    search_fields = ['title', 'slug', 'trainer__business_name']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        """Optimize queries"""
        return super().get_queryset(request).select_related('trainer', 'template')


@admin.register(PageSection)
class PageSectionAdmin(admin.ModelAdmin):
    """Admin interface for page sections"""
    list_display = ['page', 'section_type', 'order', 'is_visible']
    list_filter = ['section_type', 'is_visible']
    search_fields = ['page__title']
    
    def get_queryset(self, request):
        """Optimize queries"""
        return super().get_queryset(request).select_related('page')
