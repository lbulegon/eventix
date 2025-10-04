# app_eventos/admin.py
from django import forms
from .admin_restricoes import AdminRestricoesMixin
from .models import (
    User, PlanoContratacao, EmpresaContratante, Empresa, LocalEvento, Evento, SetorEvento, Vaga, Funcao, TipoFuncao,
    Freelance, Candidatura, ContratoFreelance, TipoEmpresa,
    CategoriaEquipamento, Equipamento, EquipamentoSetor, ManutencaoEquipamento,
    CategoriaFinanceira, DespesaEvento, ReceitaEvento, Fornecedor,
    # Sistema de Grupos e Permissões
    GrupoPermissaoEmpresa, PermissaoSistema, GrupoUsuario, UsuarioGrupo,
    # Sistema de Notificações
    Notificacao, ConfiguracaoNotificacao,
    # Analytics e Business Intelligence
    MetricaEvento, RelatorioAnalytics, DashboardPersonalizado, ComparativoEventos,
    # Gestão de Qualidade e Satisfação
    AvaliacaoEvento, IndicadorQualidade, PesquisaSatisfacao, FeedbackFreelancer,
    # Automação e Workflows
    WorkflowEvento, RegraNegocio, NotificacaoAutomatica, IntegracaoERP,
    # Mobilidade e Field Management
    ChecklistMobile, ItemChecklistMobile, GeolocalizacaoEquipamento, QRCodeEquipamento, ScanQRCode, AppFieldWorker,
    # Gestão de Riscos e Compliance
    RiscoEvento, PlanoContingencia, ComplianceEvento, SeguroEvento,
    # Inteligência Artificial e Predição
    PrevisaoDemanda, OtimizacaoRecursos, DeteccaoAnomalias, RecomendacaoInteligente,
    # Marketplace e Networking
    MarketplaceFreelancer, RedeFornecedores, AvaliacaoFornecedor, ContratoInteligente,
    # Gestão de Crescimento e Expansão
    FranchiseEvento, Licenciamento, ExpansaoMercado, ParceriaEstrategica
)
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .mixins import EmpresaContratanteMixin

# Importar admin dos grupos
from . import admin_grupos

# Importar admin dos modelos globais
from . import admin_globais

class ScopedAdmin(admin.ModelAdmin):
    """Filtra por empresa_contratante para usuários de empresa."""
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        u = request.user
        if getattr(u, "is_admin_sistema", False):
            return qs
        if getattr(u, "is_empresa_user", False) and hasattr(self.model, "empresa_contratante"):
            return qs.filter(empresa_contratante=u.empresa_contratante)
        return qs.none() if not u.is_superuser else qs

@admin.register(PlanoContratacao)
class PlanoContratacaoAdmin(admin.ModelAdmin, AdminRestricoesMixin):
    list_display = ('nome', 'tipo_plano', 'valor_mensal', 'max_eventos_mes', 'max_usuarios', 'ativo')
    list_filter = ('tipo_plano', 'ativo', 'suporte_24h', 'relatorios_avancados')
    search_fields = ('nome', 'descricao')
    readonly_fields = ('data_criacao', 'data_atualizacao')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'tipo_plano', 'descricao', 'ativo')
        }),
        ('Limites e Recursos', {
            'fields': ('max_eventos_mes', 'max_usuarios', 'max_freelancers', 'max_equipamentos', 'max_locais')
        }),
        ('Recursos Inclusos', {
            'fields': ('suporte_24h', 'relatorios_avancados', 'integracao_api', 'backup_automatico', 'ssl_certificado', 'dominio_personalizado')
        }),
        ('Preços', {
            'fields': ('valor_mensal', 'valor_anual', 'desconto_anual')
        }),
        ('Metadados', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )

