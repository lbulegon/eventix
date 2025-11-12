from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_eventos.models import Evento

from .models import Briefing
from .serializers import BriefingSerializer


class BriefingView(APIView):
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

        return get_object_or_404(queryset, pk=evento_id)

    def get(self, request, evento_id: int):
        evento = self.get_evento(request, evento_id)
        briefing = getattr(evento, "briefing", None)
        if not briefing:
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = BriefingSerializer(briefing)
        return Response(serializer.data)

    def post(self, request, evento_id: int):
        evento = self.get_evento(request, evento_id)
        if not self._can_edit(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        if hasattr(evento, "briefing"):
            return Response(
                {"detail": "Briefing já existe para este evento."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payload = request.data.copy()
        payload["evento"] = evento.id
        serializer = BriefingSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, evento_id: int):
        evento = self.get_evento(request, evento_id)
        if not self._can_edit(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        briefing = getattr(evento, "briefing", None)
        if not briefing:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = BriefingSerializer(briefing, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request, evento_id: int):
        evento = self.get_evento(request, evento_id)
        if not self._can_edit(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        briefing = getattr(evento, "briefing", None)
        if not briefing:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = BriefingSerializer(briefing, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @staticmethod
    def _can_edit(user) -> bool:
        return getattr(user, "is_empresa_user", False) or getattr(user, "is_admin_sistema", False)

