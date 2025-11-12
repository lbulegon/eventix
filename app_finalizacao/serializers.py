from rest_framework import serializers

from .models import FinalizacaoEvento


class FinalizacaoEventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinalizacaoEvento
        fields = [
            "id",
            "evento",
            "hora_extra",
            "observacoes",
            "fechamento_bebidas",
            "materiais_recolhidos",
        ]
        read_only_fields = ["id"]

