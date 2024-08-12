from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from .serializers import userSerializer
from rest_framework import status
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ObjectDoesNotExist

@api_view(['GET'])
@permission_classes([AllowAny])
def getRoutes(request):
    routes = [

        {'POST': 'chat/'},
        {'GET': 'chat/assistant/'},
        {'POST': 'chat/assistant/'},
        {'GET': 'chat/assistant/<int:id>'},
        {'PUT': 'chat/assistant/<int:id>'},
        {'DELETE': 'chat/assistant/<int:id>'},

        {'GET': 'chat_assistant_documents/'},
        {'POST': 'chat_assistant_documents/'},
        {'GET': 'chat_assistant_documents/<int:id>'},
        {'PUT': 'chat_assistant_documents/<int:id>'},
        {'DELETE': 'chat_assistant_documents/<int:id>'},


        {'POST': 'chat/evaluate_answer/<int:id_chat_history>/<int:useful>'},
        {'POST': 'chat_my_docs/<int:id>'},
        {'POST': 'chat_with_assistant/<int:id>'},

        {'GET': 'documents/'},
        {'POST': 'documents/'},
        {'GET': 'documents/<int:id>'},
        {'PUT': 'documents/<int:id>'},
        {'DELETE': 'documents/<int:id>'},

        {'GET': 'document_type/'},
        {'POST': 'document_type/'},
        {'GET': 'document_type/<int:id>'},
        {'PUT': 'document_type/<int:id>'},
        {'DELETE': 'document_type/<int:id>'},

        {'GET': 'document_category/'},
        {'POST': 'document_category/'},
        {'GET': 'document_category/<int:id>'},
        {'PUT': 'document_category/<int:id>'},
        {'DELETE': 'document_category/<int:id>'},

        {'GET': 'document_department/'},
        {'POST': 'document_department/'},
        {'GET': 'document_department/<int:id>'},
        {'PUT': 'document_department/<int:id>'},
        {'DELETE': 'document_department/<int:id>'},

        {'POST': 'users/token'},
        {'POST': 'users/token/refresh'},
    ]
    return Response(routes)

@api_view(['POST'])
@permission_classes([AllowAny])  # Cambia a IsAuthenticated si es necesario
def LoginUser(request):

    username = request.data['username']
    password = request.data['password']
    user = None

    try:
        user = User.objects.get(email=username)
    except ObjectDoesNotExist:
        try:
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            return Response('User or password invalid', status=status.HTTP_404_NOT_FOUND)

    if not user or not user.check_password(password):
        return Response('User or password invalid', status=status.HTTP_400_BAD_REQUEST)

    refresh = RefreshToken.for_user(user)
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user': request.data['username']
    }, status=status.HTTP_200_OK)

@api_view(['POST','GET'])
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
@permission_classes([AllowAny])  # Cambia a IsAuthenticated si es necesario
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

