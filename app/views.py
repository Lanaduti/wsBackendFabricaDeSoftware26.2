from django.shortcuts import render
import requests
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics

from .models import Eleitor, DeputadoFavorito, ResultadoQuiz
from .serializers import (
    EleitorSerializer, 
    DeputadoFavoritoSerializer, 
    ResultadoQuizSerializer
)


class EleitorViewSet(viewsets.ModelViewSet):
    queryset = Eleitor.objects.all()
    serializer_class = EleitorSerializer


class DeputadoFavoritoViewSet(viewsets.ModelViewSet):
    serializer_class = DeputadoFavoritoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        
        return DeputadoFavorito.objects.filter(eleitor=self.request.user)

    def perform_create(self, serializer):
     
        serializer.save(eleitor=self.request.user)


class ResultadoQuizViewSet(viewsets.ModelViewSet):
    serializer_class = ResultadoQuizSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
       
        return ResultadoQuiz.objects.filter(eleitor=self.request.user)

    def perform_create(self, serializer):
       
        serializer.save(eleitor=self.request.user)


class CamaraDeputadosView(APIView):
    def get(self, request):
        
        uf = request.query_params.get('uf', 'PB')
        
        url = "https://dadosabertos.camara.leg.br/api/v2/deputados"
        params = {
            'siglaUf': uf,
            'ordem': 'ASC',
            'ordenarPor': 'nome'
        }
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                dados = response.json()
                return Response(dados, status=status.HTTP_200_OK)
            return Response({'error': 'Erro ao buscar dados da Câmara'}, status=response.status_code)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class CriarEleitorView(generics.CreateAPIView):
    queryset = Eleitor.objects.all()
    serializer_class = EleitorSerializer
    permission_classes = [permissions.AllowAny]