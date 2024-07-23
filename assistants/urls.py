from django.urls import path
from . import views

urlpatterns = [
    path('', views.ServiceDesk_VA, name='ServiceDesk_VA'),
    path('servicetonic/', views.ServiceDesk_VA, name='ServiceDesk_VA'),  
]
