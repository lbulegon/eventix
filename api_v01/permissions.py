from rest_framework import permissions

from app_eventos.utils_empresa_ativa import empresa_contexto_api, is_api_empresa_actor


class IsFreelancer(permissions.BasePermission):
    """
    Permissão para freelancers
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_freelancer


class IsEmpresaUser(permissions.BasePermission):
    """
    Permissão para utilizadores de empresa (admin/operador) ou gestor de grupo
    com contexto válido (cabeçalho ``X-Empresa-Context-Id``).
    """
    def has_permission(self, request, view):
        u = request.user
        if not u.is_authenticated:
            return False
        if getattr(u, 'is_empresa_user', False) and getattr(u, 'empresa_contratante', None):
            return True
        if getattr(u, 'is_gestor_grupo', False) and empresa_contexto_api(request) is not None:
            return True
        return False


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
    Permissão para freelancers ou utilizadores com escopo de empresa (inclui gestor + cabeçalho).
    """
    def has_permission(self, request, view):
        u = request.user
        return u.is_authenticated and (
            getattr(u, 'is_freelancer', False) or is_api_empresa_actor(request)
        )


class IsEmpresaOrAdminSistema(permissions.BasePermission):
    """
    Permissão para escopo empresa (inclui gestor + cabeçalho) ou administradores do sistema
    """
    def has_permission(self, request, view):
        u = request.user
        return u.is_authenticated and (
            getattr(u, 'is_admin_sistema', False) or is_api_empresa_actor(request)
        )


class IsOwnerOrEmpresa(permissions.BasePermission):
    """
    Permissão para dono do objeto ou usuário de empresa
    """
    def has_object_permission(self, request, view, obj):
        # Admin do sistema tem acesso total
        if request.user.is_admin_sistema:
            return True
        
        # Utilizadores com escopo empresa (inclui gestor + cabeçalho)
        if is_api_empresa_actor(request) and hasattr(obj, 'empresa_contratante'):
            emp = empresa_contexto_api(request)
            return emp is not None and obj.empresa_contratante == emp
        
        # Freelancers só podem acessar seus próprios objetos
        if request.user.is_freelancer and hasattr(obj, 'usuario'):
            return obj.usuario == request.user
        
        return False
