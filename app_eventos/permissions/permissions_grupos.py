# app_eventos/permissions/permissions_grupos.py
from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.contrib.auth.models import AnonymousUser


class TemPermissao(BasePermission):
    """
    Permissão baseada no sistema de grupos e permissões customizado
    """
    def __init__(self, codigo_permissao):
        self.codigo_permissao = codigo_permissao
    
    def has_permission(self, request, view):
        if isinstance(request.user, AnonymousUser):
            return False
        
        return request.user.tem_permissao(self.codigo_permissao)


class IsAdminSistema(BasePermission):
    """Verifica se o usuário é administrador do sistema"""
    def has_permission(self, request, view):
        if isinstance(request.user, AnonymousUser):
            return False
        return request.user.is_admin_sistema or request.user.is_superuser


class IsEmpresaUser(BasePermission):
    """Verifica se o usuário é da empresa (admin ou operador)"""
    def has_permission(self, request, view):
        if isinstance(request.user, AnonymousUser):
            return False
        return request.user.is_empresa_user or request.user.is_superuser


class IsFreelancer(BasePermission):
    """Verifica se o usuário é freelancer"""
    def has_permission(self, request, view):
        if isinstance(request.user, AnonymousUser):
            return False
        return request.user.is_freelancer or request.user.is_superuser


class IsOwnerOrReadOnly(BasePermission):
    """
    Permissão personalizada para permitir apenas que proprietários de um objeto o editem.
    """
    def has_object_permission(self, request, view, obj):
        # Permissões de leitura são concedidas para qualquer requisição,
        # então sempre permitiremos requisições GET, HEAD ou OPTIONS.
        if request.method in SAFE_METHODS:
            return True

        # Permissões de escrita são concedidas apenas ao proprietário do objeto.
        return obj.usuario == request.user


class IsEmpresaOwnerOrAdmin(BasePermission):
    """
    Permissão para verificar se o usuário é dono da empresa ou admin do sistema
    """
    def has_permission(self, request, view):
        if isinstance(request.user, AnonymousUser):
            return False
        
        if request.user.is_superuser or request.user.is_admin_sistema:
            return True
        
        return request.user.is_empresa_user
    
    def has_object_permission(self, request, view, obj):
        if isinstance(request.user, AnonymousUser):
            return False
        
        if request.user.is_superuser or request.user.is_admin_sistema:
            return True
        
        # Verifica se o objeto pertence à empresa do usuário
        if hasattr(obj, 'empresa_contratante'):
            return obj.empresa_contratante == request.user.empresa_contratante
        
        return False


class IsGrupoOwnerOrAdmin(BasePermission):
    """
    Permissão para verificar se o usuário pode gerenciar grupos
    """
    def has_permission(self, request, view):
        if isinstance(request.user, AnonymousUser):
            return False
        
        if request.user.is_superuser or request.user.is_admin_sistema:
            return True
        
        # Usuários de empresa podem gerenciar grupos da sua empresa
        if request.user.is_empresa_user:
            return request.user.pode_gerenciar_empresa
        
        return False
    
    def has_object_permission(self, request, view, obj):
        if isinstance(request.user, AnonymousUser):
            return False
        
        if request.user.is_superuser or request.user.is_admin_sistema:
            return True
        
        # Verifica se o grupo pertence à empresa do usuário
        if hasattr(obj, 'empresa_contratante'):
            return obj.empresa_contratante == request.user.empresa_contratante
        
        return False


class PermissaoCombinada(BasePermission):
    """
    Permissão que combina múltiplas verificações
    """
    def __init__(self, permissoes=None, operador='AND'):
        self.permissoes = permissoes or []
        self.operador = operador.upper()  # AND ou OR
    
    def has_permission(self, request, view):
        if isinstance(request.user, AnonymousUser):
            return False
        
        if not self.permissoes:
            return True
        
        resultados = []
        for permissao in self.permissoes:
            if isinstance(permissao, str):
                # Código de permissão
                resultados.append(request.user.tem_permissao(permissao))
            elif hasattr(permissao, 'has_permission'):
                # Classe de permissão
                resultados.append(permissao().has_permission(request, view))
            else:
                # Função
                resultados.append(permissao(request.user))
        
        if self.operador == 'AND':
            return all(resultados)
        else:  # OR
            return any(resultados)


# Permissões específicas do sistema
class PodeGerenciarUsuarios(BasePermission):
    def has_permission(self, request, view):
        if isinstance(request.user, AnonymousUser):
            return False
        return request.user.tem_permissao('gerenciar_usuarios')


class PodeGerenciarEventos(BasePermission):
    def has_permission(self, request, view):
        if isinstance(request.user, AnonymousUser):
            return False
        return request.user.tem_permissao('gerenciar_eventos')


class PodeGerenciarEquipamentos(BasePermission):
    def has_permission(self, request, view):
        if isinstance(request.user, AnonymousUser):
            return False
        return request.user.tem_permissao('gerenciar_equipamentos')


class PodeGerenciarFinanceiro(BasePermission):
    def has_permission(self, request, view):
        if isinstance(request.user, AnonymousUser):
            return False
        return request.user.tem_permissao('gerenciar_financeiro')


class PodeVisualizarRelatorios(BasePermission):
    def has_permission(self, request, view):
        if isinstance(request.user, AnonymousUser):
            return False
        return request.user.tem_permissao('visualizar_relatorios')


class PodeGerenciarFornecedores(BasePermission):
    def has_permission(self, request, view):
        if isinstance(request.user, AnonymousUser):
            return False
        return request.user.tem_permissao('gerenciar_fornecedores')


class PodeGerenciarFreelancers(BasePermission):
    def has_permission(self, request, view):
        if isinstance(request.user, AnonymousUser):
            return False
        return request.user.tem_permissao('gerenciar_freelancers')
