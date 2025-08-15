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
