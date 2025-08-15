from rest_framework import serializers
from app_eventos.models import Freelance

class FreelanceDocumentosSerializer(serializers.ModelSerializer):
    """
    Serializer para upload de documentos do freelancer.
    Todos os campos são obrigatórios por padrão.
    """
    class Meta:
        model = Freelance
        fields = [
            'arquivo_exame_medico',
            'arquivo_comprovante_residencia',
            'arquivo_identidade_frente',
            'arquivo_identidade_verso'
        ]
        extra_kwargs = {
            'arquivo_exame_medico': {'required': True},
            'arquivo_comprovante_residencia': {'required': True},
            'arquivo_identidade_frente': {'required': True},
            'arquivo_identidade_verso': {'required': True},
        }


class FreelanceCadastroBasicoSerializer(serializers.ModelSerializer):
    """
    Etapa 1 - Cadastro básico do freelancer (sem documentos obrigatórios).
    """
    class Meta:
        model = Freelance
        exclude = ['usuario', 'cadastro_completo']


class FreelanceUploadDocumentosSerializer(serializers.ModelSerializer):
    """
    Etapa 2 - Upload de documentos obrigatórios do freelancer.
    """
    class Meta:
        model = Freelance
        fields = [
            'arquivo_exame_medico',
            'arquivo_comprovante_residencia',
            'arquivo_identidade_frente',
            'arquivo_identidade_verso'
        ]

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.verificar_cadastro_completo()
        return instance
