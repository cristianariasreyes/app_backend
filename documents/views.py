from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .serializers import (
    DocumentSerializer,
    Document_typeSerializer,
    Document_departmentSerializer,
    Document_categorySerializer,
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from documents.models import (
    Document_type,
    Document_department,
    Document_category,
    Document,
)
from rest_framework import status
from .document_services import document
from django.db import transaction 
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
import boto3
from botocore.exceptions import NoCredentialsError
from django.conf import settings




@api_view(["GET", "POST"])
@permission_classes([AllowAny])
# This method handles requests for new documents and also for searching lists of documents
# Also handle uploading a new document
def AddListDocument(request):
    if request.method == "GET":
        search_query = str(request.GET.get("search", ""))
        page_number = int(request.GET.get("page", 1))
        items_per_page = int(request.GET.get("per_page", 12))

        documents = Document.objects.filter(
            Q(document_name__icontains=search_query)
            | Q(subject__icontains=search_query)
            | Q(resume__icontains=search_query)
        )

        paginator = Paginator(documents, items_per_page)

        try:
            page = paginator.page(page_number)
        except PageNotAnInteger:
            page = paginator.page(1)
        except EmptyPage:
            page = paginator.page(paginator.num_pages)

        serializer = DocumentSerializer(page.object_list, many=True)
        return Response(
            {
                "current_page": page.number,
                "total_pages": paginator.num_pages,
                "items_per_page": items_per_page,
                "items_total": paginator.count,
                "data": serializer.data,
            }
        )

    if request.method == "POST":
        # Validate if a file was sent
        if "file" not in request.FILES:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
        try:
           
            # Create an instance of the document service
            DocObject = document(request)
            SavedDocument = DocObject.SaveDocument()
            # Create and validate the serializer
            serializer = DocumentSerializer(data=SavedDocument)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"error": f"Error processing document: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([AllowAny])  # Change to IsAuthenticated if necessary
def DocumentHandle(request, id):
    # Validate if the document exists
    try:
        document = Document.objects.get(id=id)
    except Document.DoesNotExist:
        return Response(
            {"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND
        )
    # If it exists, we can handle the request whether it is GET, PUT, or DELETE
    if request.method == "GET":
        serializer = DocumentSerializer(document)
        return Response(serializer.data)

    if request.method == "PUT":
        try:
            data = request.data.copy()

            if not data.get('document_path'):
                data['document_path'] = 'null'
            if not data.get('id_vdb'):
                data['id_vdb'] = 0

            serializer = DocumentSerializer(document, data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if request.method == 'DELETE':
        try:
            document.delete()
        except Exception as e:
            return Response({'error': f'Error deleting document in database: {e}'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "POST"])
@permission_classes([AllowAny])  # Change to IsAuthenticated if necessary
def document_type(request):
    if request.method == "GET":
        search_query = str(request.GET.get("search", "") or "")
        page_number = int(request.GET.get("page", 1) or 1)
        items_per_page = int(request.GET.get("per_page", 12) or 12)

        assistants = Document_type.objects.filter(
            Q(description__icontains=search_query)
        )

        paginator = Paginator(assistants, items_per_page)

        try:
            page = paginator.page(page_number)
        except PageNotAnInteger:
            page = paginator.page(1)
        except EmptyPage:
            page = paginator.page(paginator.num_pages)

        serializer = Document_typeSerializer(page.object_list, many=True)
        return Response(
            {
                "current_page": page.number,
                "total_pages": paginator.num_pages,
                "items_per_page": items_per_page,
                "items_total": paginator.count,
                "data": serializer.data,
            }
        )

    if request.method == "POST":
        serializer = Document_typeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([AllowAny])  # Change to IsAuthenticated if necessary
def document_type_detail(request, id):
    try:
        document_types = Document_type.objects.get(id_document_type=id)
    except Document_type.DoesNotExist:
        return Response(
            {"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND
        )

    if request.method == "GET":
        serializer = Document_typeSerializer(document_types)
        return Response(serializer.data)

    if request.method == "PUT":
        serializer = Document_typeSerializer(document_types, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        document_types.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "POST"])
@permission_classes([AllowAny])  # Change to IsAuthenticated if necessary
def document_category(request):
    if request.method == "GET":
        search_query = str(request.GET.get("search", "") or "")
        page_number = int(request.GET.get("page", 1) or 1)
        items_per_page = int(request.GET.get("per_page", 12) or 12)

        assistants = Document_category.objects.filter(
            Q(description__icontains=search_query)
        )

        paginator = Paginator(assistants, items_per_page)

        try:
            page = paginator.page(page_number)
        except PageNotAnInteger:
            page = paginator.page(1)
        except EmptyPage:
            page = paginator.page(paginator.num_pages)

        serializer = Document_categorySerializer(page.object_list, many=True)
        return Response(
            {
                "current_page": page.number,
                "total_pages": paginator.num_pages,
                "items_per_page": items_per_page,
                "items_total": paginator.count,
                "data": serializer.data,
            }
        )

    if request.method == "POST":
        serializer = Document_categorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([AllowAny])  # Change to IsAuthenticated if necessary
def document_category_detail(request, id):
    try:
        document_categories = Document_category.objects.get(id_document_type_id=id)
    except Document_category.DoesNotExist:
        return Response(
            {"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND
        )

    if request.method == "GET":
        serializer = Document_categorySerializer(document_categories)
        return Response(serializer.data)

    if request.method == "PUT":
        serializer = Document_categorySerializer(document_categories, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        document_categories.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "POST"])
@permission_classes([AllowAny])  # Change to IsAuthenticated if necessary
def document_department(request):
    if request.method == "GET":
        search_query = str(request.GET.get("search", "") or "")
        page_number = int(request.GET.get("page", 1) or 1)
        items_per_page = int(request.GET.get("per_page", 12) or 12)

        document_departamens = Document_department.objects.filter(
            Q(description__icontains=search_query)
        )

        paginator = Paginator(document_departamens, items_per_page)

        try:
            page = paginator.page(page_number)
        except PageNotAnInteger:
            page = paginator.page(1)
        except EmptyPage:
            page = paginator.page(paginator.num_pages)

        serializer = Document_departmentSerializer(page.object_list, many=True)
        return Response(
            {
                "current_page": page.number,
                "total_pages": paginator.num_pages,
                "items_per_page": items_per_page,
                "items_total": paginator.count,
                "data": serializer.data,
            }
        )

    if request.method == "POST":
        serializer = Document_departmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([AllowAny])  # Change to IsAuthenticated if necessary
def document_department_detail(request, id):
    try:
        document = Document_department.objects.get(id_document_department=id)
    except Document_department.DoesNotExist:
        return Response(
            {"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND
        )

    if request.method == "GET":
        serializer = Document_departmentSerializer(document)
        return Response(serializer.data)

    if request.method == "PUT":
        serializer = Document_departmentSerializer(document, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        document.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
