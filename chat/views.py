import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .services.chat_with_documents import document_chat
from .services.chat_ast_coach import assistant_coach
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from documents.models import (
    Document_type,
    Document_department,
    Document_category,
    Document,
)
from chat.models import Chat_assistant, Chat_assistant_documents
from chat.serializers import (
    Chat_assistantSerializer,
    Chat_assistant_documentsSerializer,
)
from chat.services.chat_with_documents import document_chat
from rest_framework import status
from rest_framework import permissions


@api_view(["POST"])
@permission_classes([AllowAny])  # Cambia a IsAuthenticated si es necesario
def chat_with_an_assistant(request, id):

    print("chat_with_an_assistant")
    data = request.data
    pregunta = data.get("message")
    print("pregunta: " + pregunta)
    try:
        new_chat = document_chat()
        respuesta = new_chat.assistant_chat(id, pregunta)
    except Exception as e:
        respuesta = {"result": str(e)}
        return Response({"respuesta": respuesta}, status=status.HTTP_400_BAD_REQUEST)
    return Response(
        {
            "respuesta": respuesta["content"],
            "id_chat_history": respuesta["id_chat_history"],
        }
    )


@api_view(["POST"])
@permission_classes([AllowAny])  # Cambia a IsAuthenticated si es necesario
def chat_my_docs(request, id):
    data = request.data
    pregunta = data.get("message")
    new_chat = document_chat()
    respuesta = new_chat.ChatSingleDoc(id, pregunta)
    return Response({"respuesta": respuesta})


@api_view(["POST"])
@permission_classes([AllowAny])  # Cambia a IsAuthenticated si es necesario
def chat_with_documents(request):
    if request.method == "POST":
        data = request.data
        pregunta = data.get("message")
        temperature = data.get("temperature")
        llm_model = data.get("llm_model")
        chat_technique = data.get("chat_technique")
        asistant = ""
        conversation_hash = ""
        pdf_document = ""
        pdf_id_document = 0
        respuesta = ""

        print(f"Pregunta:{pregunta}")
        print(f"Temperatura:{temperature}")
        print(f"Modelo de lenguaje:{llm_model}")
        print(f"Tecnica de chat:{chat_technique}")
        print(f"Asistente:{asistant}")
        print(f"Hash de la conversacion:{conversation_hash}")

        try:
            if chat_technique == "Basic chat with memory":
                chat = document_chat(
                    pregunta,
                    temperature,
                    llm_model,
                    asistant,
                    pdf_id_document,
                    pdf_document,
                    conversation_hash,
                )
                respuesta = chat.basic_chat_with_memory()
                return Response(
                    {
                        "respuesta": respuesta["result"],
                        "id_chat_history": respuesta["id_chat_history"],
                    }
                )

            if chat_technique == "Basic chat":
                chat = document_chat(
                    pregunta,
                    temperature,
                    llm_model,
                    asistant,
                    pdf_id_document,
                    pdf_document,
                    conversation_hash,
                )
                respuesta = chat.basic_chat(0.7)
                return Response({"respuesta": respuesta})
            else:
                print("No es una opcion valida")
        except Exception as e:
            respuesta = {"result": str(e)}
        print(respuesta)
        return Response({"respuesta": respuesta})
    else:
        return Response("Puedes chatear", status=status.HTTP_200_OK)


@api_view(["GET", "POST"])
@permission_classes([AllowAny])  # Cambia a IsAuthenticated si es necesario
def Getchat_assistant(request):
    if request.method == "GET":

        search_query = str(request.GET.get("search", "") or "")
        page_number = int(request.GET.get("page", 1) or 1)
        items_per_page = int(request.GET.get("per_page", 6) or 6)

        assistants = Chat_assistant.objects.filter(
            Q(name__icontains=search_query) | Q(role__icontains=search_query)
        )

        paginator = Paginator(assistants, items_per_page)

        try:
            page = paginator.page(page_number)
        except PageNotAnInteger:
            page = paginator.page(1)
        except EmptyPage:
            page = paginator.page(paginator.num_pages)

        serializer = Chat_assistantSerializer(page.object_list, many=True)
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
        serializer = Chat_assistantSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([AllowAny])  # Cambia a IsAuthenticated si es necesario
