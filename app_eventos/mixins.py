from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from django.db import DatabaseError


class EmpresaContratanteMixin:
    """
    Mixin para filtrar querysets por empresa contratante
    """
    
    def get_queryset(self):
        try:
            queryset = super().get_queryset()
            
            # Admin do sistema vê tudo
            if self.request.user.tipo_usuario == 'admin_sistema':
                return queryset
                
            # Freelancers só veem seu próprio perfil
            if self.request.user.tipo_usuario == 'freelancer':
                if hasattr(self.model, 'usuario'):
                    return queryset.filter(usuario=self.request.user)
                return queryset.none()
                
            # Usuários da empresa veem apenas dados da sua empresa
            if hasattr(self.request.user, 'empresa_contratante') and self.request.user.empresa_contratante:
                empresa = self.request.user.empresa_contratante
                
                # Filtra por empresa_contratante se o modelo tem esse campo
                if hasattr(self.model, 'empresa_contratante'):
                    return queryset.filter(empresa_contratante=empresa)
                    
                # Para freelancers, filtra por candidaturas/contratos da empresa
                if self.model.__name__ == 'Freelance':
                    from app_eventos.models import Candidatura, ContratoFreelance
                    candidaturas = Candidatura.objects.filter(
                        vaga__setor__evento__empresa_contratante=empresa
                    ).values_list('freelance_id', flat=True)
                    contratos = ContratoFreelance.objects.filter(
                        vaga__setor__evento__empresa_contratante=empresa
                    ).values_list('freelance_id', flat=True)
                    return queryset.filter(id__in=list(candidaturas) + list(contratos))
                    
            return queryset.none()
            
        except DatabaseError:
            # Se há erro de banco, retorna queryset vazio
            return self.model.objects.none()
        except Exception:
            # Se há qualquer outro erro, retorna queryset vazio
            return self.model.objects.none()


class EmpresaContratanteRequiredMixin(UserPassesTestMixin):
    """
    Mixin para verificar se o usuário tem empresa contratante
    """
    
    def test_func(self):
        try:
            user = self.request.user
            
            # Admin do sistema sempre tem acesso
            if user.tipo_usuario == 'admin_sistema':
                return True
                
            # Freelancers podem acessar seu próprio perfil
            if user.tipo_usuario == 'freelancer':
                return True
                
            # Usuários da empresa precisam ter empresa contratante ativa
            if hasattr(user, 'empresa_contratante') and user.empresa_contratante:
                return user.empresa_contratante.ativo and user.ativo
                
            return False
            
        except Exception:
            return False
    
    def handle_no_permission(self):
        messages.error(self.request, 'Você não tem permissão para acessar esta página.')
        return redirect('admin:index')


class AdminEmpresaRequiredMixin(UserPassesTestMixin):
    """
    Mixin para verificar se o usuário é admin da empresa
    """
    
    def test_func(self):
        try:
            user = self.request.user
            
            # Admin do sistema sempre tem acesso
            if user.tipo_usuario == 'admin_sistema':
                return True
                
            # Admin da empresa tem acesso
            if user.tipo_usuario == 'admin_empresa':
                return hasattr(user, 'empresa_contratante') and user.empresa_contratante and user.empresa_contratante.ativo
                
            return False
            
        except Exception:
            return False
    
    def handle_no_permission(self):
        messages.error(self.request, 'Apenas administradores podem acessar esta página.')
        return redirect('admin:index')


class OperadorEmpresaRequiredMixin(UserPassesTestMixin):
    """
    Mixin para verificar se o usuário pode operar o sistema
    """
    
    def test_func(self):
        try:
            user = self.request.user
            
            # Admin do sistema sempre tem acesso
            if user.tipo_usuario == 'admin_sistema':
                return True
                
            # Admin e operador da empresa têm acesso
            if user.tipo_usuario in ['admin_empresa', 'operador_empresa']:
                return hasattr(user, 'empresa_contratante') and user.empresa_contratante and user.empresa_contratante.ativo
                
            return False
            
        except Exception:
            return False
    
    def handle_no_permission(self):
        messages.error(self.request, 'Você não tem permissão para operar o sistema.')
        return redirect('admin:index')
