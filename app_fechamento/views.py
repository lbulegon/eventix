from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_eventos.models import Evento

from .models import FechamentoInterno
from .serializers import FechamentoInternoSerializer


class FechamentoInternoView(APIView):
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
        fechamento, _ = FechamentoInterno.objects.get_or_create(evento=evento, defaults={"custo_real": 0, "lucro_liquido": 0})
        serializer = FechamentoInternoSerializer(fechamento)
        return Response(serializer.data)

    def patch(self, request, evento_id: int):
        if not self._can_edit(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        evento = self.get_evento(request, evento_id)
        fechamento, created = FechamentoInterno.objects.get_or_create(
            evento=evento,
            defaults={
                "perdas": request.data.get("perdas", 0),
                "extravios": request.data.get("extravios", 0),
                "custo_real": request.data.get("custo_real", 0),
                "lucro_liquido": request.data.get("lucro_liquido", 0),
                "aprendizado": request.data.get("aprendizado", ""),
                "indicadores": request.data.get("indicadores", {}),
            },
        )

        if created:
            serializer = FechamentoInternoSerializer(fechamento)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        serializer = FechamentoInternoSerializer(fechamento, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @staticmethod
    def _can_edit(user) -> bool:
        return getattr(user, "is_empresa_user", False) or getattr(user, "is_admin_sistema", False)

