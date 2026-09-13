from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    home,
    CustomLoginView,
    CriarEleitorView,
    SolicitacaoCodigoView,
    RedefinirSenhaView,
    CamaraDeputadosView,
    SenadoView,
    CandidatosTSEView,
    EleitorViewSet, 
    DeputadoFavoritoViewSet, 
    ResultadoQuizViewSet,
    ComentarioViewSet,
    VotoEleitorViewSet,
    DashboardPublicoView
)

router = DefaultRouter()
router.register(r'eleitores', EleitorViewSet, basename='eleitor')
router.register(r'favoritos', DeputadoFavoritoViewSet, basename='favorito')
router.register(r'quiz-resultados', ResultadoQuizViewSet, basename='quiz-resultado')
router.register(r'comentarios', ComentarioViewSet, basename='comentario')
router.register(r'votos', VotoEleitorViewSet, basename='voto')

urlpatterns = [
    path('', home, name='home'),
    path('cadastrar/', CriarEleitorView.as_view(), name='cadastrar'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('solicitar-codigo/', SolicitacaoCodigoView.as_view(), name='solicitar_codigo'),
    path('redefinir-senha/', RedefinirSenhaView.as_view(), name='redefinir_senha'),
    
    path('dashboard/', DashboardPublicoView.as_view(), name='dashboard'),
    
    path('deputados-camara/', CamaraDeputadosView.as_view(), name='deputados_camara'),
    path('senadores/', SenadoView.as_view(), name='senadores'),
    path('candidatos-tse/', CandidatosTSEView.as_view(), name='candidatos_tse'),
    
    path('', include(router.urls)),
]