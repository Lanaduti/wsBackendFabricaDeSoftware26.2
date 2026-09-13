from rest_framework import serializers
from .models import Eleitor, DeputadoFavorito, ResultadoQuiz, Comentario, VotoEleitor


class PerfilEleitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Eleitor
        fields = ['id', 'nome', 'apelido', 'email', 'cpf', 'rg', 'endereco', 'data_nascimento', 'foto_perfil']
        read_only_fields = ['email', 'cpf']  


class ResetSenhaSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ConfirmarCodigoSerializer(serializers.Serializer):
    email = serializers.EmailField()
    codigo = serializers.CharField(max_length=6)
    nova_senha = serializers.CharField(min_length=8)


class EleitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Eleitor
        fields = ['id', 'username', 'email', 'nome', 'cpf', 'rg', 'endereco', 'data_nascimento', 'foto_perfil', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'required': False}  
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = Eleitor(**validated_data)
        if password:
            user.set_password(password)  
        user.save()
        return user


class DeputadoFavoritoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeputadoFavorito
        fields = '__all__'
        read_only_fields = ['eleitor']


class ResultadoQuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultadoQuiz
        fields = '__all__'
        read_only_fields = ['eleitor']


class ComentarioSerializer(serializers.ModelSerializer):
    nome_eleitor = serializers.ReadOnlyField(source='eleitor.nome')
    foto_eleitor = serializers.SerializerMethodField()

    class Meta:
        model = Comentario
        fields = ['id', 'eleitor', 'nome_eleitor', 'foto_eleitor', 'parlamentar_id', 'tipo_parlamentar', 'texto', 'criado_em']
        read_only_fields = ['eleitor']

    def get_foto_eleitor(self, obj):
        request = self.context.get('request')
        if obj.eleitor.foto_perfil and hasattr(obj.eleitor.foto_perfil, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.eleitor.foto_perfil.url)
            return obj.eleitor.foto_perfil.url
        return None


class VotoEleitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = VotoEleitor
        fields = ['id', 'cargo', 'candidato_id', 'nome_candidato', 'partido', 'atualizado_em']
        read_only_fields = ['eleitor']