@admin.register(EmpresaContratante)
class EmpresaContratanteAdmin(admin.ModelAdmin, AdminRestricoesMixin):
    list_display = ('nome_fantasia', 'cnpj', 'plano_contratado', 'valor_mensal', 'ativo', 'data_vencimento')
    list_filter = ('ativo', 'plano_contratado__tipo_plano', 'data_contratacao')
    search_fields = ('nome_fantasia', 'razao_social', 'cnpj', 'email')
    readonly_fields = ('data_contratacao', 'data_atualizacao')
    autocomplete_fields = ('plano_contratado',)
    
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
class UserAdmin(BaseUserAdmin, EmpresaContratanteMixin, AdminRestricoesMixin):
    list_display = ('username', 'email', 'tipo_usuario', 'empresa_contratante', 'ativo', 'data_ultimo_acesso')
    list_filter = ('tipo_usuario', 'ativo', 'empresa_contratante', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('data_ultimo_acesso',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Empresa e Permissões", {
            "fields": ("tipo_usuario", "empresa_contratante", "grupo_permissao", "ativo")
        }),
        ("Informações Adicionais", {
            "fields": ("data_ultimo_acesso",)
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Empresa e Permissões", {
            "fields": ("tipo_usuario", "empresa_contratante", "grupo_permissao", "ativo")
        }),
    )
    
    def get_queryset(self, request):
        """Filtra usuários baseado no tipo de usuário logado"""
        qs = super().get_queryset(request)
        u = request.user
        
        # Admin do sistema vê todos os usuários
        if u.tipo_usuario == 'admin_sistema':
            return qs
            
        # Admin da empresa vê apenas usuários da sua empresa
        if u.tipo_usuario == 'admin_empresa' and u.empresa_contratante:
            return qs.filter(empresa_contratante=u.empresa_contratante)
            
        # Operadores não podem ver lista de usuários
        return qs.none()
    
    def get_form(self, request, obj=None, **kwargs):
        """Personaliza o formulário baseado no tipo de usuário"""
        form = super().get_form(request, obj, **kwargs)
        
        # Se é admin da empresa, restringe alguns campos
        if request.user.tipo_usuario == 'admin_empresa':
            # Remove campos que não devem ser editados por admin da empresa
            if 'is_superuser' in form.base_fields:
                form.base_fields['is_superuser'].widget = forms.HiddenInput()
            if 'groups' in form.base_fields:
                form.base_fields['groups'].widget = forms.HiddenInput()
            if 'user_permissions' in form.base_fields:
                form.base_fields['user_permissions'].widget = forms.HiddenInput()
            if 'empresa_contratante' in form.base_fields:
                form.base_fields['empresa_contratante'].widget = forms.HiddenInput()
                
        return form
    
    def save_model(self, request, obj, form, change):
        """Personaliza o salvamento do modelo"""
        # Se é admin da empresa criando usuário
        if request.user.tipo_usuario == 'admin_empresa' and not change:
            # Define a empresa do usuário como a empresa do admin
            obj.empresa_contratante = request.user.empresa_contratante
            # Define como operador da empresa
            obj.tipo_usuario = 'operador_empresa'
            # Define como staff mas não superuser
            obj.is_staff = True
            obj.is_superuser = False
            
        super().save_model(request, obj, form, change)


@admin.register(GrupoPermissaoEmpresa)
class GrupoPermissaoEmpresaAdmin(admin.ModelAdmin, EmpresaContratanteMixin):
    list_display = ('nome', 'empresa_contratante', 'ativo', 'usuarios_count')
    list_filter = ('ativo', 'empresa_contratante')
    search_fields = ('nome', 'descricao', 'empresa_contratante__nome_fantasia')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'empresa_contratante', 'ativo')
        }),
        ('Permissões do Sistema', {
            'fields': (
                'pode_gerenciar_usuarios',
                'pode_gerenciar_eventos', 
                'pode_gerenciar_freelancers',
                'pode_gerenciar_equipamentos',
                'pode_gerenciar_estoque',
                'pode_gerenciar_financeiro',
                'pode_gerenciar_relatorios'
            )
        }),
    )
    
    def usuarios_count(self, obj):
        """Conta quantos usuários estão neste grupo"""
        return obj.usuarios.count()
    usuarios_count.short_description = 'Usuários'
    
    def get_queryset(self, request):
        """Filtra grupos baseado no tipo de usuário logado"""
        qs = super().get_queryset(request)
        u = request.user
        
        # Admin do sistema vê todos os grupos
        if u.tipo_usuario == 'admin_sistema':
            return qs
            
        # Admin da empresa vê apenas grupos da sua empresa
        if u.tipo_usuario == 'admin_empresa' and u.empresa_contratante:
            return qs.filter(empresa_contratante=u.empresa_contratante)
            
        # Operadores não podem ver grupos
        return qs.none()
    
    def get_form(self, request, obj=None, **kwargs):
        """Personaliza o formulário baseado no tipo de usuário"""
        form = super().get_form(request, obj, **kwargs)
        
        # Se é admin da empresa, restringe alguns campos
        if request.user.tipo_usuario == 'admin_empresa':
            if 'empresa_contratante' in form.base_fields:
                form.base_fields['empresa_contratante'].widget = forms.HiddenInput()
                
        return form
    
    def save_model(self, request, obj, form, change):
        """Personaliza o salvamento do modelo"""
        # Se é admin da empresa criando grupo
        if request.user.tipo_usuario == 'admin_empresa' and not change:
            # Define a empresa do grupo como a empresa do admin
            obj.empresa_contratante = request.user.empresa_contratante
            
        super().save_model(request, obj, form, change)


