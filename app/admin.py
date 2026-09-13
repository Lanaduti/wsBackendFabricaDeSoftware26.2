from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Eleitor, DeputadoFavorito, ResultadoQuiz, Comentario, VotoEleitor

@admin.register(Eleitor)
class EleitorAdmin(UserAdmin):
  
    list_display = ('nome', 'email',  'cpf', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('nome', 'email', 'cpf', 'username')
    ordering = ('nome',)

    fieldsets = UserAdmin.fieldsets + (
        ('Informações Pessoais Extra', {
            'fields': ('nome', 'apelido', 'cpf', 'rg', 'endereco', 'data_nascimento', 'foto_perfil', 'codigo_recuperacao')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações Pessoais Extra', {
            'fields': ('nome', 'email', 'cpf')
        }),
    )


@admin.register(DeputadoFavorito)
class DeputadoFavoritoAdmin(admin.ModelAdmin):
    list_display = ('id', 'eleitor', 'nome_deputado', 'partido', 'criado_em')
    search_fields = ('nome_deputado', 'eleitor__nome', 'eleitor__email', 'partido')
    list_filter = ('partido', 'criado_em')


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'eleitor', 'tipo_parlamentar', 'parlamentar_id', 'texto_resumido', 'criado_em')
    search_fields = ('eleitor__nome', 'texto', 'parlamentar_id')
    list_filter = ('tipo_parlamentar', 'criado_em')

    def texto_resumido(self, obj):
        return obj.texto[:50] + '...' if len(obj.texto) > 50 else obj.texto
    texto_resumido.short_description = 'Comentário'


@admin.register(VotoEleitor)
class VotoEleitorAdmin(admin.ModelAdmin):
    list_display = ('id', 'eleitor', 'cargo', 'nome_candidato', 'partido', 'atualizado_em')
    search_fields = ('eleitor__nome', 'nome_candidato', 'partido')
    list_filter = ('cargo', 'partido', 'atualizado_em')


@admin.register(ResultadoQuiz)
class ResultadoQuizAdmin(admin.ModelAdmin):
    list_display = ('id', 'eleitor', 'classe_social_resultado', 'data_teste')
    search_fields = ('eleitor__nome', 'classe_social_resultado')
    list_filter = ('data_teste',)