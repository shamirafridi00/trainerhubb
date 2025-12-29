from django.contrib import admin
from .models import Client, ClientNote


class ClientNoteInline(admin.TabularInline):
    """Inline admin for client notes."""
    model = ClientNote
    extra = 0
    fields = ['content', 'created_by', 'created_at']
    readonly_fields = ['created_at']


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """Admin interface for Client model."""
    list_display = ('get_full_name', 'email', 'trainer', 'fitness_level', 'is_active', 'created_at')
    list_filter = ('fitness_level', 'is_active', 'created_at', 'trainer')
    search_fields = ('first_name', 'last_name', 'email', 'trainer__business_name')
    ordering = ('-created_at',)
    inlines = [ClientNoteInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('trainer', 'first_name', 'last_name', 'email', 'phone')
        }),
        ('Fitness Information', {
            'fields': ('fitness_level', 'goals', 'preferences', 'notes')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Name'


@admin.register(ClientNote)
class ClientNoteAdmin(admin.ModelAdmin):
    """Admin interface for ClientNote model."""
    list_display = ('client', 'content_preview', 'created_by', 'created_at')
    list_filter = ('created_at', 'created_by')
    search_fields = ('client__first_name', 'client__last_name', 'content')
    ordering = ('-created_at',)
    
    fields = ('client', 'content', 'created_by', 'created_at')
    readonly_fields = ('created_at',)
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'
