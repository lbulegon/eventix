from rest_framework import serializers

from .models import FichaTecnica, Menu, Prato


class FichaTecnicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FichaTecnica
        fields = [
            "id",
            "prato",
            "modo_preparo",
            "rendimento",
            "tempo_execucao",
            "insumos",
        ]
        read_only_fields = ["id"]


class PratoSerializer(serializers.ModelSerializer):
    fichas = FichaTecnicaSerializer(many=True, read_only=True)

    class Meta:
        model = Prato
        fields = [
            "id",
            "menu",
            "nome",
            "categoria",
            "custo_estimado",
            "tempo_preparo_min",
            "fichas",
        ]
        read_only_fields = ["id", "fichas"]


class MenuSerializer(serializers.ModelSerializer):
    pratos = PratoSerializer(many=True, read_only=True)

    class Meta:
        model = Menu
        fields = [
            "id",
            "evento",
            "titulo",
            "observacoes",
            "criado_em",
            "pratos",
        ]
        read_only_fields = ["id", "criado_em", "pratos"]

