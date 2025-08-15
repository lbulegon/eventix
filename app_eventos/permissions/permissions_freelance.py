from rest_framework.permissions import BasePermission
from rest_framework import permissions

class IsCadastroCompleto(BasePermission):
    """
    Permissão que garante que o freelancer só acesse o endpoint
    se o cadastro estiver completo (cadastro_completo=True).
    """
    message = "Complete seu cadastro para receber ofertas de vagas."

    def has_permission(self, request, view):
        # O usuário precisa estar autenticado
        if not request.user or not request.user.is_authenticated:
            return False

        # Verifica se existe perfil de freelancer vinculado
        try:
            freelance = request.user.freelance
        except AttributeError:
            return False

        # Retorna True apenas se cadastro_completo for True
        return freelance.cadastro_completo is True