@admin.register(TipoEmpresa)
class TipoEmpresaAdmin(admin.ModelAdmin, AdminRestricoesMixin):
    list_display = ('nome', 'descricao')
    search_fields = ('nome',)


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin, AdminRestricoesMixin):
    list_display = ('nome', 'cnpj', 'tipo_empresa', 'ativo')
    list_filter = ('tipo_empresa', 'ativo')
    search_fields = ('nome', 'cnpj', 'email')
    autocomplete_fields = ('tipo_empresa',)


@admin.register(LocalEvento)
class LocalEventoAdmin(admin.ModelAdmin, AdminRestricoesMixin):
    list_display = ('nome', 'endereco', 'capacidade', 'empresa_proprietaria', 'ativo')
    list_filter = ('ativo', 'empresa_proprietaria')
    search_fields = ('nome', 'endereco')
    autocomplete_fields = ('empresa_proprietaria',)


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin, EmpresaContratanteMixin):
    list_display = ('nome', 'data_inicio', 'data_fim', 'empresa_contratante', 'empresa_produtora', 'local', 'ativo')
    list_filter = ('ativo', 'empresa_contratante', 'empresa_produtora', 'data_inicio', 'data_fim')
    search_fields = ('nome',)
    autocomplete_fields = ('local', 'empresa_produtora', 'empresa_contratante')
    
    fieldsets = (
        ("Informações Básicas", {
            "fields": ("nome", "descricao", "data_inicio", "data_fim", "local")
        }),
        ("Empresas", {
            "fields": ("empresa_contratante", "empresa_produtora"),
            "description": "Empresa Contratante = Operadora (cria e gerencia) | Empresa Produtora = Concedente (apenas referência)"
        }),
        ("Status", {
            "fields": ("ativo",)
        }),
    )


@admin.register(SetorEvento)
class SetorEventoAdmin(admin.ModelAdmin, EmpresaContratanteMixin):
    list_display = ('nome', 'evento', 'ativo')
    list_filter = ('ativo', 'evento__empresa_contratante')
    search_fields = ('nome',)
    autocomplete_fields = ('evento',)


@admin.register(Vaga)
class VagaAdmin(admin.ModelAdmin, EmpresaContratanteMixin):
    list_display = ('titulo', 'empresa_contratante', 'setor', 'quantidade', 'remuneracao', 'ativa')
    list_filter = ('ativa', 'empresa_contratante', 'setor__evento')
    search_fields = ('titulo',)
    autocomplete_fields = ('setor', 'empresa_contratante', 'funcao')
    
    fieldsets = (
        ("Informações da Vaga", {
            "fields": ("titulo", "descricao", "requisitos", "quantidade", "remuneracao")
        }),
        ("Relacionamentos", {
            "fields": ("setor", "empresa_contratante", "funcao"),
            "description": "Empresa Contratante = Operadora (quem cria e contrata freelancers)"
        }),
        ("Status", {
            "fields": ("ativa", "publicada", "data_limite_candidatura")
        }),
    )


