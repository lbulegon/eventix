from decimal import Decimal

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_eventos.models import Evento

from .models import OrcamentoOperacional
from .serializers import OrcamentoOperacionalSerializer


class OrcamentoOperacionalView(APIView):
    permission_classes = [IsAuthenticated]

    def get_evento(self, request, evento_id: int) -> Evento:
        queryset = Evento.objects.all()
        user = request.user

        if getattr(user, "is_empresa_user", False):
            queryset = queryset.filter(empresa_contratante=user.empresa_contratante)
        elif getattr(user, "is_admin_sistema", False):
            queryset = queryset
        else:
            queryset = queryset.filter(ativo=True)

        return queryset.filter(pk=evento_id).first()

    def post(self, request, evento_id: int):
        evento = self.get_evento(request, evento_id)
        if not evento:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if not self._can_edit(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        subtotal = Decimal(request.data.get("subtotal", "0"))
        margem = Decimal(request.data.get("margem", "0"))
        lucro_minimo = Decimal(request.data.get("lucro_minimo", "0"))
        tipo_precificacao = request.data.get("tipo_precificacao", "percentual")
        detalhes_custos = request.data.get("detalhes_custos", {})

        percentual = margem / Decimal("100")
        total_percentual = subtotal * (Decimal("1") + percentual)

        if tipo_precificacao == "minimo":
            total = max(subtotal + lucro_minimo, total_percentual)
        else:
            total = total_percentual

        payload = {
            "evento": evento.id,
            "subtotal": subtotal,
            "margem": margem,
            "lucro_minimo": lucro_minimo,
            "total": total,
            "tipo_precificacao": tipo_precificacao,
            "detalhes_custos": detalhes_custos,
        }

        instance = getattr(evento, "orcamento_operacional", None)
        serializer = OrcamentoOperacionalSerializer(instance=instance, data=payload)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        status_code = status.HTTP_200_OK if instance else status.HTTP_201_CREATED
        return Response(serializer.data, status=status_code)

    @staticmethod
    def _can_edit(user) -> bool:
        return getattr(user, "is_empresa_user", False) or getattr(user, "is_admin_sistema", False)

