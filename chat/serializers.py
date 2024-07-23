from rest_framework import serializers
from chat.models import Chat_session, Chat_history, Chat_session_end_reason,Chat_assistant,Chat_assistant_documents

class ChatHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat_history
        fields = '__all__'

class Chat_session_end_reasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat_session_end_reason
        fields = '__all__'

class Chat_sessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat_session
        fields = '__all__'

class Chat_assistantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat_assistant
        fields = '__all__'

class Chat_assistant_documentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat_assistant_documents
        fields = '__all__'