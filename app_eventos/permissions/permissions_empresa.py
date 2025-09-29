"""
Permissões específicas para administração privada por empresa
"""
from rest_framework.permissions import BasePermission
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages


class IsAdminEmpresa(BasePermission):
    """
    Permissão que verifica se o usuário é administrador da empresa
    """
    message = "Apenas administradores da empresa podem acessar esta funcionalidade."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin do sistema sempre tem acesso
        if request.user.is_admin_sistema:
            return True
            
        # Verifica se é admin da empresa
        if request.user.tipo_usuario == 'admin_empresa':
            return request.user.empresa_contratante and request.user.empresa_contratante.ativo
            
        return False


class PodeGerenciarUsuarios(BasePermission):
    """
    Permissão que verifica se o usuário pode gerenciar usuários da empresa
    """
    message = "Você não tem permissão para gerenciar usuários."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Admin do sistema sempre tem acesso
        if request.user.is_admin_sistema:
            return True
            
        # Verifica se tem permissão específica
        return request.user.pode_gerenciar_usuarios()


class PodeGerenciarEventos(BasePermission):
    """
    Permissão que verifica se o usuário pode gerenciar eventos
    """
    message = "Você não tem permissão para gerenciar eventos."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Admin do sistema sempre tem acesso
        if request.user.is_admin_sistema:
            return True
            
        # Verifica se tem permissão específica
        return request.user.pode_gerenciar_eventos()


class PodeGerenciarFreelancers(BasePermission):
    """
    Permissão que verifica se o usuário pode gerenciar freelancers
    """
    message = "Você não tem permissão para gerenciar freelancers."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Admin do sistema sempre tem acesso
        if request.user.is_admin_sistema:
            return True
            
        # Verifica se tem permissão específica
        return request.user.pode_gerenciar_freelancers()


class PodeGerenciarEquipamentos(BasePermission):
    """
    Permissão que verifica se o usuário pode gerenciar equipamentos
    """
    message = "Você não tem permissão para gerenciar equipamentos."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Admin do sistema sempre tem acesso
        if request.user.is_admin_sistema:
            return True
            
        # Verifica se tem permissão específica
        return request.user.pode_gerenciar_equipamentos()


class PodeGerenciarEstoque(BasePermission):
    """
    Permissão que verifica se o usuário pode gerenciar estoque
    """
    message = "Você não tem permissão para gerenciar estoque."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Admin do sistema sempre tem acesso
        if request.user.is_admin_sistema:
            return True
            
        # Verifica se tem permissão específica
        return request.user.pode_gerenciar_estoque()


class PodeGerenciarFinanceiro(BasePermission):
    """
    Permissão que verifica se o usuário pode gerenciar financeiro
    """
    message = "Você não tem permissão para acessar informações financeiras."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Admin do sistema sempre tem acesso
        if request.user.is_admin_sistema:
            return True
            
        # Verifica se tem permissão específica
        return request.user.pode_gerenciar_financeiro()


class PodeGerenciarRelatorios(BasePermission):
    """
    Permissão que verifica se o usuário pode gerar relatórios
    """
    message = "Você não tem permissão para gerar relatórios."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Admin do sistema sempre tem acesso
        if request.user.is_admin_sistema:
            return True
            
        # Verifica se tem permissão específica
        return request.user.pode_gerenciar_relatorios()


class PodeConfigurarSistema(BasePermission):
    """
    Permissão que verifica se o usuário pode configurar o sistema
    """
    message = "Você não tem permissão para configurar o sistema."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Admin do sistema sempre tem acesso
        if request.user.is_admin_sistema:
            return True
            
        # Verifica se tem permissão específica
        return request.user.pode_configurar_sistema()


# Mixins para views baseadas em classe
class AdminEmpresaRequiredMixin(UserPassesTestMixin):
    """
    Mixin que verifica se o usuário é administrador da empresa
    """
    
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_admin_sistema or 
            (user.tipo_usuario == 'admin_empresa' and user.empresa_contratante and user.empresa_contratante.ativo)
        )
    
    def handle_no_permission(self):
        messages.error(self.request, 'Apenas administradores da empresa podem acessar esta página.')
        return redirect('admin:index')


class PodeGerenciarUsuariosMixin(UserPassesTestMixin):
    """
    Mixin que verifica se o usuário pode gerenciar usuários
    """
    
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_admin_sistema or user.pode_gerenciar_usuarios()
        )
    
    def handle_no_permission(self):
        messages.error(self.request, 'Você não tem permissão para gerenciar usuários.')
        return redirect('admin:index')


class PodeGerenciarEventosMixin(UserPassesTestMixin):
    """
    Mixin que verifica se o usuário pode gerenciar eventos
    """
    
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_admin_sistema or user.pode_gerenciar_eventos()
        )
    
    def handle_no_permission(self):
        messages.error(self.request, 'Você não tem permissão para gerenciar eventos.')
        return redirect('admin:index')


class PodeGerenciarFreelancersMixin(UserPassesTestMixin):
    """
    Mixin que verifica se o usuário pode gerenciar freelancers
    """
    
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_admin_sistema or user.pode_gerenciar_freelancers()
        )
    
    def handle_no_permission(self):
        messages.error(self.request, 'Você não tem permissão para gerenciar freelancers.')
        return redirect('admin:index')


class PodeGerenciarEquipamentosMixin(UserPassesTestMixin):
    """
    Mixin que verifica se o usuário pode gerenciar equipamentos
    """
    
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_admin_sistema or user.pode_gerenciar_equipamentos()
        )
    
    def handle_no_permission(self):
        messages.error(self.request, 'Você não tem permissão para gerenciar equipamentos.')
        return redirect('admin:index')


class PodeGerenciarEstoqueMixin(UserPassesTestMixin):
    """
    Mixin que verifica se o usuário pode gerenciar estoque
    """
    
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_admin_sistema or user.pode_gerenciar_estoque()
        )
    
    def handle_no_permission(self):
        messages.error(self.request, 'Você não tem permissão para gerenciar estoque.')
        return redirect('admin:index')


class PodeGerenciarFinanceiroMixin(UserPassesTestMixin):
    """
    Mixin que verifica se o usuário pode gerenciar financeiro
    """
    
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_admin_sistema or user.pode_gerenciar_financeiro()
        )
    
    def handle_no_permission(self):
        messages.error(self.request, 'Você não tem permissão para acessar informações financeiras.')
        return redirect('admin:index')


class PodeGerenciarRelatoriosMixin(UserPassesTestMixin):
    """
    Mixin que verifica se o usuário pode gerar relatórios
    """
    
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_admin_sistema or user.pode_gerenciar_relatorios()
        )
    
    def handle_no_permission(self):
        messages.error(self.request, 'Você não tem permissão para gerar relatórios.')
        return redirect('admin:index')


class PodeConfigurarSistemaMixin(UserPassesTestMixin):
    """
    Mixin que verifica se o usuário pode configurar o sistema
    """
    
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_admin_sistema or user.pode_configurar_sistema()
        )
    
    def handle_no_permission(self):
        messages.error(self.request, 'Você não tem permissão para configurar o sistema.')
        return redirect('admin:index')

