from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_eventos.models import Evento

from .models import FichaTecnica, Menu, Prato
from .serializers import FichaTecnicaSerializer, MenuSerializer, PratoSerializer


class BaseEventoView(APIView):
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

    @staticmethod
    def can_edit(user) -> bool:
        return getattr(user, "is_empresa_user", False) or getattr(user, "is_admin_sistema", False)


class MenuListCreateView(BaseEventoView):
    def get(self, request, evento_id: int):
        evento = self.get_evento(request, evento_id)
        queryset = evento.menus.all()
        serializer = MenuSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, evento_id: int):
        if not self.can_edit(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)
        evento = self.get_evento(request, evento_id)
        payload = request.data.copy()
        payload["evento"] = evento.id
        serializer = MenuSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PratoListCreateView(BaseEventoView):
    def get(self, request, evento_id: int, menu_id: int):
        evento = self.get_evento(request, evento_id)
        menu = get_object_or_404(evento.menus.all(), pk=menu_id)
        serializer = PratoSerializer(menu.pratos.all(), many=True)
        return Response(serializer.data)

    def post(self, request, evento_id: int, menu_id: int):
        if not self.can_edit(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)
        evento = self.get_evento(request, evento_id)
        menu = get_object_or_404(evento.menus.all(), pk=menu_id)
        payload = request.data.copy()
        payload["menu"] = menu.id
        serializer = PratoSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FichaTecnicaListCreateView(BaseEventoView):
    def get(self, request, evento_id: int, menu_id: int, prato_id: int):
        evento = self.get_evento(request, evento_id)
        menu = get_object_or_404(evento.menus.all(), pk=menu_id)
        prato = get_object_or_404(menu.pratos.all(), pk=prato_id)
        serializer = FichaTecnicaSerializer(prato.fichas.all(), many=True)
        return Response(serializer.data)

    def post(self, request, evento_id: int, menu_id: int, prato_id: int):
        if not self.can_edit(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)
        evento = self.get_evento(request, evento_id)
        menu = get_object_or_404(evento.menus.all(), pk=menu_id)
        prato = get_object_or_404(menu.pratos.all(), pk=prato_id)
        payload = request.data.copy()
        payload["prato"] = prato.id
        serializer = FichaTecnicaSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

