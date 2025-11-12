from rest_framework import serializers

from .models import Briefing


class BriefingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Briefing
        fields = [
            "id",
            "evento",
            "proposito",
            "experiencia_desejada",
            "tipo_servico",
            "publico_estimado",
            "restricoes_alimentares",
            "orcamento_disponivel",
            "infraestrutura_local",
            "observacoes",
            "criado_em",
        ]
        read_only_fields = ["id", "criado_em"]

