import random
import requests
from django.shortcuts import render
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import authenticate
from django.db.models import Q, Count

from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.authtoken.models import Token

from .models import (
    Eleitor, 
    DeputadoFavorito, 
    ResultadoQuiz, 
    Comentario, 
    VotoEleitor
)
from .serializers import (
    EleitorSerializer,
    PerfilEleitorSerializer,
    ResetSenhaSerializer,
    ConfirmarCodigoSerializer,
    DeputadoFavoritoSerializer,
    ResultadoQuizSerializer,
    ComentarioSerializer,
    VotoEleitorSerializer
)


class CustomLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        login_input = request.data.get('username') or request.data.get('email') or request.data.get('login') or request.data.get('email_or_cpf')
        password = request.data.get('password')

        if not login_input or not password:
            return Response({'error': 'Informe o e-mail/CPF e a senha.'}, status=status.HTTP_400_BAD_REQUEST)
        
        login_limpo = login_input.replace('.', '').replace('-', '').strip()
        
        user_obj = Eleitor.objects.filter(
            Q(email__iexact=login_input) | 
            Q(cpf=login_limpo) | 
            Q(cpf=login_input) |
            Q(username__iexact=login_input)
        ).first()

        if user_obj:
            
            user: Eleitor = authenticate(username=user_obj.username, password=password)

            if user is not None:
                token, _ = Token.objects.get_or_create(user=user)
                return Response({
                    'token': token.key,
                    'nome': user.nome or user.first_name or "Eleitor",  
                    'email': user.email,                                
                    'cpf': user.cpf
                }, status=status.HTTP_200_OK)

        return Response({'error': 'E-mail, CPF ou senha inválidos.'}, status=status.HTTP_400_BAD_REQUEST)

class SolicitacaoCodigoView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ResetSenhaSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
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
                    fail_silently=True,
                )
            return Response({'message': 'Se o e-mail estiver cadastrado, o código foi enviado.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RedefinirSenhaView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ConfirmarCodigoSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            codigo = serializer.validated_data['codigo']
            nova_senha = serializer.validated_data['nova_senha']

            user = Eleitor.objects.filter(email=email, codigo_recuperacao=codigo).first()
            if user and codigo:
                user.set_password(nova_senha)
                user.codigo_recuperacao = None
                user.save()
                return Response({'message': 'Senha alterada com sucesso!'}, status=status.HTTP_200_OK)

            return Response({'error': 'Código inválido ou e-mail incorreto.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CriarEleitorView(generics.CreateAPIView):
    queryset = Eleitor.objects.all()
    serializer_class = EleitorSerializer
    permission_classes = [permissions.AllowAny]


class EleitorViewSet(viewsets.ModelViewSet):
    queryset = Eleitor.objects.all()
    serializer_class = EleitorSerializer

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return PerfilEleitorSerializer
        return EleitorSerializer


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


class ComentarioViewSet(viewsets.ModelViewSet):
    serializer_class = ComentarioSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        queryset = Comentario.objects.all().order_by('-criado_em')
        parlamentar_id = self.request.query_params.get('parlamentar_id')
        if parlamentar_id:
            queryset = queryset.filter(parlamentar_id=parlamentar_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(eleitor=self.request.user)


class VotoEleitorViewSet(viewsets.ModelViewSet):
    serializer_class = VotoEleitorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return VotoEleitor.objects.filter(eleitor=self.request.user)

    def create(self, request, *args, **kwargs):
        cargo = request.data.get('cargo')
        candidato_id = request.data.get('candidato_id')
        nome_candidato = request.data.get('nome_candidato')
        partido = request.data.get('partido')

        voto, created = VotoEleitor.objects.update_or_create(
            eleitor=request.user,
            cargo=cargo,
            defaults={
                'candidato_id': candidato_id,
                'nome_candidato': nome_candidato,
                'partido': partido
            }
        )
        serializer = self.get_serializer(voto)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(serializer.data, status=status_code)


class DashboardPublicoView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        top_favoritos = DeputadoFavorito.objects.values(
            'deputado_id', 'nome_deputado', 'partido', 'foto_url'
        ).annotate(total_favoritos=Count('id')).order_by('-total_favoritos')[:5]

        ranking_votos = VotoEleitor.objects.values(
            'cargo', 'candidato_id', 'nome_candidato', 'partido'
        ).annotate(total_votos=Count('id')).order_by('cargo', '-total_votos')

        return Response({
            'deputados_mais_favoritados': top_favoritos,
            'ranking_votos_comunidade': ranking_votos
        }, status=status.HTTP_200_OK)


def home(request):
    return render(request, 'index.html')