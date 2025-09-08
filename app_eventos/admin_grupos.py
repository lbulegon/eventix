# app_eventos/admin_grupos.py
from django.contrib import admin
from django.utils.html import format_html
from .models import PermissaoSistema, GrupoUsuario, UsuarioGrupo
from .mixins import EmpresaContratanteMixin


@admin.register(PermissaoSistema)
class PermissaoSistemaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome', 'modulo', 'ativo')
    list_filter = ('modulo', 'ativo')
    search_fields = ('codigo', 'nome', 'descricao')
    readonly_fields = ('codigo',)
    
    fieldsets = (
        ("Informações Básicas", {
            "fields": ("codigo", "nome", "descricao", "modulo")
        }),
        ("Status", {
            "fields": ("ativo",)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        # Não permite editar o código após criação
        if obj:
            return self.readonly_fields + ('codigo',)
        return self.readonly_fields


@admin.register(GrupoUsuario)
class GrupoUsuarioAdmin(admin.ModelAdmin, EmpresaContratanteMixin):
    list_display = ('nome', 'tipo_grupo', 'empresa_contratante', 'ativo', 'total_permissoes', 'total_usuarios')
    list_filter = ('tipo_grupo', 'ativo', 'empresa_contratante')
    search_fields = ('nome', 'descricao')
    filter_horizontal = ('permissoes',)
    readonly_fields = ('data_criacao', 'data_atualizacao')
    
    fieldsets = (
        ("Informações Básicas", {
            "fields": ("nome", "descricao", "tipo_grupo")
        }),
        ("Empresa", {
            "fields": ("empresa_contratante",)
        }),
        ("Permissões", {
            "fields": ("permissoes",)
        }),
        ("Status", {
            "fields": ("ativo",)
        }),
        ("Timestamps", {
            "fields": ("data_criacao", "data_atualizacao")
        }),
    )
    
    def total_permissoes(self, obj):
        return obj.permissoes.count()
    total_permissoes.short_description = "Total de Permissões"
    
    def total_usuarios(self, obj):
        return obj.usuarios_grupo.filter(ativo=True).count()
    total_usuarios.short_description = "Total de Usuários"


@admin.register(UsuarioGrupo)
class UsuarioGrupoAdmin(admin.ModelAdmin, EmpresaContratanteMixin):
    list_display = ('usuario', 'grupo', 'empresa_grupo', 'ativo', 'data_entrada')
    list_filter = ('ativo', 'grupo__tipo_grupo', 'grupo__empresa_contratante', 'data_entrada')
    search_fields = ('usuario__username', 'usuario__email', 'grupo__nome')
    autocomplete_fields = ('usuario', 'grupo')
    readonly_fields = ('data_entrada',)
    
    fieldsets = (
        ("Relacionamento", {
            "fields": ("usuario", "grupo")
        }),
        ("Status", {
            "fields": ("ativo",)
        }),
        ("Timestamps", {
            "fields": ("data_entrada",)
        }),
    )
    
    def empresa_grupo(self, obj):
        return obj.grupo.empresa_contratante.nome_fantasia if obj.grupo.empresa_contratante else 'Sistema'
    empresa_grupo.short_description = "Empresa do Grupo"
