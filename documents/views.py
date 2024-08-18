from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .serializers import DocumentSerializer, Document_typeSerializer, Document_departmentSerializer, Document_categorySerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from documents.models import Document_type, Document_department, Document_category, Document
from rest_framework import status


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])  # Cambia a IsAuthenticated si es necesario
def GetDocument(request):
    if request.method == 'GET':
        documents = Document.objects.all()
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = DocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])  # Cambia a IsAuthenticated si es necesario
def GetDocument_detail(request, id):
    try:
        document = Document.objects.get(id=id)
    except Document.DoesNotExist:
        return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = DocumentSerializer(document)
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = DocumentSerializer(document, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        document.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])  # Cambia a IsAuthenticated si es necesario
def document_type(request):
    if request.method == 'GET':
        document_types = Document_type.objects.all()
        serializer = Document_typeSerializer(document_types, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    if request.method == 'POST':
        serializer = Document_typeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])  # Cambia a IsAuthenticated si es necesario
def document_type_detail(request, id):
    try:
        document_types = Document_type.objects.get(id_document_type=id)
    except Document_type.DoesNotExist:
        return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = Document_typeSerializer(document_types)
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = Document_typeSerializer(document_types, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        document_types.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])  # Cambia a IsAuthenticated si es necesario
def document_category(request):
    if request.method == 'GET':
        document_categories = Document_category.objects.all()
        serializer = Document_categorySerializer(document_categories, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = Document_categorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])  # Cambia a IsAuthenticated si es necesario
def document_category_detail(request, id):
    try:
        document_categories = Document_category.objects.get(id_document_category=id)
    except Document_category.DoesNotExist:
        return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = Document_categorySerializer(document_categories)
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = Document_categorySerializer(document_categories, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        document_categories.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])  # Cambia a IsAuthenticated si es necesario
def document_department(request):
    if request.method == 'GET':
        documents = Document_department.objects.all()
        serializer = Document_departmentSerializer(documents, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = Document_departmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])  # Cambia a IsAuthenticated si es necesario
def document_department_detail(request, id):
    try:
        document = Document_department.objects.get(id_document_department=id)
    except Document_department.DoesNotExist:
        return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = Document_departmentSerializer(document)
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = Document_departmentSerializer(document, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        document.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
