from rest_framework import serializers

from .models import MiseEnPlace


class MiseEnPlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MiseEnPlace
        fields = [
            "id",
            "evento",
            "setor",
            "tarefa",
            "responsavel",
            "tempo_estimado_min",
            "status",
            "qr_code_url",
        ]
        read_only_fields = ["id"]

