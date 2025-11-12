from rest_framework import serializers

from .models import CronogramaPreProducao


class CronogramaPreProducaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CronogramaPreProducao
        fields = [
            "id",
            "evento",
            "etapa",
            "prazo",
            "responsavel",
            "status",
            "observacoes",
        ]
        read_only_fields = ["id"]

