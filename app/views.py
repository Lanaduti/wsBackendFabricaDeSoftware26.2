from django.shortcuts import render
import requests
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.db.models import Q
import random
from django.core.mail import send_mail
from django.conf import settings

from .models import Eleitor, DeputadoFavorito, ResultadoQuiz
from .serializers import (
    EleitorSerializer, 
    DeputadoFavoritoSerializer, 
    ResultadoQuizSerializer
)

class CustomLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        login_input = request.data.get('username') or request.data.get('email') or request.data.get('login')
        password = request.data.get('password')

        if not login_input or not password:
            return Response({'error': 'Informe o e-mail/CPF e a senha.'}, status=status.HTTP_400_BAD_REQUEST)

        # Remove caracteres especiais se o usuario digitou CPF formatado (000.000.000-00)
        login_limpo = login_input.replace('.', '').replace('-', '').strip()

        user_obj = Eleitor.objects.filter(Q(email=login_input) | Q(cpf=login_limpo)).first()
        
        if user_obj:
            user = authenticate(username=user_obj.username, password=password)
            if user is not None:
                token, _ = Token.objects.get_or_create(user=user)
                return Response({
                    'token': token.key,
                    'email': user.email,
                    'nome': user.nome,
                    'cpf': user.cpf
                }, status=status.HTTP_200_OK)

        return Response({'error': 'Credenciais inválidas.'}, status=status.HTTP_400_BAD_REQUEST)

class CamaraDeputadosView(APIView):
    def get(self, request):
        uf = request.query_params.get('uf', 'PB')
        url = "https://dadosabertos.camara.leg.br/api/v2/deputados"
        params = {'siglaUf': uf, 'ordem': 'ASC', 'ordenarPor': 'nome'}
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return Response(response.json(), status=status.HTTP_200_OK)
            return Response({'error': 'Erro na Câmara'}, status=response.status_code)
        except requests.exceptions.Timeout:
            return Response({'error': 'Tempo limite excedido ao consultar a Câmara.'}, status=status.HTTP_504_GATEWAY_TIMEOUT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SenadoView(APIView):
    def get(self, request):
        uf = request.query_params.get('uf', 'PB')
        url = f"https://legis.senado.leg.br/dadosabertos/senador/lista/atual.json?uf={uf}"
        try:
            response = requests.get(url, headers={'Accept': 'application/json'}, timeout=10)
            if response.status_code == 200:
                return Response(response.json(), status=status.HTTP_200_OK)
            return Response({'error': 'Erro no Senado'}, status=response.status_code)
        except requests.exceptions.Timeout:
            return Response({'error': 'Tempo limite excedido ao consultar o Senado.'}, status=status.HTTP_504_GATEWAY_TIMEOUT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class SolicitacaoCodigoView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        user = Eleitor.objects.filter(email=email).first()
        
        if user:
            
            codigo = str(random.randint(100000, 999999))
            user.codigo_recuperacao = codigo
            user.save()

            send_mail(
                'Código de Recuperação - VVCC',
                f'Seu código de verificação para redefinir a senha é: {codigo}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
        
       
        return Response({'message': 'Se o e-mail estiver cadastrado, o código foi enviado.'}, status=status.HTTP_200_OK)


class RedefinirSenhaView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        codigo = request.data.get('codigo')
        nova_senha = request.data.get('nova_senha')

        user = Eleitor.objects.filter(email=email, codigo_recuperacao=codigo).first()
        
        if user and codigo:
            user.set_password(nova_senha) 
            user.codigo_recuperacao = None 
            return Response({'message': 'Senha alterada com sucesso!'}, status=status.HTTP_200_OK)


class CandidatosTSEView(APIView):
    def get(self, request):
        uf = request.query_params.get('uf', 'PB').upper()
        cargo_id = request.query_params.get('cargo', '1')
        eleicao_id = "2045202026" 
        
        if cargo_id == "1":
            uf = "BR"

        url = f"https://divulgacandcontas.tse.jus.br/divulga/rest/v1/candidatura/listar/2026/{uf}/{eleicao_id}/{cargo_id}/candidatos"
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            if response.status_code == 200:
                return Response(response.json(), status=status.HTTP_200_OK)
            return Response({'error': 'Não foi possível buscar candidatos no TSE'}, status=response.status_code)
        except requests.exceptions.Timeout:
            return Response({'error': 'Tempo limite excedido ao consultar o TSE.'}, status=status.HTTP_504_GATEWAY_TIMEOUT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CriarEleitorView(generics.CreateAPIView):
    queryset = Eleitor.objects.all()
    serializer_class = EleitorSerializer
    permission_classes = [permissions.AllowAny]


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


def home(request):
    return render(request, 'index.html')