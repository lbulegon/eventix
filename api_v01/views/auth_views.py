from rest_framework import generics, permissions
from api_v01.serializers.auth_serializers import SignupFreelancerSerializer, SignupEmpresaSerializer
from app_eventos.models import User

class AllowAnyPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return True

class SignupFreelancerView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignupFreelancerSerializer
    permission_classes = [AllowAnyPermission]

class SignupEmpresaView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignupEmpresaSerializer
    permission_classes = [AllowAnyPermission]

