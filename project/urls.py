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
from django.conf import settings
from django.conf.urls.static import static
from app.views import SolicitacaoCodigoView, RedefinirSenhaView

from app.views import (
    home,
    CustomLoginView,
    CriarEleitorView,
    CamaraDeputadosView,
    SenadoView,
    CandidatosTSEView,
    EleitorViewSet, 
    DeputadoFavoritoViewSet, 
    ResultadoQuizViewSet
)

router = DefaultRouter()
router.register(r'eleitores', EleitorViewSet, basename='eleitor')
router.register(r'favoritos', DeputadoFavoritoViewSet, basename='favorito')
router.register(r'quiz-resultados', ResultadoQuizViewSet, basename='quiz-resultado')

urlpatterns = [

    path('admin/', admin.site.urls),
    path('', home, name='home'),
    
    path('api/cadastrar/', CriarEleitorView.as_view(), name='cadastrar'),
    path('api/login/', CustomLoginView.as_view(), name='login'),
    
    path('api/deputados-camara/', CamaraDeputadosView.as_view(), name='deputados_camara'),
    path('api/senadores/', SenadoView.as_view(), name='senadores'),
    path('api/candidatos-tse/', CandidatosTSEView.as_view(), name='candidatos_tse'),
    
    path('api/', include(router.urls)),

    path('api/esqueci-senha/', SolicitacaoCodigoView.as_view(), name='esqueci_senha'),
    path('api/redefinir-senha/', RedefinirSenhaView.as_view(), name='redefinir_senha'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)