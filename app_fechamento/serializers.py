from rest_framework import serializers

from .models import FechamentoInterno


class FechamentoInternoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FechamentoInterno
        fields = [
            "id",
            "evento",
            "perdas",
            "extravios",
            "custo_real",
            "lucro_liquido",
            "aprendizado",
            "indicadores",
            "criado_em",
        ]
        read_only_fields = ["id", "criado_em"]

