from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_eventos.models import Evento

from .models import InsightEvento
from .serializers import InsightEventoSerializer


class InsightEventoView(APIView):
    permission_classes = [IsAuthenticated]

    def get_evento(self, request, evento_id: int) -> Evento:
        queryset = Evento.objects.all()
        user = request.user
        if getattr(user, "is_empresa_user", False):
            queryset = queryset.filter(empresa_contratante=user.empresa_contratante)
        elif not getattr(user, "is_admin_sistema", False):
            queryset = queryset.filter(ativo=True)
        return queryset.filter(pk=evento_id).first()

    def get(self, request, evento_id: int):
        evento = self.get_evento(request, evento_id)
        if not evento:
            return Response(status=status.HTTP_404_NOT_FOUND)

        insights = InsightEvento.objects.filter(evento_base=evento)
        serializer = InsightEventoSerializer(insights, many=True)
        return Response(serializer.data)

    def post(self, request, evento_id: int):
        evento = self.get_evento(request, evento_id)
        if not evento:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if not self._can_edit(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        payload = request.data.copy()
        payload["evento_base"] = evento.id
        serializer = InsightEventoSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def _can_edit(user) -> bool:
        return getattr(user, "is_empresa_user", False) or getattr(user, "is_admin_sistema", False)

