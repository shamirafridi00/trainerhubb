from django.db import models
from apps.trainers.models import Trainer


class PageTemplate(models.Model):
    """Pre-designed page templates"""
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to='templates/thumbnails/', null=True, blank=True)
    category = models.CharField(max_length=50)  # fitness, wellness, nutrition, general
    is_premium = models.BooleanField(default=False)
    template_data = models.JSONField(default=dict)  # Template structure
    available_for_plans = models.JSONField(default=list)  # ['free', 'pro', 'business']
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['is_premium']),
        ]
    
    def __str__(self):
        return self.name


class Page(models.Model):
    """Trainer's published pages"""
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='pages')
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    template = models.ForeignKey(PageTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    content = models.JSONField(default=dict)  # Page structure and content
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    seo_title = models.CharField(max_length=255, blank=True)
    seo_description = models.TextField(blank=True)
    seo_keywords = models.CharField(max_length=500, blank=True)
    custom_domain = models.ForeignKey('admin_panel.CustomDomain', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['trainer', 'slug']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['trainer', 'is_published']),
            models.Index(fields=['trainer', 'slug']),
            models.Index(fields=['is_published', 'published_at']),
        ]
    
    def __str__(self):
        return f"{self.trainer.business_name} - {self.title}"
    
    def get_public_url(self):
        """Generate public URL for the page"""
        if self.custom_domain and self.custom_domain.status == 'active':
            return f"https://{self.custom_domain.domain}/{self.slug}"
        trainer_slug = self.trainer.user.username or str(self.trainer.id)
        return f"https://{trainer_slug}.trainerhubb.app/{self.slug}"


class PageSection(models.Model):
    """Reusable content sections"""
    SECTION_TYPES = [
        ('hero', 'Hero'),
        ('services', 'Services'),
        ('about', 'About'),
        ('testimonials', 'Testimonials'),
        ('contact', 'Contact'),
        ('pricing', 'Pricing'),
        ('gallery', 'Gallery'),
        ('faq', 'FAQ'),
        ('booking', 'Booking'),
    ]
    
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='sections')
    section_type = models.CharField(max_length=50, choices=SECTION_TYPES)
    order = models.IntegerField(default=0)
    content = models.JSONField(default=dict)  # Section-specific data
    is_visible = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
        indexes = [
            models.Index(fields=['page', 'order']),
            models.Index(fields=['section_type']),
        ]
    
    def __str__(self):
        return f"{self.page.title} - {self.get_section_type_display()}"
