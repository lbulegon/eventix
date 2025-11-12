from rest_framework import serializers

from .models import OperacaoEvento


class OperacaoEventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperacaoEvento
        fields = [
            "id",
            "evento",
            "inicio_real",
            "fim_real",
            "status",
            "timeline",
        ]
        read_only_fields = ["id"]

