"""
Django admin configuration for chatbot models.
"""

from django.contrib import admin
from .models import Conversation, Message, HumanHandoffRequest


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """Admin interface for Conversation model."""
    
    list_display = ('session_id_short', 'language', 'message_count', 'created_at', 'last_active', 'duration')
    list_filter = ('language', 'created_at', 'last_active')
    search_fields = ('session_id',)
    readonly_fields = ('id', 'session_id', 'created_at', 'last_active', 'message_count', 'duration')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Session Info', {
            'fields': ('id', 'session_id', 'language')
        }),
        ('Statistics', {
            'fields': ('message_count', 'duration')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_active'),
            'classes': ('collapse',)
        }),
    )
    
    def session_id_short(self, obj):
        """Display shortened session ID."""
        return f"...{obj.session_id[-12:]}"
    session_id_short.short_description = 'Session ID'
    
    def message_count(self, obj):
        """Display the number of messages in conversation."""
        return obj.messages.count()
    message_count.short_description = 'Messages'
    
    def duration(self, obj):
        """Display conversation duration."""
        if obj.created_at and obj.last_active:
            delta = obj.last_active - obj.created_at
            hours = delta.total_seconds() / 3600
            if hours < 1:
                minutes = delta.total_seconds() / 60
                return f"{int(minutes)} minutes"
            elif hours < 24:
                return f"{hours:.1f} hours"
            else:
                days = hours / 24
                return f"{days:.1f} days"
        return "N/A"
    duration.short_description = 'Duration'
    
    def has_add_permission(self, request):
        """Prevent manual creation of conversations via admin."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Allow deletion only for superusers to preserve data."""
        return request.user.is_superuser


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin interface for Message model."""
    
    list_display = ('id_short', 'conversation_session', 'sender_type', 'content_preview', 'timestamp')
    list_filter = ('is_user', 'timestamp', 'conversation__language')
    search_fields = ('content', 'conversation__session_id')
    readonly_fields = ('id', 'conversation', 'content', 'is_user', 'timestamp')
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Message Info', {
            'fields': ('id', 'conversation', 'content', 'is_user')
        }),
        ('Metadata', {
            'fields': ('timestamp',),
            'classes': ('collapse',)
        }),
    )
    
    def id_short(self, obj):
        """Display shortened ID."""
        return str(obj.id)[:8]
    id_short.short_description = 'ID'
    
    def conversation_session(self, obj):
        """Display conversation session ID."""
        return f"...{obj.conversation.session_id[-12:]}"
    conversation_session.short_description = 'Session'
    
    def sender_type(self, obj):
        """Display message sender type."""
        return '👤 User' if obj.is_user else '🤖 AI'
    sender_type.short_description = 'Sender'
    
    def content_preview(self, obj):
        """Display preview of message content."""
        preview = obj.content[:60]
        if len(obj.content) > 60:
            preview += '...'
        return preview
    content_preview.short_description = 'Content'
    
    def has_add_permission(self, request):
        """Prevent manual creation of messages via admin."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Prevent editing of messages to preserve data integrity."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Allow deletion only for superusers to preserve data."""
        return request.user.is_superuser


@admin.register(HumanHandoffRequest)
class HumanHandoffRequestAdmin(admin.ModelAdmin):
    """Admin interface for HumanHandoffRequest model."""
    
    list_display = ('ticket_number', 'name', 'phone', 'status', 'created_at', 'session_id')
    list_filter = ('status', 'created_at', 'conversation__language')
    search_fields = ('name', 'phone', 'problem_summary', 'conversation__session_id')
    readonly_fields = ('id', 'conversation', 'created_at')
    
    fieldsets = (
        ('Customer Info', {
            'fields': ('id', 'name', 'phone')
        }),
        ('Request Details', {
            'fields': ('conversation', 'problem_summary', 'status')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_contacted', 'mark_as_resolved']
    
    def ticket_number(self, obj):
        """Display formatted ticket number."""
        return str(obj.id)[:8].upper()
    ticket_number.short_description = 'Ticket #'
    
    def session_id(self, obj):
        """Display associated session ID."""
        return obj.conversation.session_id
    session_id.short_description = 'Session'
    
    def mark_as_contacted(self, request, queryset):
        """Bulk action to mark requests as contacted."""
        updated = queryset.update(status='contacted')
        self.message_user(request, f"{updated} request(s) marked as contacted.")
    mark_as_contacted.short_description = "Mark selected as Contacted"
    
    def mark_as_resolved(self, request, queryset):
        """Bulk action to mark requests as resolved."""
        updated = queryset.update(status='resolved')
        self.message_user(request, f"{updated} request(s) marked as resolved.")
    mark_as_resolved.short_description = "Mark selected as Resolved"
    
    def has_add_permission(self, request):
        """Prevent manual creation via admin (use API instead)."""
        return False
