"""
Sistema de restrições para o admin do Django
Restringe acesso de usuários de empresa a tabelas genéricas
"""

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model

User = get_user_model()


class AdminRestricoesMixin:
    """
    Mixin para restringir acesso de usuários de empresa a tabelas genéricas
    """
    
    # Tabelas que apenas admin do sistema pode acessar
    TABELAS_RESTRITAS = [
        'EmpresaContratante',  # Apenas esta é restrita (informação sensível)
        'User',  # Lista de usuários
        'Group',  # Grupos do Django
        'Permission',  # Permissões do Django
        'ContentType',  # Tipos de conteúdo
        'Session',  # Sessões
        'LogEntry',  # Logs do admin
    ]
    
    # Tabelas genéricas que usuários de empresa podem ver mas não modificar
    TABELAS_GENERICAS_SOMENTE_LEITURA = [
        'PlanoContratacao',
        'TipoEmpresa',
        'Empresa',
        'LocalEvento',
        'TipoFuncao',
    ]
    
    def has_view_permission(self, request, obj=None):
        """Verifica se o usuário pode visualizar"""
        # Admin do sistema pode ver tudo
        if self._is_admin_sistema(request.user):
            return True
            
        # Para tabelas restritas, usuários de empresa não podem nem visualizar
        if self._is_tabela_restrita():
            return False
            
        # Para tabelas genéricas, usuários de empresa podem ver mas não modificar
        if self._is_tabela_generica_somente_leitura():
            return True
            
        # Para outras tabelas, verifica se é usuário de empresa
        if self._is_admin_empresa(request.user) or request.user.tipo_usuario == 'operador_empresa':
            return True
            
        # Comportamento padrão do Django
        return super().has_view_permission(request, obj)
    
    def has_add_permission(self, request):
        """Verifica se o usuário pode adicionar"""
        # Tabelas restritas: apenas admin do sistema
        if self._is_tabela_restrita() and not self._is_admin_sistema(request.user):
            return False
        # Tabelas genéricas: apenas admin do sistema
        if self._is_tabela_generica_somente_leitura() and not self._is_admin_sistema(request.user):
            return False
        return super().has_add_permission(request)
    
    def has_change_permission(self, request, obj=None):
        """Verifica se o usuário pode editar"""
        # Tabelas restritas: apenas admin do sistema
        if self._is_tabela_restrita() and not self._is_admin_sistema(request.user):
            return False
        # Tabelas genéricas: apenas admin do sistema
        if self._is_tabela_generica_somente_leitura() and not self._is_admin_sistema(request.user):
            return False
        return super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        """Verifica se o usuário pode deletar"""
        # Tabelas restritas: apenas admin do sistema
        if self._is_tabela_restrita() and not self._is_admin_sistema(request.user):
            return False
        # Tabelas genéricas: apenas admin do sistema
        if self._is_tabela_generica_somente_leitura() and not self._is_admin_sistema(request.user):
            return False
        return super().has_delete_permission(request, obj)
    
    def _is_tabela_restrita(self):
        """Verifica se esta é uma tabela restrita"""
        model_name = self.model.__name__
        return model_name in self.TABELAS_RESTRITAS
    
    def _is_tabela_generica_somente_leitura(self):
        """Verifica se esta é uma tabela genérica (somente leitura para usuários de empresa)"""
        model_name = self.model.__name__
        return model_name in self.TABELAS_GENERICAS_SOMENTE_LEITURA
    
    def _is_admin_sistema(self, user):
        """Verifica se o usuário é admin do sistema"""
        return user.tipo_usuario == 'admin_sistema'
    
    def _is_admin_empresa(self, user):
        """Verifica se o usuário é admin da empresa"""
        return user.tipo_usuario == 'admin_empresa'
    
    def changelist_view(self, request, extra_context=None):
        """Sobrescreve a view de listagem"""
        if self._is_tabela_restrita() and not self._is_admin_sistema(request.user):
            raise PermissionDenied("Você não tem permissão para acessar esta seção.")
        return super().changelist_view(request, extra_context)
    
    def add_view(self, request, form_url='', extra_context=None):
        """Sobrescreve a view de adição"""
        if self._is_tabela_restrita() and not self._is_admin_sistema(request.user):
            raise PermissionDenied("Você não tem permissão para acessar esta seção.")
        return super().add_view(request, form_url, extra_context)
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Sobrescreve a view de edição"""
        if self._is_tabela_restrita() and not self._is_admin_sistema(request.user):
            raise PermissionDenied("Você não tem permissão para acessar esta seção.")
        return super().change_view(request, object_id, form_url, extra_context)
    
    def delete_view(self, request, object_id, extra_context=None):
        """Sobrescreve a view de exclusão"""
        if self._is_tabela_restrita() and not self._is_admin_sistema(request.user):
            raise PermissionDenied("Você não tem permissão para acessar esta seção.")
        return super().delete_view(request, object_id, extra_context)


def aplicar_restricoes_admin():
    """
    Aplica as restrições aos admins existentes
    """
    # Importar todos os admins
    from app_eventos.admin import (
        PlanoContratacaoAdmin,
        EmpresaContratanteAdmin,
        TipoEmpresaAdmin,
        EmpresaAdmin,
        LocalEventoAdmin,
        TipoFuncaoAdmin,
        UserAdmin,
    )
    
    # Aplicar mixin aos admins restritos
    admin_classes_restritas = [
        PlanoContratacaoAdmin,
        EmpresaContratanteAdmin,
        TipoEmpresaAdmin,
        EmpresaAdmin,
        LocalEventoAdmin,
        TipoFuncaoAdmin,
        UserAdmin,
    ]
    
    for admin_class in admin_classes_restritas:
        if not issubclass(admin_class, AdminRestricoesMixin):
            # Adicionar o mixin dinamicamente
            admin_class.__bases__ = (AdminRestricoesMixin,) + admin_class.__bases__
