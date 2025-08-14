from rest_framework import serializers
from app_eventos.models import (
    Empresa, EmpresaUser, Evento, Setor, Funcao, Vaga, Candidatura, AlocacaoFinal
)

class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = "__all__"

class EventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evento
        fields = ["id", "empresa", "descricao", "data_inicio", "data_fim", "meta_cmv"]

class SetorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Setor
        fields = "__all__"

class FuncaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Funcao
        fields = "__all__"

class VagaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vaga
        fields = "__all__"

class CandidaturaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidatura
        fields = ["vaga"]

    def create(self, validated_data):
        user = self.context["request"].user
        return Candidatura.objects.create(user=user, **validated_data)

class CandidaturaListSerializer(serializers.ModelSerializer):
    vaga = VagaSerializer()
    class Meta:
        model = Candidatura
        fields = ["id", "vaga", "status", "data_candidatura"]

class CandidaturaUpdateStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidatura
        fields = ["status"]

class AlocacaoFinalSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlocacaoFinal
        fields = ["id", "candidatura", "setor", "funcao", "data_alocacao"]
