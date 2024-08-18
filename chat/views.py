from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .services.chat_with_documents import document_chat
from .services.chat_ast_coach import assistant_coach
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from documents.models import Document_type, Document_department, Document_category, Document
from chat.models import Chat_assistant,Chat_assistant_documents
from chat.serializers import Chat_assistantSerializer, Chat_assistant_documentsSerializer
from chat.services.chat_with_documents import document_chat
from rest_framework import status

@api_view(['POST'])
@permission_classes([AllowAny])  # Cambia a IsAuthenticated si es necesario
def chat_with_an_assistant(request,id):

    print('chat_with_an_assistant')
    data = request.data
    pregunta = data.get('message')

    print('pregunta: ' + pregunta)

    new_chat = document_chat()
    respuesta = new_chat.assistant_chat(id,pregunta)
    return Response({'respuesta': respuesta})

@api_view(['POST'])
@permission_classes([AllowAny])  # Cambia a IsAuthenticated si es necesario
def chat_my_docs(request,id):
    data=request.data
    pregunta = data.get('message')
    new_chat = document_chat()
    respuesta = new_chat.ChatSingleDoc(id,pregunta)
    return Response({'respuesta': respuesta})


@api_view(['POST'])
@permission_classes([AllowAny])  # Cambia a IsAuthenticated si es necesario
def chat_with_documents(request):
    if request.method == 'POST':
        data = request.data
        pregunta = data.get('message')
        temperature = data.get('temperature')
        llm_model = data.get('llm_model')
        chat_technique = data.get('chat_technique')
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
                chat = document_chat(pregunta, temperature, llm_model, asistant, pdf_id_document, pdf_document, conversation_hash)
                respuesta = chat.basic_chat_with_memory()
                return Response({'respuesta': respuesta['result'], 'id_chat_history': respuesta['id_chat_history']})

            if chat_technique == "Basic chat":
                chat = document_chat(pregunta, temperature, llm_model, asistant, pdf_id_document, pdf_document, conversation_hash)
                respuesta = chat.basic_chat(0.7)
                return Response({'respuesta': respuesta})
            else:
                print("No es una opcion valida")
        except Exception as e:
            respuesta = {'result': str(e)}
        print(respuesta)
        return Response({'respuesta': respuesta})
    else:
        return Response('Puedes chatear', status=status.HTTP_200_OK)


@api_view(['GET','POST'])
@permission_classes([AllowAny])  # Cambia a IsAuthenticated si es necesario
def Getchat_assistant(request):
    if request.method == 'GET':

        search_query = str(request.GET.get('search', '') or '')
        page_number = int(request.GET.get('page', 1) or 1)
        items_per_page = int(request.GET.get('per_page', 6) or 6)

        assistants = Chat_assistant.objects.filter(
            Q(name__icontains=search_query)
            |
            Q(role__icontains=search_query)
        )

        paginator = Paginator(assistants, items_per_page)

        try:
            page = paginator.page(page_number)
        except PageNotAnInteger:
            page = paginator.page(1)
        except EmptyPage:
            page = paginator.page(paginator.num_pages)

        serializer = Chat_assistantSerializer(page.object_list, many=True)
        return Response({
            'current_page': page.number,
            'total_pages': paginator.num_pages,
            'items_per_page': items_per_page,
            'items_total': paginator.count,
            'data': serializer.data
        })

    if request.method == 'POST':
        serializer = Chat_assistantSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])  # Cambia a IsAuthenticated si es necesario
def Getchat_assistant_detail(request, id):
    try:
        assistants = Chat_assistant.objects.get(id_chat_assistant=id)
    except Chat_assistant.DoesNotExist:
        return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = Chat_assistantSerializer(assistants)
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = Chat_assistantSerializer(assistants, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        assistants.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET','POST'])
@permission_classes([AllowAny])  # Cambia a IsAuthenticated si es necesario
def Get_chat_assistant_document(request):
    try:
        if request.method == 'GET':
            search_query = str(request.GET.get('search', '') or '')
            page_number = int(request.GET.get('page', 1))
            items_per_page = int(request.GET.get('per_page', 6))

            # Obteniendo el queryset
            assistants = Chat_assistant_documents.objects.filter(
                Q(id_document__name__icontains=search_query) |
                Q(id_document__resume__icontains=search_query)
            )

            paginator = Paginator(assistants, items_per_page)

            try:
                page = paginator.page(page_number)
            except PageNotAnInteger:
                page = paginator.page(1)
            except EmptyPage:
                page = paginator.page(paginator.num_pages)

            serializer = Chat_assistant_documentsSerializer(page.object_list, many=True)
            return Response({
                'current_page': page.number,
                'total_pages': paginator.num_pages,
                'items_per_page': items_per_page,
                'items_total': paginator.count,
                'data': serializer.data
            })

        if request.method == 'POST':
            serializer = Chat_assistant_documentsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])  # Cambia a IsAuthenticated si es necesario
