from rest_framework import serializers
from .models import Eleitor, DeputadoFavorito, ResultadoQuiz

class EleitorSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Eleitor
        fields = ['id', 'username', 'email', 'nome', 'data_nascimento', 'password']

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