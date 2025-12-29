from django.contrib import admin
from .models import SessionPackage, ClientPackage


@admin.register(SessionPackage)
class SessionPackageAdmin(admin.ModelAdmin):
    """Admin interface for SessionPackage model."""
    list_display = ('name', 'trainer', 'sessions_count', 'price', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at', 'trainer')
    search_fields = ('name', 'trainer__business_name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Package Information', {
            'fields': ('trainer', 'name', 'description')
        }),
        ('Pricing & Sessions', {
            'fields': ('sessions_count', 'price', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        queryset = super().get_queryset(request)
        return queryset.select_related('trainer')


@admin.register(ClientPackage)
class ClientPackageAdmin(admin.ModelAdmin):
    """Admin interface for ClientPackage model."""
    list_display = ('get_client_name', 'get_package_name', 'sessions_remaining', 'expiry_date', 'is_active', 'purchased_at')
    list_filter = ('expiry_date', 'purchased_at', 'client__trainer')
    search_fields = ('client__first_name', 'client__last_name', 'session_package__name')
    readonly_fields = ('purchased_at', 'is_expired', 'is_active')
    ordering = ('-purchased_at',)
    date_hierarchy = 'purchased_at'
    
    fieldsets = (
        ('Package Assignment', {
            'fields': ('client', 'session_package')
        }),
        ('Session Tracking', {
            'fields': ('sessions_remaining', 'expiry_date')
        }),
        ('Status', {
            'fields': ('is_expired', 'is_active', 'purchased_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        queryset = super().get_queryset(request)
        return queryset.select_related('client', 'session_package', 'client__trainer')
    
    def get_client_name(self, obj):
        return obj.client.get_full_name()
    get_client_name.short_description = 'Client'
    get_client_name.admin_order_field = 'client__first_name'
    
    def get_package_name(self, obj):
        return obj.session_package.name if obj.session_package else 'N/A'
    get_package_name.short_description = 'Package'
    get_package_name.admin_order_field = 'session_package__name'
