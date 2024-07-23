from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_with_documents, name='chat_with_documents'),
    path('chat_assistant/', views.Getchat_assistant, name='Getchat_assistant'),  
    path('chat_assistant/<int:id>', views.Getchat_assistant_detail, name="Getchat_assistant_detail"),
    path('chat_assistant_documents/', views.Get_chat_assistant_document, name='Get_chat_assistant_document'),  
    path('chat_assistant_documents/<int:id>', views.Get_chat_assistant_document_detail, name="Get_chat_assistant_document_detail"),
    path('chat_my_docs/<int:id>', views.chat_my_docs, name='chat_my_docs'),  
    path('chat_with_assistant/<int:id>', views.chat_with_an_assistant, name='chat_with_an_assistant'),  
    path('chat/evaluate_answer/<int:id_chat_history>/<int:useful>', views.evaluate_answer, name='evaluate_answer'),  
    
    
]
