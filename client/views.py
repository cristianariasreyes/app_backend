from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from documents.models import Document_type, Document_department, Document_category, Document
from rest_framework import status
from django.db import transaction

# Create your views here.
@api_view(['POST'])
@permission_classes([AllowAny]) 
def GetClients(request):
    clients = Document.objects.all()
    serializer = DocumentSerializer(clients, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny]) 
def UpsertClient(request):
    with transaction.atomic():
        serializer = DocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
