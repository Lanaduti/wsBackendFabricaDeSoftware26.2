from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Eleitor, DeputadoFavorito, ResultadoQuiz
from .serializers import EleitorSerializer, DeputadoFavoritoSerializer, ResultadoQuizSerializer

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

