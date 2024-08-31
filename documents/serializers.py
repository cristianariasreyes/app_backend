from rest_framework import serializers
from chat.models import Chat_session, Chat_history, Chat_session_end_reason
from documents.models import (
    Document_type,
    Document_department,
    Document_category,
    Document,
)


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = "__all__"


class Document_typeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document_type
        fields = "__all__"


class Document_departmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document_department
        fields = "__all__"


class Document_categorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Document_category
        fields = "__all__"
