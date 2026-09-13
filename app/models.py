from django.db import models
from django.contrib.auth.models import AbstractUser 

class Eleitor(AbstractUser):
    nome = models.CharField(max_length=150)
    apelido = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(unique=True)
    cpf = models.CharField(max_length=11, unique=True, null=True, blank=True)
    rg = models.CharField(max_length=20, null=True, blank=True)
    endereco = models.CharField(max_length=255, null=True, blank=True)
    data_nascimento = models.DateField(null=True, blank=True)
    foto_perfil = models.ImageField(upload_to='perfis/', null=True, blank=True)
    
    # Campo para armazenar o codigo de recuperacao temporario
    codigo_recuperacao = models.CharField(max_length=6, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'nome']

    def __str__(self):
        return self.apelido if self.apelido else self.nome
     
class DeputadoFavorito(models.Model):
    deputado_id = models.IntegerField()
    nome = models.CharField(max_length=150)
    comentario = models.TextField(blank=True, null=True)
    eleitor = models.ForeignKey(Eleitor, on_delete=models.CASCADE, related_name='favoritos')

class ResultadoQuiz(models.Model):
    eleitor = models.ForeignKey(Eleitor, on_delete=models.CASCADE, related_name='resultados_quiz')
    classe_social_resultado = models.CharField(max_length=200)
    data_teste = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.eleitor.nome} - {self.c}"