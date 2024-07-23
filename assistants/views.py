from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .services.ServiceDesk_assistant import Servicetonic_assistant
import json


@csrf_exempt
def ServiceDesk_VA(request):
    
    if request.method=='POST':
        print("Entrando a la funcion de atencion de tickets de ServiceDesk...") 
        data = request.POST
        id_incident_project = data.get('id_incident_project')
        
        #Verificamo que el campo id_incident_project venga informado y no vacio. Si no esta informado
        #o viene vacio retornamos un mensaje de error.
        if id_incident_project == None or id_incident_project == "":
            return JsonResponse({'message': 'No se envio el id de ticket para ser atendido'})
        
        ticket = Servicetonic_assistant("servicetonic")
        response = ticket.update_servicetonic_ticket_with_category(id_incident_project)
        user_sentiment = response['user_sentiment']
        agora_response = response['agora_response']
        categoria = response['categoria']
        sub_categoria = response['sub_categoria']
        detalle = response['detalle']
        message = f'Se atendio el ticket {id_incident_project} correctamente'
        
        #Retornamos un jason con estops valores para que el front pueda mostrarlos en pantalla.
        return JsonResponse({
                    'message': message,
                    'user_sentiment': user_sentiment,
                    'agora_response': agora_response,
                    'categoria': categoria,
                    'sub_categoria': sub_categoria,
                    'detalle': detalle
                    })
     
    else:
        return render(request, 'servicetonic.html')

