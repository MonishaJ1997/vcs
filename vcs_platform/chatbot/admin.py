from django.contrib import admin
from .models import ChatMessage

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'message_preview', 'response_preview', 'escalated', 'created_at')
    list_filter = ('escalated', 'created_at')
    search_fields = ('user__username', 'message', 'response')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

    # Shorten message and response for list display
    def message_preview(self, obj):
        return (obj.message[:50] + '...') if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message'

    def response_preview(self, obj):
        return (obj.response[:50] + '...') if len(obj.response) > 50 else obj.response
    response_preview.short_description = 'Response'
