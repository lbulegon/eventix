"""
Admin para modelos globais do sistema
APENAS ADMINISTRADORES DO SISTEMA PODEM GERENCIAR
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models_globais import (
    CategoriaGlobal, TipoGlobal, ClassificacaoGlobal,
    ConfiguracaoSistema, ParametroSistema,
    IntegracaoGlobal, WebhookGlobal,
    TemplateGlobal,
    LogSistema, BackupGlobal,
    CategoriaFreelancerGlobal, HabilidadeGlobal, FornecedorGlobal
)
from .permissions.permissions_globais import (
    PodeGerenciarModelosGlobaisMixin,
    PodeGerenciarConfiguracoesMixin,
    PodeGerenciarLogsMixin,
    PodeGerenciarBackupsMixin,
    PodeGerenciarMarketplaceMixin
)


# ============================================================================
# CATÁLOGOS GERAIS
# ============================================================================

@admin.register(CategoriaGlobal)
class CategoriaGlobalAdmin(PodeGerenciarModelosGlobaisMixin, admin.ModelAdmin):
    list_display = ('nome', 'icone', 'cor_preview', 'ordem', 'ativo', 'data_criacao')
    list_filter = ('ativo', 'data_criacao')
    search_fields = ('nome', 'descricao')
    ordering = ('ordem', 'nome')
    readonly_fields = ('data_criacao', 'data_atualizacao')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'ativo')
        }),
        ('Aparência', {
            'fields': ('icone', 'cor', 'ordem')
        }),
        ('Metadados', {
            'fields': ('data_criacao', 'data_atualizacao', 'criado_por'),
            'classes': ('collapse',)
        }),
    )
    
    def cor_preview(self, obj):
        if obj.cor:
            return format_html(
                '<span style="display: inline-block; width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc;"></span> {}',
                obj.cor, obj.cor
            )
        return '-'
    cor_preview.short_description = 'Cor'


@admin.register(TipoGlobal)
class TipoGlobalAdmin(PodeGerenciarModelosGlobaisMixin, admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'codigo', 'ordem', 'ativo', 'data_criacao')
    list_filter = ('categoria', 'ativo', 'data_criacao')
    search_fields = ('nome', 'descricao', 'codigo')
    ordering = ('categoria', 'ordem', 'nome')
    readonly_fields = ('data_criacao', 'data_atualizacao')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('categoria', 'nome', 'descricao', 'codigo', 'ativo')
        }),
        ('Organização', {
            'fields': ('ordem',)
        }),
        ('Metadados', {
            'fields': ('data_criacao', 'data_atualizacao', 'criado_por'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ClassificacaoGlobal)
class ClassificacaoGlobalAdmin(PodeGerenciarModelosGlobaisMixin, admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'valor', 'cor_preview', 'ativo', 'data_criacao')
    list_filter = ('tipo', 'ativo', 'data_criacao')
    search_fields = ('nome', 'descricao', 'tipo')
    ordering = ('tipo', 'valor', 'nome')
    readonly_fields = ('data_criacao', 'data_atualizacao')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('tipo', 'nome', 'descricao', 'ativo')
        }),
        ('Valores', {
            'fields': ('valor', 'cor')
        }),
        ('Metadados', {
            'fields': ('data_criacao', 'data_atualizacao', 'criado_por'),
            'classes': ('collapse',)
        }),
    )
    
    def cor_preview(self, obj):
        if obj.cor:
            return format_html(
                '<span style="display: inline-block; width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc;"></span> {}',
                obj.cor, obj.cor
            )
        return '-'
    cor_preview.short_description = 'Cor'


# ============================================================================
# CONFIGURAÇÕES SISTEMA
# ============================================================================

@admin.register(ConfiguracaoSistema)
class ConfiguracaoSistemaAdmin(PodeGerenciarConfiguracoesMixin, admin.ModelAdmin):
    list_display = ('chave', 'valor', 'tipo', 'categoria', 'ativo', 'data_criacao')
    list_filter = ('tipo', 'categoria', 'ativo', 'data_criacao')
    search_fields = ('chave', 'valor', 'descricao')
    ordering = ('categoria', 'chave')
    readonly_fields = ('data_criacao', 'data_atualizacao')
    
    fieldsets = (
        ('Configuração', {
            'fields': ('chave', 'valor', 'tipo', 'descricao', 'categoria', 'ativo')
        }),
        ('Metadados', {
            'fields': ('data_criacao', 'data_atualizacao', 'criado_por'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ParametroSistema)
class ParametroSistemaAdmin(PodeGerenciarConfiguracoesMixin, admin.ModelAdmin):
    list_display = ('nome', 'valor_atual', 'tipo', 'categoria', 'editavel', 'ativo', 'data_criacao')
    list_filter = ('tipo', 'categoria', 'editavel', 'ativo', 'data_criacao')
    search_fields = ('nome', 'descricao')
    ordering = ('categoria', 'nome')
    readonly_fields = ('data_criacao', 'data_atualizacao')
    
    fieldsets = (
        ('Parâmetro', {
            'fields': ('nome', 'descricao', 'categoria', 'editavel', 'ativo')
        }),
        ('Valores', {
            'fields': ('tipo', 'valor_padrao', 'valor_atual')
        }),
        ('Metadados', {
            'fields': ('data_criacao', 'data_atualizacao', 'criado_por'),
            'classes': ('collapse',)
        }),
    )


# ============================================================================
# INTEGRAÇÕES
# ============================================================================

@admin.register(IntegracaoGlobal)
class IntegracaoGlobalAdmin(PodeGerenciarModelosGlobaisMixin, admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'url_base', 'ativo', 'data_criacao')
    list_filter = ('tipo', 'ativo', 'data_criacao')
    search_fields = ('nome', 'descricao', 'url_base')
    ordering = ('nome',)
    readonly_fields = ('data_criacao', 'data_atualizacao')
    
    fieldsets = (
        ('Integração', {
            'fields': ('nome', 'descricao', 'tipo', 'ativo')
        }),
        ('Configuração', {
            'fields': ('url_base', 'documentacao')
        }),
        ('Metadados', {
            'fields': ('data_criacao', 'data_atualizacao', 'criado_por'),
            'classes': ('collapse',)
        }),
    )


@admin.register(WebhookGlobal)
class WebhookGlobalAdmin(PodeGerenciarModelosGlobaisMixin, admin.ModelAdmin):
    list_display = ('integracao', 'evento', 'url', 'metodo', 'ativo', 'data_criacao')
    list_filter = ('integracao', 'metodo', 'ativo', 'data_criacao')
    search_fields = ('evento', 'url', 'integracao__nome')
    ordering = ('integracao', 'evento')
    readonly_fields = ('data_criacao', 'data_atualizacao')
    
    fieldsets = (
        ('Webhook', {
            'fields': ('integracao', 'evento', 'ativo')
        }),
        ('Configuração', {
            'fields': ('url', 'metodo', 'headers')
        }),
        ('Metadados', {
            'fields': ('data_criacao', 'data_atualizacao', 'criado_por'),
            'classes': ('collapse',)
        }),
    )


# ============================================================================
# TEMPLATES
# ============================================================================

@admin.register(TemplateGlobal)
class TemplateGlobalAdmin(PodeGerenciarModelosGlobaisMixin, admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'assunto', 'ativo', 'data_criacao')
    list_filter = ('tipo', 'ativo', 'data_criacao')
    search_fields = ('nome', 'assunto', 'conteudo')
    ordering = ('tipo', 'nome')
    readonly_fields = ('data_criacao', 'data_atualizacao')
    
    fieldsets = (
        ('Template', {
            'fields': ('nome', 'tipo', 'assunto', 'ativo')
        }),
        ('Conteúdo', {
            'fields': ('conteudo', 'variaveis')
        }),
        ('Metadados', {
            'fields': ('data_criacao', 'data_atualizacao', 'criado_por'),
            'classes': ('collapse',)
        }),
    )


# ============================================================================
# AUDITORIA
# ============================================================================

@admin.register(LogSistema)
class LogSistemaAdmin(PodeGerenciarLogsMixin, admin.ModelAdmin):
    list_display = ('nivel', 'mensagem_curta', 'modulo', 'funcao', 'data_criacao')
    list_filter = ('nivel', 'modulo', 'data_criacao')
    search_fields = ('mensagem', 'modulo', 'funcao')
    ordering = ('-data_criacao',)
    readonly_fields = ('data_criacao', 'data_atualizacao')
    
    fieldsets = (
        ('Log', {
            'fields': ('nivel', 'mensagem', 'modulo', 'funcao', 'linha')
        }),
        ('Dados Extras', {
            'fields': ('dados_extras',),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('data_criacao', 'data_atualizacao', 'criado_por'),
            'classes': ('collapse',)
        }),
    )
    
    def mensagem_curta(self, obj):
        return obj.mensagem[:50] + '...' if len(obj.mensagem) > 50 else obj.mensagem
    mensagem_curta.short_description = 'Mensagem'
    
    def has_add_permission(self, request):
        return False  # Logs são criados automaticamente


@admin.register(BackupGlobal)
class BackupGlobalAdmin(PodeGerenciarBackupsMixin, admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'tamanho_formatado', 'status', 'data_inicio', 'data_fim')
    list_filter = ('tipo', 'status', 'data_inicio')
    search_fields = ('nome', 'localizacao')
    ordering = ('-data_inicio',)
    readonly_fields = ('data_criacao', 'data_atualizacao')
    
    fieldsets = (
        ('Backup', {
            'fields': ('nome', 'tipo', 'status', 'ativo')
        }),
        ('Detalhes', {
            'fields': ('tamanho', 'localizacao', 'data_inicio', 'data_fim')
        }),
        ('Metadados', {
            'fields': ('data_criacao', 'data_atualizacao', 'criado_por'),
            'classes': ('collapse',)
        }),
    )
    
    def tamanho_formatado(self, obj):
        if obj.tamanho:
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if obj.tamanho < 1024.0:
                    return f"{obj.tamanho:.1f} {unit}"
                obj.tamanho /= 1024.0
        return '-'
    tamanho_formatado.short_description = 'Tamanho'


# ============================================================================
# MARKETPLACE
# ============================================================================

@admin.register(CategoriaFreelancerGlobal)
class CategoriaFreelancerGlobalAdmin(PodeGerenciarMarketplaceMixin, admin.ModelAdmin):
    list_display = ('nome', 'icone', 'cor_preview', 'ativo', 'data_criacao')
    list_filter = ('ativo', 'data_criacao')
    search_fields = ('nome', 'descricao')
    ordering = ('nome',)
    readonly_fields = ('data_criacao', 'data_atualizacao')
    
    fieldsets = (
        ('Categoria', {
            'fields': ('nome', 'descricao', 'ativo')
        }),
        ('Aparência', {
            'fields': ('icone', 'cor')
        }),
        ('Metadados', {
            'fields': ('data_criacao', 'data_atualizacao', 'criado_por'),
            'classes': ('collapse',)
        }),
    )
    
    def cor_preview(self, obj):
        if obj.cor:
            return format_html(
                '<span style="display: inline-block; width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc;"></span> {}',
                obj.cor, obj.cor
            )
        return '-'
    cor_preview.short_description = 'Cor'


@admin.register(HabilidadeGlobal)
class HabilidadeGlobalAdmin(PodeGerenciarMarketplaceMixin, admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'nivel_minimo', 'ativo', 'data_criacao')
    list_filter = ('categoria', 'nivel_minimo', 'ativo', 'data_criacao')
    search_fields = ('nome', 'descricao')
    ordering = ('categoria', 'nome')
    readonly_fields = ('data_criacao', 'data_atualizacao')
    
    fieldsets = (
        ('Habilidade', {
            'fields': ('categoria', 'nome', 'descricao', 'ativo')
        }),
        ('Requisitos', {
            'fields': ('nivel_minimo',)
        }),
        ('Metadados', {
            'fields': ('data_criacao', 'data_atualizacao', 'criado_por'),
            'classes': ('collapse',)
        }),
    )


@admin.register(FornecedorGlobal)
class FornecedorGlobalAdmin(PodeGerenciarMarketplaceMixin, admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'avaliacao_media', 'total_avaliacoes', 'ativo', 'data_criacao')
    list_filter = ('categoria', 'ativo', 'data_criacao')
    search_fields = ('nome', 'descricao', 'email', 'telefone')
    ordering = ('nome',)
    readonly_fields = ('data_criacao', 'data_atualizacao')
    
    fieldsets = (
        ('Fornecedor', {
            'fields': ('nome', 'descricao', 'categoria', 'ativo')
        }),
        ('Contato', {
            'fields': ('website', 'email', 'telefone', 'endereco')
        }),
        ('Avaliações', {
            'fields': ('avaliacao_media', 'total_avaliacoes')
        }),
        ('Metadados', {
            'fields': ('data_criacao', 'data_atualizacao', 'criado_por'),
            'classes': ('collapse',)
        }),
    )
