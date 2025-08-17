# app_eventos/admin.py
from .models import (
    User, EmpresaContratante, Empresa, LocalEvento, Evento, SetorEvento, Vaga, Funcao, TipoFuncao,
    Freelance, Candidatura, ContratoFreelance, TipoEmpresa,
    CategoriaEquipamento, Equipamento, EquipamentoSetor, ManutencaoEquipamento
)
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .mixins import EmpresaContratanteMixin


@admin.register(EmpresaContratante)
class EmpresaContratanteAdmin(admin.ModelAdmin):
    list_display = ('nome_fantasia', 'cnpj', 'plano_contratado', 'valor_mensal', 'ativo', 'data_vencimento')
    list_filter = ('ativo', 'plano_contratado', 'data_contratacao')
    search_fields = ('nome_fantasia', 'razao_social', 'cnpj', 'email')
    readonly_fields = ('data_atualizacao',)
    
    fieldsets = (
        ("Informações Básicas", {
            "fields": ("nome", "cnpj", "razao_social", "nome_fantasia")
        }),
        ("Contato", {
            "fields": ("telefone", "email", "website")
        }),
        ("Endereço", {
            "fields": ("cep", "logradouro", "numero", "complemento", "bairro", "cidade", "uf")
        }),
        ("Contrato", {
            "fields": ("data_contratacao", "data_vencimento", "plano_contratado", "valor_mensal")
        }),
        ("Status", {
            "fields": ("ativo", "data_atualizacao")
        }),
    )


@admin.register(User)
class UserAdmin(BaseUserAdmin, EmpresaContratanteMixin):
    list_display = ('username', 'email', 'tipo_usuario', 'empresa_contratante', 'ativo', 'data_ultimo_acesso')
    list_filter = ('tipo_usuario', 'ativo', 'empresa_contratante', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('data_ultimo_acesso',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Empresa e Permissões", {
            "fields": ("tipo_usuario", "empresa_contratante", "ativo")
        }),
        ("Informações Adicionais", {
            "fields": ("data_ultimo_acesso",)
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Empresa e Permissões", {
            "fields": ("tipo_usuario", "empresa_contratante", "ativo")
        }),
    )


@admin.register(TipoEmpresa)
class TipoEmpresaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')
    search_fields = ('nome',)


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin, EmpresaContratanteMixin):
    list_display = ('nome', 'cnpj', 'tipo_empresa', 'empresa_contratante', 'ativo')
    list_filter = ('tipo_empresa', 'ativo', 'empresa_contratante')
    search_fields = ('nome', 'cnpj', 'email')
    autocomplete_fields = ('tipo_empresa',)


@admin.register(LocalEvento)
class LocalEventoAdmin(admin.ModelAdmin, EmpresaContratanteMixin):
    list_display = ('nome', 'endereco', 'capacidade', 'empresa_contratante', 'empresa_proprietaria', 'ativo')
    list_filter = ('ativo', 'empresa_contratante')
    search_fields = ('nome', 'endereco')
    autocomplete_fields = ('empresa_proprietaria',)


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin, EmpresaContratanteMixin):
    list_display = ('nome', 'data_inicio', 'data_fim', 'empresa_contratante', 'local', 'ativo')
    list_filter = ('ativo', 'empresa_contratante', 'data_inicio', 'data_fim')
    search_fields = ('nome',)
    autocomplete_fields = ('local', 'empresa_produtora', 'empresa_contratante_mao_obra')


@admin.register(SetorEvento)
class SetorEventoAdmin(admin.ModelAdmin, EmpresaContratanteMixin):
    list_display = ('nome', 'evento', 'ativo')
    list_filter = ('ativo', 'evento__empresa_contratante')
    search_fields = ('nome',)
    autocomplete_fields = ('evento',)


@admin.register(Vaga)
class VagaAdmin(admin.ModelAdmin, EmpresaContratanteMixin):
    list_display = ('titulo', 'setor', 'quantidade', 'remuneracao', 'ativa')
    list_filter = ('ativa', 'setor__evento__empresa_contratante')
    search_fields = ('titulo',)
    autocomplete_fields = ('setor',)


@admin.register(TipoFuncao)
class TipoFuncaoAdmin(admin.ModelAdmin, EmpresaContratanteMixin):
    list_display = ('nome', 'empresa_contratante', 'ativo')
    list_filter = ('ativo', 'empresa_contratante')
    search_fields = ('nome',)


@admin.register(Funcao)
class FuncaoAdmin(admin.ModelAdmin, EmpresaContratanteMixin):
    list_display = ('nome', 'tipo_funcao', 'ativo')
    list_filter = ('ativo', 'tipo_funcao__empresa_contratante')
    search_fields = ('nome',)
    autocomplete_fields = ('tipo_funcao',)


@admin.register(Freelance)
class FreelanceAdmin(admin.ModelAdmin, EmpresaContratanteMixin):
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


