from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_eventos.models import Evento

from .models import FinalizacaoEvento
from .serializers import FinalizacaoEventoSerializer


class FinalizacaoEventoView(APIView):
    permission_classes = [IsAuthenticated]

    def get_evento(self, request, evento_id: int) -> Evento:
        queryset = Evento.objects.all()
        user = request.user
        if getattr(user, "is_empresa_user", False):
            queryset = queryset.filter(empresa_contratante=user.empresa_contratante)
        elif not getattr(user, "is_admin_sistema", False):
            queryset = queryset.filter(ativo=True)
        return get_object_or_404(queryset, pk=evento_id)

    def get(self, request, evento_id: int):
        evento = self.get_evento(request, evento_id)
        finalizacao, _ = FinalizacaoEvento.objects.get_or_create(evento=evento)
        serializer = FinalizacaoEventoSerializer(finalizacao)
        return Response(serializer.data)

    def patch(self, request, evento_id: int):
        if not self._can_edit(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        evento = self.get_evento(request, evento_id)
        finalizacao, _ = FinalizacaoEvento.objects.get_or_create(evento=evento)
        serializer = FinalizacaoEventoSerializer(finalizacao, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @staticmethod
    def _can_edit(user) -> bool:
        return getattr(user, "is_empresa_user", False) or getattr(user, "is_admin_sistema", False)

