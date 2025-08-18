# api_v01/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminSistema(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and getattr(u, "is_admin_sistema", False))

class IsEmpresaUser(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and getattr(u, "is_empresa_user", False))

class IsFreelancer(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and getattr(u, "is_freelancer", False))