@admin.register(Candidatura)
class CandidaturaAdmin(admin.ModelAdmin, EmpresaContratanteMixin):
    list_display = ('freelance', 'vaga', 'status', 'data_candidatura')
    list_filter = ('status', 'vaga__setor__evento__empresa_contratante')
    search_fields = ('freelance__nome_completo', 'vaga__titulo')
    autocomplete_fields = ('freelance', 'vaga')


@admin.register(ContratoFreelance)
class ContratacaoFreelanceAdmin(admin.ModelAdmin, EmpresaContratanteMixin):
    list_display = ('freelance', 'vaga', 'status', 'data_contratacao')
    list_filter = ('status', 'vaga__setor__evento__empresa_contratante')
    search_fields = ('freelance__nome_completo', 'vaga__titulo')
    autocomplete_fields = ('freelance', 'vaga')


@admin.register(CategoriaEquipamento)
class CategoriaEquipamentoAdmin(admin.ModelAdmin, EmpresaContratanteMixin):
    list_display = ('nome', 'empresa_contratante', 'ativo')
    list_filter = ('ativo', 'empresa_contratante')
    search_fields = ('nome',)


@admin.register(Equipamento)
class EquipamentoAdmin(admin.ModelAdmin, EmpresaContratanteMixin):
    list_display = ('codigo_patrimonial', 'empresa_contratante', 'empresa_proprietaria', 'categoria', 'marca', 'modelo', 'estado_conservacao', 'ativo')
    list_filter = ('empresa_contratante', 'empresa_proprietaria', 'categoria', 'estado_conservacao', 'ativo')
    search_fields = ('codigo_patrimonial', 'marca', 'modelo', 'numero_serie', 'empresa_proprietaria__nome')
    autocomplete_fields = ('empresa_proprietaria', 'categoria')
    
    fieldsets = (
        ("Empresa", {
            "fields": ("empresa_proprietaria",)
        }),
        ("Informações Básicas", {
            "fields": ("codigo_patrimonial", "categoria", "descricao", "especificacoes_tecnicas")
        }),
        ("Detalhes Técnicos", {
            "fields": ("marca", "modelo", "numero_serie", "estado_conservacao")
        }),
        ("Informações Financeiras", {
            "fields": ("data_aquisicao", "valor_aquisicao")
        }),
        ("Arquivos", {
            "fields": ("foto", "manual_instrucoes")
        }),
        ("Status", {
            "fields": ("ativo", "criado_em", "atualizado_em")
        }),
    )
    readonly_fields = ("criado_em", "atualizado_em")


@admin.register(EquipamentoSetor)
class EquipamentoSetorAdmin(admin.ModelAdmin, EmpresaContratanteMixin):
    list_display = ('equipamento', 'empresa_equipamento', 'setor', 'evento', 'quantidade_necessaria', 'quantidade_disponivel', 'status')
    list_filter = ('equipamento__empresa_contratante', 'setor__evento', 'equipamento__categoria', 'status')
    search_fields = ('equipamento__codigo_patrimonial', 'setor__nome', 'equipamento__empresa_proprietaria__nome')
    autocomplete_fields = ('setor', 'equipamento', 'responsavel_equipamento')
    
    fieldsets = (
        ("Relacionamento", {
            "fields": ("setor", "equipamento")
        }),
        ("Quantidades", {
            "fields": ("quantidade_necessaria", "quantidade_disponivel")
        }),
        ("Período de Uso", {
            "fields": ("data_inicio_uso", "data_fim_uso")
        }),
        ("Responsabilidade", {
            "fields": ("responsavel_equipamento", "status", "observacoes")
        }),
        ("Timestamps", {
            "fields": ("criado_em", "atualizado_em")
        }),
    )
    readonly_fields = ("criado_em", "atualizado_em")
    
    def empresa_equipamento(self, obj):
        return obj.equipamento.empresa_proprietaria.nome
    empresa_equipamento.short_description = "Empresa do Equipamento"
    
    def evento(self, obj):
        return obj.setor.evento.nome
    evento.short_description = "Evento"


@admin.register(ManutencaoEquipamento)
class ManutencaoEquipamentoAdmin(admin.ModelAdmin, EmpresaContratanteMixin):
    list_display = ('equipamento', 'tipo_manutencao', 'status', 'data_inicio', 'data_fim', 'custo')
    list_filter = ('tipo_manutencao', 'status', 'equipamento__categoria')
    search_fields = ('equipamento__codigo_patrimonial', 'fornecedor')
    autocomplete_fields = ('equipamento', 'responsavel')
    
    fieldsets = (
        ("Equipamento", {
            "fields": ("equipamento", "tipo_manutencao")
        }),
        ("Detalhes da Manutenção", {
            "fields": ("descricao", "observacoes")
        }),
        ("Período", {
            "fields": ("data_inicio", "data_fim")
        }),
        ("Custos e Fornecedor", {
            "fields": ("custo", "fornecedor")
        }),
        ("Responsabilidade", {
            "fields": ("responsavel", "status")
        }),
        ("Timestamps", {
            "fields": ("criado_em",)
        }),
    )
    readonly_fields = ("criado_em",)


