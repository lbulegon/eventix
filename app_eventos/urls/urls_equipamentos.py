from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app_eventos.views.views_equipamentos import (
    CategoriaEquipamentoViewSet, EquipamentoViewSet, 
    EquipamentoSetorViewSet, ManutencaoEquipamentoViewSet
)

router = DefaultRouter()
router.register(r'categorias', CategoriaEquipamentoViewSet)
router.register(r'equipamentos', EquipamentoViewSet)
router.register(r'equipamentos-setor', EquipamentoSetorViewSet)
router.register(r'manutencoes', ManutencaoEquipamentoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
