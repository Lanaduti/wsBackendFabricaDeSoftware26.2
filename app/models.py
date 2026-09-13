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
    
    codigo_recuperacao = models.CharField(max_length=6, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'nome']

    def __str__(self):
        return self.apelido or self.nome or self.email


class DeputadoFavorito(models.Model):
    eleitor = models.ForeignKey(Eleitor, on_delete=models.CASCADE, related_name='favoritos')
    deputado_id = models.IntegerField()
    nome_deputado = models.CharField(max_length=150)
    partido = models.CharField(max_length=50, blank=True, null=True)
    foto_url = models.URLField(blank=True, null=True)
    comentario = models.TextField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('eleitor', 'deputado_id')

    def __str__(self):
        return f"{self.eleitor.nome} favoritou {self.nome_deputado}"


class ResultadoQuiz(models.Model):
    eleitor = models.ForeignKey(Eleitor, on_delete=models.CASCADE, related_name='resultados_quiz')
    classe_social_resultado = models.CharField(max_length=200)
    data_teste = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Resultado Quiz de {self.eleitor.nome}"


class Comentario(models.Model):
    eleitor = models.ForeignKey(Eleitor, on_delete=models.CASCADE)
    parlamentar_id = models.IntegerField()  # ID do parlamentar na API da Camara/Senado
    tipo_parlamentar = models.CharField(max_length=20, choices=[('deputado', 'Deputado'), ('senador', 'Senador')])
    texto = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comentário de {self.eleitor.nome} no parlamentar {self.parlamentar_id}"


class VotoEleitor(models.Model):
    CARGOS_CHOICES = [
        ('presidente', 'Presidente'),
        ('governador', 'Governador'),
        ('senador', 'Senador'),
        ('deputado_federal', 'Deputado Federal'),
        ('deputado_estadual', 'Deputado Estadual'),
        ('prefeito', 'Prefeito'),
    ]

    eleitor = models.ForeignKey(Eleitor, on_delete=models.CASCADE, related_name='votos')
    cargo = models.CharField(max_length=30, choices=CARGOS_CHOICES)
    candidato_id = models.IntegerField()
    nome_candidato = models.CharField(max_length=150)
    partido = models.CharField(max_length=50, blank=True, null=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        
        unique_together = ('eleitor', 'cargo')

    def __str__(self):
        return f"{self.eleitor.nome} -> {self.nome_candidato} ({self.cargo})"