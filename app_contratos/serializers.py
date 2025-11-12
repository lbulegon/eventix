from rest_framework import serializers

from .models import ContratoEvento


class ContratoEventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContratoEvento
        fields = [
            "id",
            "evento",
            "orcamento",
            "pdf_url",
            "assinatura_cliente",
            "data_assinatura",
            "condicoes_gerais",
        ]
        read_only_fields = ["id", "pdf_url", "assinatura_cliente", "data_assinatura"]

