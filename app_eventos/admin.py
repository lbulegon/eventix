# app_eventos/admin.py
from django.contrib import admin
from .models import User, Empresa, LocalEvento, Evento, SetorEvento, Vaga,Funcao, TipoFuncao
from .models import Freelance, Candidatura, ContratoFreelance



@admin.register(Candidatura)
class CandidaturaAdmin(admin.ModelAdmin):
    list_display = ('freelance', 'vaga', 'status', 'data_candidatura')
    list_filter = ('status',)
    search_fields = ('freelance__nome_completo', 'vaga__nome')


@admin.register(ContratoFreelance)
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





@admin.register(Freelance)
class FreelanceAdmin(admin.ModelAdmin):
    list_display = ("nome_completo", "cpf", "telefone", "cadastro_completo", "atualizado_em")
    search_fields = ("nome_completo", "cpf", "telefone")
    list_filter = ("cadastro_completo", "sexo", "estado_civil")

    fieldsets = (
        ("Dados Pessoais", {
            "fields": (
                "usuario", "nome_completo", "telefone", "cpf", "rg", "orgao_expedidor", "uf_rg",
                "data_nascimento", "sexo", "estado_civil", "nacionalidade", "naturalidade",
                "nome_mae", "nome_pai", "foto"
            )
        }),
        ("Endereço", {
            "fields": (
                "cep", "logradouro", "numero", "complemento", "bairro", "cidade", "uf"
            )
        }),
        ("Vínculo", {
            "fields": (
                "tipo_vinculo", "data_admissao", "data_rescisao", "cargo", "departamento",
                "valor_hora", "carga_horaria", "escala_trabalho"
            )
        }),
        ("Documentos Extras", {
            "fields": (
                "pis_pasep", "carteira_trabalho_numero", "carteira_trabalho_serie",
                "titulo_eleitor", "cnh_numero", "cnh_categoria", "certificado_reservista"
            )
        }),
        ("Dados Bancários", {
            "fields": (
                "banco", "agencia", "conta", "tipo_conta", "chave_pix"
            )
        }),
        ("Uploads de Arquivos", {
            "fields": (
                "arquivo_exame_medico",
                "arquivo_comprovante_residencia",
                "arquivo_identidade_frente",
                "arquivo_identidade_verso",
            )
        }),
        ("Observações", {
            "fields": ("observacoes", "observacoes_medicas")
        }),
        ("Status", {
            "fields": ("cadastro_completo", "atualizado_em")
        }),
    )

    readonly_fields = ("cadastro_completo", "atualizado_em")
