"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
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
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

from app.views import (
    EleitorViewSet, 
    DeputadoFavoritoViewSet, 
    ResultadoQuizViewSet, 
    CamaraDeputadosView,
    CriarEleitorView
)

router = DefaultRouter()
router.register(r'eleitores', EleitorViewSet, basename='eleitor')
router.register(r'favoritos', DeputadoFavoritoViewSet, basename='favorito')
router.register(r'quiz-resultados', ResultadoQuizViewSet, basename='quiz-resultado')

urlpatterns = [
    
    path('admin/', admin.site.urls),
    
    path('api/', include(router.urls)),
    
    path('api/deputados-camara/', CamaraDeputadosView.as_view(), name='deputados-camara'),

    path('api/cadastrar/', CriarEleitorView.as_view(), name='cadastrar_eleitor'),
    path('api/login/', obtain_auth_token, name='login_eleitor'),

]
