from django.urls import path
from . import views

urlpatterns = [
    path('', views.GetDocument, name="GetDocument"),
    path('<int:id>', views.DocumentHandle, name="DocumentHandle"),
    path('document_type/', views.document_type, name="document_type"),
    path('document_type/<int:id>', views.document_type_detail, name="document_type_detail"),
    path('document_category/', views.document_category, name="document_category"),
    path('document_category/<int:id>', views.document_category_detail, name="document_category_detail"),
    path('document_department/', views.document_department, name="document_department"),
    path('document_department/<int:id>', views.document_department_detail, name="document_department_detail"),
    path('new_document/', views.SaveDocument, name="new_document"),
          
]
