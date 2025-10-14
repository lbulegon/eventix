"""
Views da API para sistema de documentos
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from app_eventos.models_documentos import (
    DocumentoFreelancerEmpresa,
    ConfiguracaoDocumentosEmpresa,
    ReutilizacaoDocumento
)
from app_eventos.models import EmpresaContratante
from app_eventos.models_freelancers import FreelancerGlobal, VagaEmpresa

from app_eventos.serializers.serializers_documentos import (
    DocumentoFreelancerSerializer,
    DocumentoUploadSerializer,
    ConfiguracaoDocumentosSerializer,
    VerificacaoDocumentosSerializer,
    StatusDocumentosResponseSerializer,
    ReutilizacaoDocumentoSerializer
)


class DocumentoFreelancerViewSet(viewsets.ModelViewSet):
    """
    ViewSet para documentos do freelancer
    """
    serializer_class = DocumentoFreelancerSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # Se é freelancer, retorna apenas seus documentos
        if hasattr(user, 'freelancerglobal'):
            return DocumentoFreelancerEmpresa.objects.filter(
                freelancer=user.freelancerglobal
            ).select_related('empresa_contratante', 'validado_por')
        
        # Se é empresa, retorna documentos da empresa
        elif hasattr(user, 'empresa_contratante'):
            return DocumentoFreelancerEmpresa.objects.filter(
                empresa_contratante=user.empresa_contratante
            ).select_related('freelancer__usuario', 'validado_por')
        
        return DocumentoFreelancerEmpresa.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DocumentoUploadSerializer
        return DocumentoFreelancerSerializer
    
    @action(detail=False, methods=['get'])
    def por_empresa(self, request):
        """Retorna documentos do freelancer para uma empresa específica"""
        empresa_id = request.query_params.get('empresa_id')
        
        if not empresa_id:
            return Response(
                {'error': 'empresa_id é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not hasattr(request.user, 'freelancerglobal'):
            return Response(
                {'error': 'Apenas freelancers podem acessar este endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        documentos = DocumentoFreelancerEmpresa.objects.filter(
            empresa_contratante_id=empresa_id,
            freelancer=request.user.freelancerglobal
        )
        
        serializer = self.get_serializer(documentos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pendentes(self, request):
        """Retorna documentos pendentes de validação (empresa)"""
        if not hasattr(request.user, 'empresa_contratante'):
            return Response(
                {'error': 'Apenas empresas podem acessar este endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        documentos = DocumentoFreelancerEmpresa.objects.filter(
            empresa_contratante=request.user.empresa_contratante,
            status='pendente'
        ).select_related('freelancer__usuario')
        
        serializer = self.get_serializer(documentos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def aprovar(self, request, pk=None):
        """Aprovar documento"""
        if not hasattr(request.user, 'empresa_contratante'):
            return Response(
                {'error': 'Apenas empresas podem aprovar documentos'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        documento = self.get_object()
        
        if documento.empresa_contratante != request.user.empresa_contratante:
            return Response(
                {'error': 'Você não tem permissão para aprovar este documento'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        from django.utils import timezone
        documento.status = 'aprovado'
        documento.validado_por = request.user
        documento.data_validacao = timezone.now()
        documento.observacoes = request.data.get('observacoes', '')
        documento.save()
        
        serializer = self.get_serializer(documento)
        return Response({
            'message': 'Documento aprovado com sucesso',
            'documento': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def rejeitar(self, request, pk=None):
        """Rejeitar documento"""
        if not hasattr(request.user, 'empresa_contratante'):
            return Response(
                {'error': 'Apenas empresas podem rejeitar documentos'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        documento = self.get_object()
        
        if documento.empresa_contratante != request.user.empresa_contratante:
            return Response(
                {'error': 'Você não tem permissão para rejeitar este documento'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        observacoes = request.data.get('observacoes', '')
        if not observacoes:
            return Response(
                {'error': 'Observações são obrigatórias ao rejeitar um documento'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from django.utils import timezone
        documento.status = 'rejeitado'
        documento.validado_por = request.user
        documento.data_validacao = timezone.now()
        documento.observacoes = observacoes
        documento.save()
        
        serializer = self.get_serializer(documento)
        return Response({
            'message': 'Documento rejeitado',
            'documento': serializer.data
        })


class VerificarDocumentosView(APIView):
    """
    API para verificar status dos documentos de um freelancer
    
    GET /api/v1/documentos/verificar/?empresa_id=1&vaga_id=5
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Validar parâmetros
        serializer = VerificacaoDocumentosSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar se usuário é freelancer
        if not hasattr(request.user, 'freelancerglobal'):
            return Response(
                {'error': 'Apenas freelancers podem verificar documentos'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        freelancer = request.user.freelancerglobal
        empresa_id = serializer.validated_data['empresa_id']
        vaga_id = serializer.validated_data.get('vaga_id')
        
        empresa = EmpresaContratante.objects.get(id=empresa_id)
        
        # Buscar configuração da empresa
        try:
            config = ConfiguracaoDocumentosEmpresa.objects.get(empresa_contratante=empresa)
            docs_obrigatorios = config.get_documentos_obrigatorios()
        except ConfiguracaoDocumentosEmpresa.DoesNotExist:
            docs_obrigatorios = []
        
        # Se tem vaga, verificar documentos específicos da vaga
        if vaga_id:
            # TODO: Implementar documentos específicos por vaga
            pass
        
        # Documentos do freelancer para esta empresa
        documentos = DocumentoFreelancerEmpresa.objects.filter(
            empresa_contratante=empresa,
            freelancer=freelancer
        )
        
        # Classificar documentos
        docs_aprovados = []
        docs_pendentes = []
        docs_rejeitados = []
        docs_expirados = []
        docs_faltantes = []
        
        for doc_tipo in docs_obrigatorios:
            doc = documentos.filter(tipo_documento=doc_tipo).first()
            
            if not doc:
                docs_faltantes.append(doc_tipo)
            elif doc.status == 'aprovado':
                if doc.esta_valido:
                    docs_aprovados.append(doc_tipo)
                else:
                    docs_expirados.append(doc_tipo)
            elif doc.status == 'pendente':
                docs_pendentes.append(doc_tipo)
            elif doc.status == 'rejeitado':
                docs_rejeitados.append(doc_tipo)
            elif doc.status == 'expirado':
                docs_expirados.append(doc_tipo)
        
        # Determinar se pode candidatar
        documentos_validos = (
            len(docs_faltantes) == 0 and
            len(docs_expirados) == 0 and
            len(docs_rejeitados) == 0 and
            len(docs_pendentes) == 0
        )
        
        pode_candidatar = documentos_validos
        
        # Mensagem
        if pode_candidatar:
            mensagem = "Todos os documentos estão válidos. Você pode se candidatar!"
        elif docs_faltantes:
            mensagem = f"Você precisa enviar: {', '.join(docs_faltantes)}"
        elif docs_pendentes:
            mensagem = "Aguardando validação de documentos pela empresa"
        elif docs_expirados:
            mensagem = "Alguns documentos estão expirados. Por favor, atualize-os"
        elif docs_rejeitados:
            mensagem = "Alguns documentos foram rejeitados. Verifique as observações"
        else:
            mensagem = "Status dos documentos desconhecido"
        
        response_data = {
            'documentos_validos': documentos_validos,
            'pode_candidatar': pode_candidatar,
            'documentos_faltantes': docs_faltantes,
            'documentos_expirados': docs_expirados,
            'documentos_rejeitados': docs_rejeitados,
            'documentos_pendentes': docs_pendentes,
            'documentos_aprovados': docs_aprovados,
            'total_documentos': documentos.count(),
            'mensagem': mensagem,
        }
        
        response_serializer = StatusDocumentosResponseSerializer(data=response_data)
        if response_serializer.is_valid():
            return Response(response_serializer.data)
        
        return Response(response_data)


class ConfiguracaoDocumentosViewSet(viewsets.ModelViewSet):
    """
    ViewSet para configuração de documentos da empresa
    """
    serializer_class = ConfiguracaoDocumentosSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if hasattr(self.request.user, 'empresa_contratante'):
            return ConfiguracaoDocumentosEmpresa.objects.filter(
                empresa_contratante=self.request.user.empresa_contratante
            )
        return ConfiguracaoDocumentosEmpresa.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(empresa_contratante=self.request.user.empresa_contratante)
    
    @action(detail=False, methods=['get'])
    def minha_configuracao(self, request):
        """Retorna a configuração da empresa do usuário logado"""
        if not hasattr(request.user, 'empresa_contratante'):
            return Response(
                {'error': 'Apenas empresas podem acessar este endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        config, created = ConfiguracaoDocumentosEmpresa.objects.get_or_create(
            empresa_contratante=request.user.empresa_contratante
        )
        
        serializer = self.get_serializer(config)
        return Response(serializer.data)


class ReutilizacaoDocumentoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para visualizar reutilizações de documentos
    """
    serializer_class = ReutilizacaoDocumentoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # Se é freelancer, retorna reutilizações de seus documentos
        if hasattr(user, 'freelancerglobal'):
            return ReutilizacaoDocumento.objects.filter(
                documento_original__freelancer=user.freelancerglobal
            ).select_related('documento_original', 'vaga_utilizada', 'candidatura')
        
        # Se é empresa, retorna reutilizações em suas vagas
        elif hasattr(user, 'empresa_contratante'):
            return ReutilizacaoDocumento.objects.filter(
                vaga_utilizada__empresa_contratante=user.empresa_contratante
            ).select_related('documento_original', 'vaga_utilizada', 'candidatura')
        
        return ReutilizacaoDocumento.objects.none()

