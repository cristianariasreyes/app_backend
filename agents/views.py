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
    #validamos que tenemos los datos necesarios: mail_subject, mail_body, category_path
    if 'mail_subject' not in request.data or 'mail_body' not in request.data or 'category_path' not in request.data:
        return Response({'message': 'Faltan datos necesarios'}, status=status.HTTP_400_BAD_REQUEST)
    
    #Recorremos la lista de categorias y las pasamos a un string
    category_path = ""
    for category_path in request.data['category_path']:
        #el primer registro copia tal cual el path, del segundo en adelante le añade un signo ## delante y concatena
        if category_path == request.data['category_path'][0]:
            categories = category_path
        else:
            categories = categories + "##" + category_path
    
    system_role = """Eres un agente de mesa de ayuda que lee la peticion del usuario y la 
    clasifica en una de la lista de categorias. Las categorias estan separadas por el separador
    ##. Dentro de las categorias candidatas, debes elegir siempre la categoria que tenga 
    # mas elementos separados por ##.
    La descripcion llega por correo y muchas veces se adjunta la firma del usuario. Debes ignorar
    aquel texto que parezca ser parte de la firma del correo.
    La respuesta a la consulta del usuario debe ser literalmente el nombre de la categoria que
    describa mejor la peticion del usuario dentro de las categorias disponibles tal 
    y cual estan escritas y nada mas. 
    Jamas entregues una respuesta que no este en la lista de categorias."""
    
    prompt = f"""
    Mail del usuario: Asunto:{request.data['mail_subject']+' Cuerpo del mensaje: '+request.data['mail_body']}
    Categorias disponibles:
    {categories}
    """
                
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

