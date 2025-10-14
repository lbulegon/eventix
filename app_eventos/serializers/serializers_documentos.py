"""
Serializers para sistema de documentos
"""
from rest_framework import serializers
from app_eventos.models_documentos import (
    DocumentoFreelancerEmpresa,
    ConfiguracaoDocumentosEmpresa,
    ReutilizacaoDocumento
)
from app_eventos.models import EmpresaContratante


class DocumentoFreelancerSerializer(serializers.ModelSerializer):
    """Serializer para documentos do freelancer"""
    tipo_documento_display = serializers.CharField(source='get_tipo_documento_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    empresa_nome = serializers.CharField(source='empresa_contratante.nome_fantasia', read_only=True)
    esta_valido = serializers.BooleanField(read_only=True)
    pode_ser_reutilizado = serializers.BooleanField(read_only=True)
    validado_por_nome = serializers.SerializerMethodField()
    
    class Meta:
        model = DocumentoFreelancerEmpresa
        fields = [
            'id',
            'empresa_contratante',
            'empresa_nome',
            'tipo_documento',
            'tipo_documento_display',
            'arquivo',
            'status',
            'status_display',
            'data_upload',
            'data_vencimento',
            'data_validacao',
            'validado_por',
            'validado_por_nome',
            'observacoes',
            'pode_reutilizar',
            'total_reutilizacoes',
            'esta_valido',
            'pode_ser_reutilizado',
        ]
        read_only_fields = [
            'id',
            'data_upload',
            'data_validacao',
            'validado_por',
            'total_reutilizacoes',
        ]
    
    def get_validado_por_nome(self, obj):
        if obj.validado_por:
            return obj.validado_por.get_full_name() or obj.validado_por.username
        return None


class DocumentoUploadSerializer(serializers.ModelSerializer):
    """Serializer para upload de documentos"""
    
    class Meta:
        model = DocumentoFreelancerEmpresa
        fields = [
            'empresa_contratante',
            'tipo_documento',
            'arquivo',
        ]
    
    def validate(self, data):
        # Verificar se já existe documento deste tipo para esta empresa
        freelancer = self.context['request'].user.freelancerglobal
        empresa = data['empresa_contratante']
        tipo_documento = data['tipo_documento']
        
        doc_existente = DocumentoFreelancerEmpresa.objects.filter(
            empresa_contratante=empresa,
            freelancer=freelancer,
            tipo_documento=tipo_documento
        ).first()
        
        if doc_existente:
            raise serializers.ValidationError(
                f"Já existe um documento do tipo {doc_existente.get_tipo_documento_display()} para esta empresa. "
                f"Use o endpoint de atualização ou exclua o documento anterior."
            )
        
        return data
    
    def create(self, validated_data):
        # Adicionar freelancer e calcular data de vencimento
        from django.utils import timezone
        from datetime import timedelta
        
        freelancer = self.context['request'].user.freelancerglobal
        empresa = validated_data['empresa_contratante']
        tipo_documento = validated_data['tipo_documento']
        
        # Buscar período de validade da configuração da empresa
        try:
            config = ConfiguracaoDocumentosEmpresa.objects.get(empresa_contratante=empresa)
            periodo_validade = config.get_periodo_validade(tipo_documento)
        except ConfiguracaoDocumentosEmpresa.DoesNotExist:
            periodo_validade = 365
        
        validated_data['freelancer'] = freelancer
        validated_data['data_vencimento'] = timezone.now() + timedelta(days=periodo_validade)
        validated_data['status'] = 'pendente'
        
        return super().create(validated_data)


class ConfiguracaoDocumentosSerializer(serializers.ModelSerializer):
    """Serializer para configuração de documentos da empresa"""
    empresa_nome = serializers.CharField(source='empresa_contratante.nome_fantasia', read_only=True)
    documentos_obrigatorios = serializers.SerializerMethodField()
    
    class Meta:
        model = ConfiguracaoDocumentosEmpresa
        fields = '__all__'
        read_only_fields = ['empresa_contratante']
    
    def get_documentos_obrigatorios(self, obj):
        return obj.get_documentos_obrigatorios()


class VerificacaoDocumentosSerializer(serializers.Serializer):
    """Serializer para verificação de documentos de um freelancer"""
    empresa_id = serializers.IntegerField()
    vaga_id = serializers.IntegerField(required=False, allow_null=True)
    
    def validate_empresa_id(self, value):
        try:
            EmpresaContratante.objects.get(id=value)
        except EmpresaContratante.DoesNotExist:
            raise serializers.ValidationError("Empresa não encontrada")
        return value


class StatusDocumentosResponseSerializer(serializers.Serializer):
    """Serializer para resposta de status de documentos"""
    documentos_validos = serializers.BooleanField()
    pode_candidatar = serializers.BooleanField()
    documentos_faltantes = serializers.ListField(child=serializers.CharField())
    documentos_expirados = serializers.ListField(child=serializers.CharField())
    documentos_rejeitados = serializers.ListField(child=serializers.CharField())
    documentos_pendentes = serializers.ListField(child=serializers.CharField())
    documentos_aprovados = serializers.ListField(child=serializers.CharField())
    total_documentos = serializers.IntegerField()
    mensagem = serializers.CharField()


class ReutilizacaoDocumentoSerializer(serializers.ModelSerializer):
    """Serializer para reutilização de documentos"""
    documento_tipo = serializers.CharField(source='documento_original.get_tipo_documento_display', read_only=True)
    vaga_titulo = serializers.CharField(source='vaga_utilizada.titulo', read_only=True)
    
    class Meta:
        model = ReutilizacaoDocumento
        fields = [
            'id',
            'documento_original',
            'documento_tipo',
            'vaga_utilizada',
            'vaga_titulo',
            'candidatura',
            'data_reutilizacao',
            'status_na_reutilizacao',
        ]
        read_only_fields = ['id', 'data_reutilizacao']

