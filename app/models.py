from django.db import models
from django.contrib.auth.models import AbstractUser 

class Eleitor(AbstractUser):
    nome = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    data_nascimento = models.DateField() # Adicionado para checar se possui idade >= 16 anos

    groups = models.ManyToManyField('auth.Group', related_name='eleitor_set', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='eleitor_permissions_set', blank=True )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','nome','data_nascimento']

    def __str__(self):
        return self.nome 
     
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