def Getchat_assistant_detail(request, id):
    try:
        assistants = Chat_assistant.objects.get(id_chat_assistant=id)
    except Chat_assistant.DoesNotExist:
        return Response(
            {"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND
        )

    if request.method == "GET":
        serializer = Chat_assistantSerializer(assistants)
        return Response(serializer.data)

    if request.method == "PUT":
        serializer = Chat_assistantSerializer(assistants, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        assistants.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "POST"])
@permission_classes([AllowAny])  # Cambia a IsAuthenticated si es necesario
def Get_chat_assistant_document(request):
    try:
        if request.method == "GET":
            search_query = str(request.GET.get("search", "") or "")
            page_number = int(request.GET.get("page", 1))
            items_per_page = int(request.GET.get("per_page", 6))
            filters = str(request.GET.get("filters", "") or "")

            filter_list = json.loads(filters) if filters else []

            # Obteniendo el queryset
            assistants = Chat_assistant_documents.objects.filter(
                Q(id_document__document_name__icontains=search_query)
                | Q(id_document__resume__icontains=search_query)
            )

            # Aplicar los filtros dinámicamente
            # todo ESTO HAY QUE REPLICARLO, LO MEJOR ES USAR UN UTIL
            for filter_item in filter_list:
                field = filter_item.get("id")
                value = filter_item.get("value")

                if field and value:
                    # Crear dinámicamente el filtro
                    filter_kwargs = {f"{field}": value}
                    assistants = assistants.filter(**filter_kwargs)

            paginator = Paginator(assistants, items_per_page)

            try:
                page = paginator.page(page_number)
            except PageNotAnInteger:
                page = paginator.page(1)
            except EmptyPage:
                page = paginator.page(paginator.num_pages)

            serializer = Chat_assistant_documentsSerializer(page.object_list, many=True)
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
            if not request.user.id:
                print("No hay usuario")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Hacemos una copia de los datos y agregamos el campo created_by
            data = request.data.copy()
            data["created_by"] = request.user.id

            # Pasamos la copia modificada al serializador
            serializer = Chat_assistant_documentsSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"errorcito: {e}")
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([AllowAny])  # Cambia a IsAuthenticated si es necesario
def Get_chat_assistant_document_detail(request, id):
    try:
        assistant_documents = Chat_assistant_documents.objects.get(
            id_chat_assistant_document=id
        )
    except Chat_assistant.DoesNotExist:
        return Response(
            {"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND
        )

    if request.method == "GET":
        serializer = Chat_assistant_documentsSerializer(assistant_documents)
        return Response(serializer.data)

    if request.method == "PUT":
        serializer = Chat_assistant_documentsSerializer(
            assistant_documents, data=request.data
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        assistant_documents.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([AllowAny])  # Cambia a IsAuthenticated si es necesario
def evaluate_answer(request):
    if request.method == "POST":
        useful = request.POST.get("useful")
        id_chat_history = request.POST.get("id_chat_history")

        # Convertimos lo que venga el useful (0 o 1, true o false) a booleano
        useful = useful.lower() in ["true", "1"]

        print(f"Valoración que da el usuario: {useful}")
        print(f"ID del chat history: {id_chat_history}")
        try:
            respuesta = document_chat.evaluate_answer(useful, id_chat_history)
            return JsonResponse({"respuesta": respuesta})
        except Exception as e:
            return JsonResponse({"respuesta": str(e)})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"})


class NotFoundView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        return Response({"detail": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, *args, **kwargs):
        return Response({"detail": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, *args, **kwargs):
        return Response({"detail": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, *args, **kwargs):
        return Response({"detail": "Not Found"}, status=status.HTTP_404_NOT_FOUND)
