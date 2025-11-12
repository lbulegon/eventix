from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_eventos.models import Evento

from .models import MiseEnPlace
from .serializers import MiseEnPlaceSerializer


class MiseEnPlaceView(APIView):
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
        queryset = MiseEnPlace.objects.filter(evento=evento)
        serializer = MiseEnPlaceSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, evento_id: int):
        if not self._can_edit(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        evento = self.get_evento(request, evento_id)
        payload = request.data.copy()
        payload["evento"] = evento.id
        serializer = MiseEnPlaceSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def patch(self, request, evento_id: int):
        if not self._can_edit(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        evento = self.get_evento(request, evento_id)
        item_id = request.data.get("id")
        mise = get_object_or_404(MiseEnPlace, evento=evento, pk=item_id)

        serializer = MiseEnPlaceSerializer(mise, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @staticmethod
    def _can_edit(user) -> bool:
        return getattr(user, "is_empresa_user", False) or getattr(user, "is_admin_sistema", False)

