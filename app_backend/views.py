from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import userSerializer
from rest_framework import status
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView

@api_view(['GET'])
@permission_classes([AllowAny])
def getRoutes(request):
    routes = [
        
        {'GET,POST': 'register/'},
        {'GET,POST': 'login/'},
        {'POST': 'logout/'},
        
        
        {'GET': 'chat/assistant/'},
        {'POST': 'chat/assistant/'},
        {'GET': 'chat/assistant/<int:id>'},
        {'PUT': 'chat/assistant/<int:id>'},
        {'DELETE': 'chat/assistant/<int:id>'},
        
        {'POST': 'chat/chat_my_docs/<int:id>'},
        {'POST': 'chat/chat_with_assistant/<int:id>'},        
        
        {'GET': 'chat/chat_assistant_documents/'},
        {'POST': 'chat/chat_assistant_documents/'},
        {'GET': 'chat/chat_assistant_documents/<int:id>'},
        {'PUT': 'chat/chat_assistant_documents/<int:id>'},
        {'DELETE': 'chat/chat_assistant_documents/<int:id>'},

        {'POST': 'chat/evaluate_answer/<int:id_chat_history>/<int:useful>'},

        
        {'GET': 'documents/'},
        {'POST': 'documents/'},
        {'GET': 'documents/<int:id>'},
        {'PUT': 'documents/<int:id>'},
        {'DELETE': 'documents/<int:id>'},

        {'GET': 'documents/document_type/'},
        {'POST': 'documents/document_type/'},
        {'GET': 'documents/document_type/<int:id>'},
        {'PUT': 'documents/document_type/<int:id>'},
        {'DELETE': 'documents/document_type/<int:id>'},
        
        {'GET': 'documents/document_category/'},
        {'POST': 'documents/document_category/'},
        {'GET': 'documents/document_category/<int:id>'},
        {'PUT': 'documents/document_category/<int:id>'},
        {'DELETE': 'documents/document_category/<int:id>'},
        
        {'GET': 'documents/document_department/'},
        {'POST': 'documents/document_department/'},
        {'GET': 'documents/document_department/<int:id>'},
        {'PUT': 'documents/document_department/<int:id>'},
        {'DELETE': 'documents/document_department/<int:id>'},
        
        {'POST': 'users/token'},	
        {'POST': 'users/token/refresh'},

        {'GET': 'service_desk/get_categories/'},	
        {'GET': 'service_desk/get_sentiment/'},	
        {'GET': 'service_desk/mail_response/'},	
        

    ]
        
    return Response(routes)



@api_view(['GET','POST'])
@permission_classes([AllowAny])  # Cambia a IsAuthenticated si es necesario
def LoginUser(request):
    if request.method == 'POST':
        user = get_object_or_404(User, username=request.data['username'])
    
        if not user.check_password(request.data['password']):
            return Response('Invalid password', status=status.HTTP_400_BAD_REQUEST)
        else:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': request.data['username']
            }, status=status.HTTP_200_OK)
    else:
        return Response('Welcome!')
        
@api_view(['GET','POST'])
@permission_classes([AllowAny])  # Cambia a IsAuthenticated si es necesario
def RegisterUser(request):
    LoginObj = userSerializer(data=request.data)
    if LoginObj.is_valid():
        new_user = User.objects.create_user(
            username=LoginObj.validated_data['username'], 
            email=LoginObj.validated_data['email'])
        #Actualizamos la password
        new_user.set_password(LoginObj.validated_data['password'])
        new_user.save()

        #Generamos el token de autorizacion        
        refresh = RefreshToken.for_user(new_user) 
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': LoginObj.data
        }, status=status.HTTP_200_OK)
        
    else:
        return Response(LoginObj.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Cambia a IsAuthenticated si es necesario
def LogOutUser(request):
    try:
        # Obtenemos el token de refresco del cuerpo de la solicitud
        refresh_token = request.data["refresh_token"]
        token = RefreshToken(refresh_token)
        # Agrega el token a la lista negra
        token.blacklist()
        return Response('User logged out', status=status.HTTP_200_OK)
    except Exception as e:
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def ProfileUser(request):
    return Response('Login page')

