from rest_framework import serializers
from .models import Eleitor, DeputadoFavorito, ResultadoQuiz

class PerfilEleitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Eleitor
        fields = ['id', 'nome', 'apelido', 'email', 'cpf', 'rg', 'endereco', 'data_nascimento', 'foto_perfil']
        read_only_fields = ['email', 'cpf'] # Impede alteracao direta de chaves unicas sem validacao extra

class ResetSenhaSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ConfirmarCodigoSerializer(serializers.Serializer):
    email = serializers.EmailField()
    codigo = serializers.CharField(max_length=6)
    nova_senha = serializers.CharField(min_length=8)

class EleitorSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Eleitor
        fields = ['id', 'username', 'email', 'nome', 'apelido', 'data_nascimento', 'password']

    def create(self, validated_data):
        #create_user para garantir que a senha seja salva criptografada
        user = Eleitor.objects.create_user(**validated_data)
        return user


class DeputadoFavoritoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeputadoFavorito
        fields = ['id', 'eleitor', 'deputado_id', 'nome_deputado', 'comentario', 'data_adicao']
        read_only_fields = ['id', 'eleitor', 'data_adicao']


class ResultadoQuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultadoQuiz
        fields = ['id', 'eleitor', 'classe_social_resultado', 'data_teste']
        read_only_fields = ['id', 'eleitor', 'data_teste']