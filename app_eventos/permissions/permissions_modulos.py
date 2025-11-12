"""
Sistema de permissões para módulos do sistema Eventix
"""
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from django.core.exceptions import ObjectDoesNotExist


class TemModuloPermission(permissions.BasePermission):
    """
    Permission class para verificar se a empresa tem acesso a um módulo específico
    """
    
    def __init__(self, codigo_modulo):
        self.codigo_modulo = codigo_modulo
    
    def has_permission(self, request, view):
        """
        Verifica se o usuário tem permissão para acessar o módulo
        """
        # Admin do sistema sempre tem acesso
        if hasattr(request.user, 'is_admin_sistema') and request.user.is_admin_sistema:
            return True
        
        # Verifica se é usuário da empresa
        if not hasattr(request.user, 'is_empresa_user') or not request.user.is_empresa_user:
            return False
        
        # Verifica se tem empresa contratante
        try:
            empresa = request.user.empresa_contratante
            if not empresa:
                return False
            
            return empresa.tem_modulo(self.codigo_modulo)
        except (AttributeError, ObjectDoesNotExist):
            return False


def requer_modulo(codigo_modulo):
    """
    Decorator para views que requerem acesso a um módulo específico
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            # Admin do sistema sempre tem acesso
            if hasattr(request.user, 'is_admin_sistema') and request.user.is_admin_sistema:
                return view_func(request, *args, **kwargs)
            
            # Verifica se é usuário da empresa
            if not hasattr(request.user, 'is_empresa_user') or not request.user.is_empresa_user:
                from rest_framework.response import Response
                from rest_framework import status
                return Response(
                    {'detail': 'Você não tem permissão para acessar este recurso.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Verifica se tem empresa contratante
            try:
                empresa = request.user.empresa_contratante
                if not empresa:
                    from rest_framework.response import Response
                    from rest_framework import status
                    return Response(
                        {'detail': 'Empresa contratante não encontrada.'},
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                if not empresa.tem_modulo(codigo_modulo):
                    from rest_framework.response import Response
                    from rest_framework import status
                    from app_eventos.models import ModuloSistema
                    
                    try:
                        modulo = ModuloSistema.objects.get(codigo=codigo_modulo)
                        return Response(
                            {
                                'detail': f'Módulo "{modulo.nome}" não está contratado. Entre em contato para contratar este módulo.',
                                'modulo_requerido': codigo_modulo,
                                'modulo_nome': modulo.nome
                            },
                            status=status.HTTP_403_FORBIDDEN
                        )
                    except ModuloSistema.DoesNotExist:
                        return Response(
                            {'detail': f'Módulo "{codigo_modulo}" não encontrado.'},
                            status=status.HTTP_404_NOT_FOUND
                        )
                
                return view_func(request, *args, **kwargs)
            except (AttributeError, ObjectDoesNotExist):
                from rest_framework.response import Response
                from rest_framework import status
                return Response(
                    {'detail': 'Erro ao verificar permissões de módulo.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        return wrapper
    return decorator


class RequerModuloMixin:
    """
    Mixin para views que requerem acesso a um módulo específico
    Deve ser usado em conjunto com APIView ou outras views base
    """
    codigo_modulo = None
    
    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch para verificar permissões antes de processar a requisição
        """
        if not self.codigo_modulo:
            raise ValueError("codigo_modulo deve ser definido na view")
        
        # Admin do sistema sempre tem acesso
        if hasattr(request.user, 'is_admin_sistema') and request.user.is_admin_sistema:
            return super().dispatch(request, *args, **kwargs)
        
        # Verifica se é usuário da empresa
        if not hasattr(request.user, 'is_empresa_user') or not request.user.is_empresa_user:
            raise PermissionDenied('Você não tem permissão para acessar este recurso.')
        
        # Verifica se tem empresa contratante
        try:
            empresa = request.user.empresa_contratante
            if not empresa:
                raise PermissionDenied('Empresa contratante não encontrada.')
            
            if not empresa.tem_modulo(self.codigo_modulo):
                from app_eventos.models import ModuloSistema
                try:
                    modulo = ModuloSistema.objects.get(codigo=self.codigo_modulo)
                    raise PermissionDenied(
                        f'Módulo "{modulo.nome}" não está contratado. Entre em contato para contratar este módulo.'
                    )
                except ModuloSistema.DoesNotExist:
                    raise PermissionDenied(f'Módulo "{self.codigo_modulo}" não encontrado.')
            
            return super().dispatch(request, *args, **kwargs)
        except (AttributeError, ObjectDoesNotExist):
            raise PermissionDenied('Erro ao verificar permissões de módulo.')

