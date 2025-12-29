"""
Django admin configuration for FAQ models.
"""

from django.contrib import admin
from .models import FAQ


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    """Admin interface for FAQ model."""
    
    list_display = ('question_preview', 'category', 'keyword_count', 'created_at', 'updated_at')
    list_filter = ('category', 'created_at', 'updated_at')
    search_fields = ('question', 'answer', 'keywords', 'category')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('FAQ Content', {
            'fields': ('id', 'question', 'answer')
        }),
        ('Organization', {
            'fields': ('category', 'keywords')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def question_preview(self, obj):
        """Display question preview."""
        preview = obj.question[:80]
        if len(obj.question) > 80:
            preview += '...'
        return preview
    question_preview.short_description = 'Question'
    
    def keyword_count(self, obj):
        """Display number of keywords."""
        return len(obj.keywords) if obj.keywords else 0
    keyword_count.short_description = 'Keywords'
