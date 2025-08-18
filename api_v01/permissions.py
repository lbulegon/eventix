from rest_framework import permissions


class IsFreelancer(permissions.BasePermission):
    """
    Permissão para freelancers
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_freelancer


class IsEmpresaUser(permissions.BasePermission):
    """
    Permissão para usuários de empresa (admin ou operador)
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_empresa_user


class IsAdminSistema(permissions.BasePermission):
    """
    Permissão para administradores do sistema
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin_sistema


class IsEmpresaAdmin(permissions.BasePermission):
    """
    Permissão para administradores de empresa
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.tipo_usuario == 'admin_empresa'


class IsEmpresaOperador(permissions.BasePermission):
    """
    Permissão para operadores de empresa
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.tipo_usuario == 'operador_empresa'


class IsFreelancerOrEmpresa(permissions.BasePermission):
    """
    Permissão para freelancers ou usuários de empresa
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_freelancer or request.user.is_empresa_user
        )


class IsEmpresaOrAdminSistema(permissions.BasePermission):
    """
    Permissão para usuários de empresa ou administradores do sistema
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_empresa_user or request.user.is_admin_sistema
        )


class IsOwnerOrEmpresa(permissions.BasePermission):
    """
    Permissão para dono do objeto ou usuário de empresa
    """
    def has_object_permission(self, request, view, obj):
        # Admin do sistema tem acesso total
        if request.user.is_admin_sistema:
            return True
        
        # Usuários de empresa podem acessar objetos da sua empresa
        if request.user.is_empresa_user and hasattr(obj, 'empresa_contratante'):
            return obj.empresa_contratante == request.user.empresa_contratante
        
        # Freelancers só podem acessar seus próprios objetos
        if request.user.is_freelancer and hasattr(obj, 'usuario'):
            return obj.usuario == request.user
        
        return False
