from rest_framework import serializers

from .models import InsightEvento


class InsightEventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsightEvento
        fields = [
            "id",
            "evento_base",
            "recomendacao",
            "relevancia",
            "criado_em",
        ]
        read_only_fields = ["id", "criado_em"]

