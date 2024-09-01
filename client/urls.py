from django.urls import path
from . import views

urlpatterns = [
    path('', views.GetDocument, name="GetDocument"),
          
]
