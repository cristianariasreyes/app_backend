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
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
import boto3
from botocore.exceptions import NoCredentialsError
from django.conf import settings


@api_view(["GET", "POST"])
@permission_classes([AllowAny])  # Cambia a IsAuthenticated si es necesario
def GetDocument(request):
    if request.method == "GET":
        documents = Document.objects.all()
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data)

    if request.method == "POST":
        file = request.FILES["file"]

        if not file:
            return Response(
                {"error": "Bad request"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

        try:
            s3_client.upload_fileobj(file, settings.AWS_STORAGE_BUCKET_NAME, file.name)
            s3_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
            s3_url += f"/{settings.ENVIRONMENT_CUSTOM}/{file.name}"

            # Actualizamos los datos antes de guardarlos
            data = request.data.copy()
            data["s3_document_path"] = s3_url
            serializer = DocumentSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except NoCredentialsError:
            return Response(
                {"error": "Credentials not available"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([AllowAny])  # Cambia a IsAuthenticated si es necesario
def GetDocument_detail(request, id):
    try:
        document = Document.objects.get(id=id)
    except Document.DoesNotExist:
        return Response(
            {"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND
        )

    if request.method == "GET":
        serializer = DocumentSerializer(document)
        return Response(serializer.data)

    if request.method == "PUT":
        serializer = DocumentSerializer(document, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        document.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "POST"])
@permission_classes([AllowAny])  # Cambia a IsAuthenticated si es necesario
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

        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == "POST":
        serializer = Document_typeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([AllowAny])  # Cambia a IsAuthenticated si es necesario
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
@permission_classes([AllowAny])  # Cambia a IsAuthenticated si es necesario
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
@permission_classes([AllowAny])  # Cambia a IsAuthenticated si es necesario
def document_category_detail(request, id):
    try:
        document_categories = Document_category.objects.get(id_document_category=id)
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
@permission_classes([AllowAny])  # Cambia a IsAuthenticated si es necesario
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
@permission_classes([AllowAny])  # Cambia a IsAuthenticated si es necesario
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
