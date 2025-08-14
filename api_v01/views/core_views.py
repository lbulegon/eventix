from rest_framework import generics, permissions, status
from rest_framework.response import Response
from app_eventos.models import (
    Empresa, EmpresaUser, Evento, Setor, Funcao, Vaga, Candidatura, AlocacaoFinal
)
from api_v01.serializers.core_serializers import (
    EmpresaSerializer, EventoSerializer, SetorSerializer, FuncaoSerializer, VagaSerializer,
    CandidaturaCreateSerializer, CandidaturaListSerializer, CandidaturaUpdateStatusSerializer,
    AlocacaoFinalSerializer
)

# Permissões simples por papel
class IsFreelancer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "FREELANCER"

class IsEmpregador(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "EMPREGADOR"


# --- CRUD básico (pode restringir por empresa conforme necessário) ---
class EventoCreateView(generics.CreateAPIView):
    serializer_class = EventoSerializer
    permission_classes = [IsEmpregador]

class VagaCreateView(generics.CreateAPIView):
    serializer_class = VagaSerializer
    permission_classes = [IsEmpregador]

class VagaListByEventoView(generics.ListAPIView):
    serializer_class = VagaSerializer
    permission_classes = [permissions.AllowAny]  # aberto para consulta pública se desejar

    def get_queryset(self):
        evento_id = self.kwargs["evento_id"]
        return Vaga.objects.filter(setor__evento_id=evento_id, status="aberta")


# --- Candidatura (freelancer se candidata) ---
class CandidatarVagaView(generics.CreateAPIView):
    serializer_class = CandidaturaCreateSerializer
    permission_classes = [IsFreelancer]


class MinhasCandidaturasView(generics.ListAPIView):
    serializer_class = CandidaturaListSerializer
    permission_classes = [IsFreelancer]

    def get_queryset(self):
        return Candidatura.objects.filter(user=self.request.user).select_related("vaga")


# --- Empresa aceita/recusa candidatura e aloca ---
class CandidaturaUpdateStatusView(generics.UpdateAPIView):
    queryset = Candidatura.objects.all()
    serializer_class = CandidaturaUpdateStatusSerializer
    permission_classes = [IsEmpregador]


class CriarAlocacaoView(generics.CreateAPIView):
    serializer_class = AlocacaoFinalSerializer
    permission_classes = [IsEmpregador]
