# app_eventos/admin.py
from django.contrib import admin
from .models import User, Empresa, LocalEvento, Evento, SetorEvento, Vaga,Funcao, TipoFuncao
from .models import Freelance, Candidatura, ContratacaoFreelance

@admin.register(Freelance)
class FreelanceAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'telefone', 'documento')
    search_fields = ('nome_completo', 'documento', 'telefone')


@admin.register(Candidatura)
class CandidaturaAdmin(admin.ModelAdmin):
    list_display = ('freelance', 'vaga', 'status', 'data_candidatura')
    list_filter = ('status',)
    search_fields = ('freelance__nome_completo', 'vaga__nome')


@admin.register(ContratacaoFreelance)
class ContratacaoFreelanceAdmin(admin.ModelAdmin):
    list_display = ('freelance', 'vaga', 'status', 'data_contratacao')
    list_filter = ('status',)
    search_fields = ('freelance__nome_completo', 'vaga__nome')



@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'tipo_usuario', 'is_active', 'is_staff')
    list_filter = ('tipo_usuario', 'is_active', 'is_staff')
    search_fields = ('username', 'email')


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo_empresa', 'cnpj', 'email', 'telefone')
    list_filter = ('tipo_empresa',)
    search_fields = ('nome', 'cnpj')


@admin.register(LocalEvento)
class LocalEventoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'endereco', 'capacidade', 'empresa_proprietaria')
    list_filter = ('empresa_proprietaria',)
    search_fields = ('nome', 'endereco')
    autocomplete_fields = ('empresa_proprietaria',)


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'data_inicio', 'data_fim', 'local', 'empresa_produtora', 'empresa_contratante')
    list_filter = ('empresa_contratante', 'empresa_produtora', 'local')
    search_fields = ('nome',)
    autocomplete_fields = ('local', 'empresa_produtora', 'empresa_contratante')


@admin.register(SetorEvento)
class SetorEventoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'evento')
    list_filter = ('evento',)
    search_fields = ('nome',)
    autocomplete_fields = ('evento',)


@admin.register(Vaga)
class VagaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'setor', 'quantidade', 'remuneracao')
    list_filter = ('setor',)
    search_fields = ('titulo',)
    autocomplete_fields = ('setor',)

@admin.register(TipoFuncao)
class TipoFuncaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')
    search_fields = ('nome',)


@admin.register(Funcao)
class FuncaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo_funcao', 'descricao')
    list_filter = ('tipo_funcao',)
    search_fields = ('nome',)

