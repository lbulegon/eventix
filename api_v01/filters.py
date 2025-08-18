# api_v01/filters.py
from rest_framework import filters

class EmpresaScopeFilterBackend(filters.BaseFilterBackend):
    """
    Restringe querysets por empresa_contratante do usuário empresa.
    Admin sistema vê tudo. Freelancer normalmente não passa por este filtro.
    """
    def filter_queryset(self, request, queryset, view):
        user = request.user
        if not user.is_authenticated:
            return queryset.none()
        if getattr(user, "is_admin_sistema", False):
            return queryset
        if getattr(user, "is_empresa_user", False):
            # campo padrão 'empresa_contratante' nos models multi-tenant
            if hasattr(queryset.model, "empresa_contratante"):
                return queryset.filter(empresa_contratante=user.empresa_contratante)
        return queryset
