"""
Permissões específicas para modelos globais do sistema
"""
from rest_framework.permissions import BasePermission
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages


class PodeVerModelosGlobais(BasePermission):
    """
    Permissão que verifica se o usuário pode visualizar modelos globais
    """
    message = "Você não tem permissão para visualizar este conteúdo."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin do sistema sempre tem acesso total
        if request.user.is_admin_sistema:
            return True
            
        # Usuários de empresa podem visualizar modelos globais
        if request.user.is_empresa_user and request.user.empresa_contratante:
            return True
            
        return False


class PodeGerenciarModelosGlobais(BasePermission):
    """
    Permissão que verifica se o usuário pode gerenciar modelos globais
    APENAS ADMINISTRADORES DO SISTEMA
    """
    message = "Apenas administradores do sistema podem gerenciar este conteúdo."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # APENAS admin do sistema pode gerenciar modelos globais
        return request.user.is_admin_sistema


class PodeVerConfiguracoesSistema(BasePermission):
    """
    Permissão que verifica se o usuário pode visualizar configurações do sistema
    """
    message = "Você não tem permissão para visualizar configurações do sistema."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin do sistema sempre tem acesso
        if request.user.is_admin_sistema:
            return True
            
        # Admin da empresa pode ver algumas configurações
        if request.user.tipo_usuario == 'admin_empresa':
            return request.user.empresa_contratante and request.user.empresa_contratante.ativo
            
        return False


class PodeGerenciarConfiguracoesSistema(BasePermission):
    """
    Permissão que verifica se o usuário pode gerenciar configurações do sistema
    APENAS ADMINISTRADORES DO SISTEMA
    """
    message = "Apenas administradores do sistema podem gerenciar configurações."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # APENAS admin do sistema pode gerenciar configurações
        return request.user.is_admin_sistema


class PodeVerIntegracoes(BasePermission):
    """
    Permissão que verifica se o usuário pode visualizar integrações
    """
    message = "Você não tem permissão para visualizar integrações."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin do sistema sempre tem acesso
        if request.user.is_admin_sistema:
            return True
            
        # Usuários de empresa podem ver integrações disponíveis
        if request.user.is_empresa_user and request.user.empresa_contratante:
            return True
            
        return False


class PodeGerenciarIntegracoes(BasePermission):
    """
    Permissão que verifica se o usuário pode gerenciar integrações
    APENAS ADMINISTRADORES DO SISTEMA
    """
    message = "Apenas administradores do sistema podem gerenciar integrações."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # APENAS admin do sistema pode gerenciar integrações
        return request.user.is_admin_sistema


class PodeVerTemplates(BasePermission):
    """
    Permissão que verifica se o usuário pode visualizar templates
    """
    message = "Você não tem permissão para visualizar templates."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin do sistema sempre tem acesso
        if request.user.is_admin_sistema:
            return True
            
        # Usuários de empresa podem ver templates disponíveis
        if request.user.is_empresa_user and request.user.empresa_contratante:
            return True
            
        return False


class PodeGerenciarTemplates(BasePermission):
    """
    Permissão que verifica se o usuário pode gerenciar templates
    APENAS ADMINISTRADORES DO SISTEMA
    """
    message = "Apenas administradores do sistema podem gerenciar templates."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # APENAS admin do sistema pode gerenciar templates
        return request.user.is_admin_sistema


class PodeVerLogsSistema(BasePermission):
    """
    Permissão que verifica se o usuário pode visualizar logs do sistema
    """
    message = "Você não tem permissão para visualizar logs do sistema."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # APENAS admin do sistema pode ver logs
        return request.user.is_admin_sistema


class PodeGerenciarLogsSistema(BasePermission):
    """
    Permissão que verifica se o usuário pode gerenciar logs do sistema
    APENAS ADMINISTRADORES DO SISTEMA
    """
    message = "Apenas administradores do sistema podem gerenciar logs."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # APENAS admin do sistema pode gerenciar logs
        return request.user.is_admin_sistema


class PodeVerBackups(BasePermission):
    """
    Permissão que verifica se o usuário pode visualizar backups
    """
    message = "Você não tem permissão para visualizar backups."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # APENAS admin do sistema pode ver backups
        return request.user.is_admin_sistema


class PodeGerenciarBackups(BasePermission):
    """
    Permissão que verifica se o usuário pode gerenciar backups
    APENAS ADMINISTRADORES DO SISTEMA
    """
    message = "Apenas administradores do sistema podem gerenciar backups."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # APENAS admin do sistema pode gerenciar backups
        return request.user.is_admin_sistema


