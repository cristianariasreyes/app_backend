from django.contrib import admin
from .models import (
    Chat_session_end_reason, Chat_session, Chat_history, Chat_assistant, Chat_assistant_documents
)

# Chat Assistant Models
class ChatAssistantAdmin(admin.ModelAdmin):
    list_display = ('id_chat_assistant', 'name', 'llm_model', 'temperature', 'created_by', 'company_id')
    search_fields = ('name', 'llm_model')
    list_filter = ('company_id',)

class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('id_chat_session', 'id_user', 'started', 'ended', 'id_end_reason')
    search_fields = ('id_user__username',)
    list_filter = ('started', 'id_end_reason')

class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ('id_chat_history', 'id_user', 'id_chat_session', 'creation_date', 'useful')
    search_fields = ('id_user__username', 'human_entry', 'ia_entry')
    list_filter = ('creation_date', 'useful')

class ChatAssistantDocumentsAdmin(admin.ModelAdmin):
    list_display = ('id_chat_assistant_document', 'id_chat_assistant', 'id_document', 'creation_date', 'created_by')
    search_fields = ('id_chat_assistant__name', 'id_document__document_name')
    list_filter = ('creation_date',)

# Register the models in the Django Admin
admin.site.register(Chat_session_end_reason)
admin.site.register(Chat_session, ChatSessionAdmin)
admin.site.register(Chat_history, ChatHistoryAdmin)
admin.site.register(Chat_assistant, ChatAssistantAdmin)
admin.site.register(Chat_assistant_documents, ChatAssistantDocumentsAdmin)