@admin.register(TipoFuncao)
class TipoFuncaoAdmin(admin.ModelAdmin, AdminRestricoesMixin):
    list_display = ('nome', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('nome',)


@admin.register(Funcao)
class FuncaoAdmin(admin.ModelAdmin, EmpresaContratanteMixin):
    list_display = ('nome', 'empresa_contratante', 'tipo_funcao', 'disponivel_para_vagas', 'ativo')
    list_filter = ('ativo', 'disponivel_para_vagas', 'empresa_contratante', 'tipo_funcao')
    search_fields = ('nome', 'empresa_contratante__nome_fantasia', 'tipo_funcao__nome')
    autocomplete_fields = ('empresa_contratante', 'tipo_funcao')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('empresa_contratante', 'tipo_funcao', 'nome', 'descricao', 'ativo')
        }),
        ('Controle de Planos', {
            'fields': ('disponivel_para_vagas', 'valor_base_por_vaga'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('empresa_contratante', 'tipo_funcao')


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


@admin.register(CategoriaFinanceira)
class CategoriaFinanceiraAdmin(admin.ModelAdmin, EmpresaContratanteMixin):
    list_display = ('nome', 'tipo', 'empresa_contratante', 'ativo', 'cor_display')
    list_filter = ('tipo', 'ativo', 'empresa_contratante')
    search_fields = ('nome', 'descricao')
    
    fieldsets = (
        ("Informações Básicas", {
            "fields": ("nome", "descricao", "tipo")
        }),
        ("Aparência", {
            "fields": ("cor",)
        }),
        ("Status", {
            "fields": ("ativo",)
        }),
    )
    
    def cor_display(self, obj):
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 3px;">{}</span>',
            obj.cor, obj.cor
        )
    cor_display.short_description = "Cor"


@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin, EmpresaContratanteMixin):
    list_display = ('nome_fantasia', 'tipo_fornecedor', 'cnpj', 'telefone', 'email', 'ativo', 'total_despesas_display')
    list_filter = ('tipo_fornecedor', 'ativo', 'empresa_contratante', 'data_cadastro')
    search_fields = ('nome_fantasia', 'razao_social', 'cnpj', 'email', 'telefone')
    readonly_fields = ('data_cadastro', 'data_atualizacao', 'total_despesas', 'despesas_pagas', 'despesas_pendentes')
    
    fieldsets = (
        ("Informações Básicas", {
            "fields": ("nome_fantasia", "razao_social", "cnpj", "tipo_fornecedor")
        }),
        ("Contato", {
            "fields": ("telefone", "email", "website")
        }),
        ("Endereço", {
            "fields": ("cep", "logradouro", "numero", "complemento", "bairro", "cidade", "uf")
        }),
        ("Informações Financeiras", {
            "fields": ("banco", "agencia", "conta", "pix")
        }),
        ("Observações", {
            "fields": ("observacoes",)
        }),
        ("Status", {
            "fields": ("ativo",)
        }),
        ("Timestamps", {
            "fields": ("data_cadastro", "data_atualizacao")
        }),
        ("Estatísticas", {
            "fields": ("total_despesas", "despesas_pagas", "despesas_pendentes")
        }),
    )
    
    def total_despesas_display(self, obj):
        return f"R$ {obj.total_despesas:,.2f}"
    total_despesas_display.short_description = "Total Despesas"


@admin.register(DespesaEvento)
class DespesaEventoAdmin(admin.ModelAdmin, EmpresaContratanteMixin):
    list_display = ('descricao', 'evento', 'categoria', 'valor', 'data_vencimento', 'status', 'fornecedor', 'atrasada_display')
    list_filter = ('status', 'categoria', 'data_vencimento', 'evento__empresa_contratante')
    search_fields = ('descricao', 'fornecedor', 'numero_documento', 'evento__nome')
    autocomplete_fields = ('evento', 'categoria', 'fornecedor')
    readonly_fields = ('data_criacao', 'data_atualizacao')
    
    fieldsets = (
        ("Evento e Categoria", {
            "fields": ("evento", "categoria")
        }),
        ("Informações da Despesa", {
            "fields": ("descricao", "valor", "fornecedor", "numero_documento")
        }),
        ("Datas", {
            "fields": ("data_vencimento", "data_pagamento")
        }),
        ("Status", {
            "fields": ("status",)
        }),
        ("Observações", {
            "fields": ("observacoes",)
        }),
        ("Timestamps", {
            "fields": ("data_criacao", "data_atualizacao")
        }),
    )
    
    def atrasada_display(self, obj):
        if obj.atrasada:
            return format_html(
                '<span style="color: red; font-weight: bold;">ATRASADA ({})</span>',
                f"{obj.dias_atraso} dias"
            )
        return "Em dia"
    atrasada_display.short_description = "Status de Vencimento"




@admin.register(ReceitaEvento)
class ReceitaEventoAdmin(admin.ModelAdmin, EmpresaContratanteMixin):
    list_display = ('descricao', 'evento', 'categoria', 'valor', 'data_vencimento', 'status', 'cliente', 'atrasada_display')
    list_filter = ('status', 'categoria', 'data_vencimento', 'evento__empresa_contratante')
    search_fields = ('descricao', 'cliente', 'numero_documento', 'evento__nome')
    autocomplete_fields = ('evento', 'categoria')
    readonly_fields = ('data_criacao', 'data_atualizacao')
    
    fieldsets = (
        ("Evento e Categoria", {
            "fields": ("evento", "categoria")
        }),
        ("Informações da Receita", {
            "fields": ("descricao", "valor", "cliente", "numero_documento")
        }),
        ("Datas", {
            "fields": ("data_vencimento", "data_recebimento")
        }),
        ("Status", {
            "fields": ("status",)
        }),
        ("Observações", {
            "fields": ("observacoes",)
        }),
        ("Timestamps", {
            "fields": ("data_criacao", "data_atualizacao")
        }),
    )
    
    def atrasada_display(self, obj):
        if obj.atrasada:
            return format_html(
                '<span style="color: red; font-weight: bold;">ATRASADA ({})</span>',
                f"{obj.dias_atraso} dias"
            )
        return "Em dia"
    atrasada_display.short_description = "Status de Vencimento"