def Get_chat_assistant_document_detail(request, id):
    try:
        assistant_documents = Chat_assistant_documents.objects.get(id_chat_assistant_document=id)
    except Chat_assistant.DoesNotExist:
        return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = Chat_assistant_documentsSerializer(assistant_documents)
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = Chat_assistant_documentsSerializer(assistant_documents, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        assistant_documents.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)




@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])  # Cambia a IsAuthenticated si es necesario
def evaluate_answer(request):
    if request.method == 'POST':
        useful = request.POST.get('useful')
        id_chat_history = request.POST.get('id_chat_history')
        print(f"Valoración que da el usuario: {useful}")
        print(f"ID del chat history: {id_chat_history}")
        try:
            respuesta = document_chat.evaluate_answer(useful, id_chat_history)
            return JsonResponse({'respuesta': respuesta})
        except Exception as e:
            return JsonResponse({'respuesta': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def handle_assistant_coach(request):
    if request.method == 'POST':
        data= request.POST
        id_ast_coach=data.get('id_ast_coach')
        id_ast_coach_chain = data.get('id_ast_coach_chain')
        user_answer = data.get('user_answer')
        id_ast_coach_question = data.get('id_ast_coach_question')

        print (f"el valor de id_ast_coach_chain es:{id_ast_coach_chain}")
        print (f"el valor de id_ast_coach es:{id_ast_coach}")
        print (f"el usuario ha respondido:{user_answer}")

        if id_ast_coach_chain =='0':
            id_ast_coach_chain = None
        goodbye = False
        coach = assistant_coach(id_ast_coach,id_ast_coach_chain,user_answer)

        if id_ast_coach_chain is None:
            print("Creando una nueva ronda de preguntas...")
            try:
                new_chain=coach.begin_coaching_chain()

                return JsonResponse({'result':True,
                                'id_ast_coach_chain':new_chain['id_ast_coach_chain'],
                                'current_question':new_chain['current_question'],
                                'welcome_message':new_chain['welcome_message'],
                                'avatar':new_chain['avatar'],
                                'id_ast_coach_question': new_chain['id_ast_coach_question'],
                                'goodbye':False,
                                'error_message':''})
            except Exception as e:
                return JsonResponse({'result':False,'error_message': str(e)})
        else:
            try:
                print("Evaluando la respuesta del alumno...")
                coach_evaluation = coach.get_comment_and_evaluation(id_ast_coach_question,user_answer)
                coach_comment = coach_evaluation['answer_evaluation']
                is_correct = coach_evaluation['is_correct']
                avatar = coach_evaluation['avatar']
                str_next_question=""
                if is_correct in [0,1]:
                    print("entrando al bloque de is_correct in [0,1]")
                    coach.save_evaluation(id_ast_coach_question,is_correct)
                    next_question = coach.get_next_question(id_ast_coach_chain)
                    if next_question is not None:
                        str_next_question = next_question['question']
                        goodbye = next_question['goodbye']
                        if next_question['goodbye'] is not None:
                            print("Agregando la siguiente pregunta al asistente...")
                            id_ast_coach_question = coach._add_new_question(id_ast_coach_chain,
                                                                            next_question['id_ast_coach_qa'],
                                                                            str_next_question)
                            print("Termine todas las instrucciones del bloque Ok")
                    else:
                        print("entrando al bloque de next_question=None")
                else:
                    print("entrando al bloque de is_correct not in [0,1] lo que quiere decir que es 2")
                    str_next_question = coach_comment

                diccionario_respuestas = {'result':True,
                                            'coach_comment':coach_comment,
                                            'is_correct':is_correct,
                                            'avatar':avatar,
                                            'current_question':str_next_question,
                                            'id_ast_coach_question': id_ast_coach_question,
                                            'error_message':''}
                print(f"El diccionario de respuestas es:{diccionario_respuestas}")
                return JsonResponse({'result':True,
                            'coach_comment':coach_comment,
                            'is_correct':is_correct,
                            'avatar':avatar,
                            'current_question':str_next_question,
                            'id_ast_coach_question': id_ast_coach_question,
                            'goodbye':goodbye,
                            'error_message':''})
            except Exception as e:
                return JsonResponse({'result':False,'error_message': str(e)})
    else:
        return render(request, 'assistant_coach.html')
