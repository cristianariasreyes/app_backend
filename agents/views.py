from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from documents.models import Document_type, Document_department, Document_category, Document
from chat.models import Chat_assistant,Chat_assistant_documents
from chat.serializers import Chat_assistantSerializer, Chat_assistant_documentsSerializer
from chat.services.chat_with_documents import document_chat
from rest_framework import status


@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def ServiceDesk(request):
    return Response({'message': 'Service Tonic'})

@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def ServiceDesk_GetCategories(request):
    return Response({'message': 'Service Tonic'})

@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def ServiceDesk_MailResponse(request):
    return Response({'message': 'Service Tonic'})

@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def ServiceDesk_GetSentiment(request):
    return Response({'message': 'Service Tonic'})

@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def getRoutes(request):
    return Response({'message': 'Service Tonic'})