class PodeVerMarketplace(BasePermission):
    """
    Permissão que verifica se o usuário pode visualizar marketplace
    """
    message = "Você não tem permissão para visualizar o marketplace."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin do sistema sempre tem acesso
        if request.user.is_admin_sistema:
            return True
            
        # Usuários de empresa podem ver marketplace
        if request.user.is_empresa_user and request.user.empresa_contratante:
            return True
            
        return False


class PodeGerenciarMarketplace(BasePermission):
    """
    Permissão que verifica se o usuário pode gerenciar marketplace
    APENAS ADMINISTRADORES DO SISTEMA
    """
    message = "Apenas administradores do sistema podem gerenciar o marketplace."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # APENAS admin do sistema pode gerenciar marketplace
        return request.user.is_admin_sistema


# ============================================================================
# MIXINS PARA VIEWS
# ============================================================================

class PodeVerModelosGlobaisMixin(UserPassesTestMixin):
    """
    Mixin que verifica se o usuário pode visualizar modelos globais
    """
    
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_admin_sistema or 
            (user.is_empresa_user and user.empresa_contratante)
        )
    
    def handle_no_permission(self):
        messages.error(self.request, 'Você não tem permissão para visualizar este conteúdo.')
        return redirect('admin:index')


class PodeGerenciarModelosGlobaisMixin(UserPassesTestMixin):
    """
    Mixin que verifica se o usuário pode gerenciar modelos globais
    APENAS ADMINISTRADORES DO SISTEMA
    """
    
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.is_admin_sistema
    
    def handle_no_permission(self):
        messages.error(self.request, 'Apenas administradores do sistema podem gerenciar este conteúdo.')
        return redirect('admin:index')


class PodeVerConfiguracoesMixin(UserPassesTestMixin):
    """
    Mixin que verifica se o usuário pode visualizar configurações
    """
    
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_admin_sistema or 
            (user.tipo_usuario == 'admin_empresa' and user.empresa_contratante and user.empresa_contratante.ativo)
        )
    
    def handle_no_permission(self):
        messages.error(self.request, 'Você não tem permissão para visualizar configurações.')
        return redirect('admin:index')


class PodeGerenciarConfiguracoesMixin(UserPassesTestMixin):
    """
    Mixin que verifica se o usuário pode gerenciar configurações
    APENAS ADMINISTRADORES DO SISTEMA
    """
    
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.is_admin_sistema
    
    def handle_no_permission(self):
        messages.error(self.request, 'Apenas administradores do sistema podem gerenciar configurações.')
        return redirect('admin:index')


class PodeVerLogsMixin(UserPassesTestMixin):
    """
    Mixin que verifica se o usuário pode visualizar logs
    APENAS ADMINISTRADORES DO SISTEMA
    """
    
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.is_admin_sistema
    
    def handle_no_permission(self):
        messages.error(self.request, 'Apenas administradores do sistema podem visualizar logs.')
        return redirect('admin:index')


class PodeGerenciarLogsMixin(UserPassesTestMixin):
    """
    Mixin que verifica se o usuário pode gerenciar logs
    APENAS ADMINISTRADORES DO SISTEMA
    """
    
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.is_admin_sistema
    
    def handle_no_permission(self):
        messages.error(self.request, 'Apenas administradores do sistema podem gerenciar logs.')
        return redirect('admin:index')


class PodeVerBackupsMixin(UserPassesTestMixin):
    """
    Mixin que verifica se o usuário pode visualizar backups
    APENAS ADMINISTRADORES DO SISTEMA
    """
    
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.is_admin_sistema
    
    def handle_no_permission(self):
        messages.error(self.request, 'Apenas administradores do sistema podem visualizar backups.')
        return redirect('admin:index')


class PodeGerenciarBackupsMixin(UserPassesTestMixin):
    """
    Mixin que verifica se o usuário pode gerenciar backups
    APENAS ADMINISTRADORES DO SISTEMA
    """
    
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.is_admin_sistema
    
    def handle_no_permission(self):
        messages.error(self.request, 'Apenas administradores do sistema podem gerenciar backups.')
        return redirect('admin:index')


class PodeVerMarketplaceMixin(UserPassesTestMixin):
    """
    Mixin que verifica se o usuário pode visualizar marketplace
    """
    
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_admin_sistema or 
            (user.is_empresa_user and user.empresa_contratante)
        )
    
    def handle_no_permission(self):
        messages.error(self.request, 'Você não tem permissão para visualizar o marketplace.')
        return redirect('admin:index')


class PodeGerenciarMarketplaceMixin(UserPassesTestMixin):
    """
    Mixin que verifica se o usuário pode gerenciar marketplace
    APENAS ADMINISTRADORES DO SISTEMA
    """
    
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.is_admin_sistema
    
    def handle_no_permission(self):
        messages.error(self.request, 'Apenas administradores do sistema podem gerenciar o marketplace.')
        return redirect('admin:index')

