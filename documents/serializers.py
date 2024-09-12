from rest_framework import serializers
from documents.models import (
    Document_type,
    Document_department,
    Document_category,
    Document,
)


class DocumentSerializer(serializers.ModelSerializer):
    
    document_category_name = serializers.CharField(
        source="id_document_category.description", read_only=True
    )
    document_department_name = serializers.CharField(
        source="id_document_department.description", read_only=True
    )
    document_type_name = serializers.CharField(
        source="id_document_type.description", read_only=True
    )
    owner_by_name = serializers.CharField(source="owner.email", read_only=True)

    # Campo para subir el archivo
    file = serializers.FileField(write_only=True, required=False)  # No es obligatorio

    class Meta:
        model = Document
        fields = [
            'subject',
            'id_document_department',
            'id_document_category',
            'id_document_type',
            'owner',
            'file',  # Si necesitas el archivo en la solicitud
            'document_category_name',  # Campo de solo lectura
            'document_department_name',  # Campo de solo lectura
            'document_type_name',  # Campo de solo lectura
            'owner_by_name',  # Campo de solo lectura
            ]
    
    def validate(self, data):
        # Validaciones personalizadas, si las necesitas
        return data



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
