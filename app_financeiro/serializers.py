from decimal import Decimal

from rest_framework import serializers

from .models import OrcamentoOperacional


class OrcamentoOperacionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrcamentoOperacional
        fields = [
            "id",
            "evento",
            "subtotal",
            "margem",
            "lucro_minimo",
            "total",
            "tipo_precificacao",
            "data_calculo",
            "detalhes_custos",
        ]
        read_only_fields = ["id", "data_calculo"]

    def validate(self, attrs):
        subtotal = attrs.get("subtotal", Decimal("0"))
        margem = attrs.get("margem", Decimal("0"))
        total = attrs.get("total", Decimal("0"))

        if subtotal < 0:
            raise serializers.ValidationError({"subtotal": "Subtotal deve ser não-negativo."})
        if margem < 0:
            raise serializers.ValidationError({"margem": "Margem deve ser não-negativa."})
        if total < 0:
            raise serializers.ValidationError({"total": "Total deve ser não-negativo."})
        return attrs

