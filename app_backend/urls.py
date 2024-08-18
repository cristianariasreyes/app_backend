"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
urlpatterns = [
    path('', views.getRoutes, name='getRoutesss'),
    path('register/', views.RegisterUser, name='register'),
    path('login/', views.LoginUser, name='login'),
    path('logout/', views.LogOutUser, name='logout'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/access/', TokenVerifyView.as_view(), name='token_access'),
    path('admin/', admin.site.urls),
    path('chat/', include('chat.urls')),
    path('documents/', include('documents.urls')),
    path('assistants/', include('assistants.urls')),
    path('agents/', include('agents.urls')),
]
