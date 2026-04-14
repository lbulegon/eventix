# api_v01/filters.py
from rest_framework import filters

from app_eventos.utils_empresa_ativa import empresa_contexto_api


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
        emp = empresa_contexto_api(request)
        if emp and hasattr(queryset.model, "empresa_contratante"):
            return queryset.filter(empresa_contratante=emp)
        return queryset
