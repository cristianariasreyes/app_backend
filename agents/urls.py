from django.urls import path
from . import views

urlpatterns = [
    path('', views.getRoutes, name='getRoutes'),
    path('service_desk/', views.ServiceDesk, name='ServiceDesk'),
    path('service_desk/get_categories', views.ServiceDesk_GetCategories, name='ServiceDesk_GetCategories'),
    path('service_desk/get_sentiment', views.ServiceDesk_GetSentiment, name='ServiceDesk_GetSentiment'),
    path('service_desk/mail_response', views.ServiceDesk_MailResponse, name='ServiceDesk_MailResponse')
]
