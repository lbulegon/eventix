# api_mobile/views_avancadas.py
from rest_framework import viewsets, status, permissions, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, Count, F
from django.utils import timezone
from django.shortcuts import get_object_or_404

from app_eventos.utils_empresa_ativa import empresa_contexto_api
from app_eventos.models import (
    Vaga, Candidatura, Evento, Freelance, Empresa, 
    EmpresaContratante, SetorEvento, Funcao
)
from app_eventos.services.matching_service import MatchingService, VagaRecommendationService
from .serializers import (
    VagaSerializer, CandidaturaSerializer, EventoSerializer,
    FreelanceSerializer, EmpresaSerializer, EmpresaContratanteSerializer
)

_VAGA_COUNT_ANNOTATE = {'_candidaturas_count': Count('candidaturas')}


class VagaAvancadaViewSet(viewsets.ModelViewSet):
    """
    ViewSet avançado para gerenciamento de vagas
    """
    serializer_class = VagaSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_freelancer:
            # Freelancer vê vagas ativas e publicadas
            return (
                Vaga.objects.filter(
                    ativa=True,
                    publicada=True,
                    data_limite_candidatura__gte=timezone.now(),
                )
                .annotate(**_VAGA_COUNT_ANNOTATE)
                .select_related(
                    'setor__evento',
                    'funcao',
                    'ponto_operacao',
                    'criado_por',
                    'empresa_contratante',
                )
            )
        elif user.is_empresa_user:
            # Empresa vê suas próprias vagas
            return (
                Vaga.objects.filter(empresa_contratante=user.empresa_contratante)
                .annotate(**_VAGA_COUNT_ANNOTATE)
                .select_related(
                    'setor__evento',
                    'funcao',
                    'ponto_operacao',
                    'criado_por',
                    'empresa_contratante',
                )
            )
        elif getattr(user, 'is_gestor_grupo', False):
            ec = empresa_contexto_api(self.request)
            if not ec:
                return Vaga.objects.none()
            return (
                Vaga.objects.filter(empresa_contratante=ec)
                .annotate(**_VAGA_COUNT_ANNOTATE)
                .select_related(
                    'setor__evento',
                    'funcao',
                    'ponto_operacao',
                    'criado_por',
                    'empresa_contratante',
                )
            )
        else:
            # Admin vê todas
            return (
                Vaga.objects.all()
                .annotate(**_VAGA_COUNT_ANNOTATE)
                .select_related('setor__evento', 'funcao', 'criado_por', 'empresa_contratante')
            )
    
    def perform_create(self, serializer):
        user = self.request.user
        empresa_actor_id = None
        if user.is_empresa_user:
            empresa_actor_id = user.empresa_contratante_id
        elif getattr(user, 'is_gestor_grupo', False):
            ec = empresa_contexto_api(self.request)
            if not ec:
                raise serializers.ValidationError("Gestor de grupo deve informar contexto de empresa.")
            empresa_actor_id = ec.id
        else:
            raise serializers.ValidationError("Apenas empresas ou gestor de grupo podem criar vagas")
        
        # Define empresa contratante: do setor/evento ou do ponto de operação
        setor = serializer.validated_data.get('setor')
        ponto_operacao = serializer.validated_data.get('ponto_operacao')
        if ponto_operacao:
            empresa_contratante = ponto_operacao.empresa_contratante
        elif setor:
            empresa_contratante = setor.evento.empresa_contratante
        else:
            raise serializers.ValidationError("Informe setor (evento) ou ponto_operacao")

        if empresa_contratante_id := getattr(empresa_contratante, 'id', None):
            if empresa_contratante_id != empresa_actor_id:
                raise serializers.ValidationError(
                    "Você só pode criar vagas vinculadas à sua própria empresa."
                )
        
        evento = setor.evento if setor else None
        serializer.save(
            criado_por=user,
            empresa_contratante=empresa_contratante,
            evento=evento,
        )

    def perform_update(self, serializer):
        user = self.request.user
        vaga = self.get_object()
        empresa_actor_id = None
        if user.is_empresa_user:
            empresa_actor_id = user.empresa_contratante_id
        elif getattr(user, 'is_gestor_grupo', False):
            ec = empresa_contexto_api(self.request)
            if not ec:
                raise serializers.ValidationError("Gestor de grupo deve informar contexto de empresa.")
            empresa_actor_id = ec.id
        else:
            raise serializers.ValidationError("Apenas empresas ou gestor de grupo podem editar vagas")

        if vaga.empresa_contratante_id != empresa_actor_id:
            raise serializers.ValidationError("Você não pode editar vagas de outra empresa.")
        setor = serializer.validated_data.get('setor', vaga.setor)
        ponto = serializer.validated_data.get('ponto_operacao', vaga.ponto_operacao)
        evento = setor.evento if setor else None
        serializer.save(
            evento=evento,
            setor=setor if not ponto else None,
        )
    
    @action(detail=False, methods=['get'])
    def recomendadas(self, request):
        """
        Retorna vagas recomendadas para o freelancer logado
        """
        user = request.user
        if not user.is_freelancer:
            return Response(
                {'error': 'Apenas freelancers podem acessar vagas recomendadas'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Por enquanto, retorna as mesmas vagas que a API normal
        vagas = self.get_queryset()
        serializer = self.get_serializer(vagas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def trending(self, request):
        """
        Retorna vagas em alta (com mais candidaturas)
        """
        # Por enquanto, retorna as mesmas vagas que a API normal
        vagas = self.get_queryset()
        serializer = self.get_serializer(vagas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def urgentes(self, request):
        """
        Retorna vagas urgentes
        """
        # Por enquanto, retorna as mesmas vagas que a API normal
        vagas = self.get_queryset()
        serializer = self.get_serializer(vagas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def por_localizacao(self, request):
        """
        Retorna vagas por localização
        """
        cidade = request.query_params.get('cidade')
        if not cidade:
            return Response(
                {'error': 'Parâmetro cidade é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        vagas = VagaRecommendationService.obter_vagas_por_localizacao(cidade)
        serializer = self.get_serializer(vagas, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def publicar(self, request, pk=None):
        """
        Publica uma vaga (apenas empresas)
        """
        vaga = self.get_object()
        user = request.user
        
        empresa_actor_id = None
        if user.is_empresa_user:
            empresa_actor_id = user.empresa_contratante_id
        elif getattr(user, 'is_gestor_grupo', False):
            ec = empresa_contexto_api(request)
            if not ec:
                return Response(
                    {'error': 'Gestor de grupo deve informar contexto de empresa'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            empresa_actor_id = ec.id
        else:
            return Response(
                {'error': 'Apenas empresas ou gestor de grupo podem publicar vagas'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if vaga.empresa_contratante_id != empresa_actor_id:
            return Response(
                {'error': 'Você não pode publicar esta vaga'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        vaga.publicada = True
        vaga.save()
        
        return Response({'message': 'Vaga publicada com sucesso'})
    
    @action(detail=True, methods=['post'])
    def despublicar(self, request, pk=None):
        """
        Despublica uma vaga (apenas empresas)
        """
        vaga = self.get_object()
        user = request.user
        
        empresa_actor_id = None
        if user.is_empresa_user:
            empresa_actor_id = user.empresa_contratante_id
        elif getattr(user, 'is_gestor_grupo', False):
            ec = empresa_contexto_api(request)
            if not ec:
                return Response(
                    {'error': 'Gestor de grupo deve informar contexto de empresa'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            empresa_actor_id = ec.id
        else:
            return Response(
                {'error': 'Apenas empresas ou gestor de grupo podem despublicar vagas'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if vaga.empresa_contratante_id != empresa_actor_id:
            return Response(
                {'error': 'Você não pode despublicar esta vaga'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        vaga.publicada = False
        vaga.save()
        
        return Response({'message': 'Vaga despublicada com sucesso'})
    
    @action(detail=True, methods=['get'])
    def estatisticas(self, request, pk=None):
        """
        Retorna estatísticas de uma vaga
        """
        vaga = self.get_object()
        user = request.user
        
        # Verificar permissão
        if user.is_freelancer:
            return Response(
                {'error': 'Freelancers não podem ver estatísticas de vagas'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if user.is_empresa_user and vaga.empresa_contratante != user.empresa_contratante:
            return Response(
                {'error': 'Você não pode ver estatísticas desta vaga'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Calcular estatísticas
        total_candidaturas = vaga.candidaturas.count()
        candidaturas_aprovadas = vaga.candidaturas.filter(status='aprovado').count()
        candidaturas_pendentes = vaga.candidaturas.filter(status='pendente').count()
        candidaturas_rejeitadas = vaga.candidaturas.filter(status='rejeitado').count()
        
        taxa_aprovacao = (candidaturas_aprovadas / total_candidaturas * 100) if total_candidaturas > 0 else 0
        
        return Response({
            'total_candidaturas': total_candidaturas,
            'candidaturas_aprovadas': candidaturas_aprovadas,
            'candidaturas_pendentes': candidaturas_pendentes,
            'candidaturas_rejeitadas': candidaturas_rejeitadas,
            'taxa_aprovacao': round(taxa_aprovacao, 2),
            'vagas_disponiveis': vaga.vagas_disponiveis,
            'vagas_preenchidas': vaga.quantidade_preenchida,
            'percentual_preenchimento': round((vaga.quantidade_preenchida / vaga.quantidade * 100), 2)
        })


class CandidaturaAvancadaViewSet(viewsets.ModelViewSet):
    """
    ViewSet avançado para gerenciamento de candidaturas
    """
    serializer_class = CandidaturaSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_freelancer:
            # Freelancer vê suas próprias candidaturas
            try:
                freelance = user.freelance
                return Candidatura.objects.filter(freelance=freelance).select_related(
                    'vaga__setor__evento', 'vaga__funcao', 'analisado_por'
                )
            except Freelance.DoesNotExist:
                return Candidatura.objects.none()
        else:
            # Empresa vê candidaturas para suas vagas
            return Candidatura.objects.filter(
                vaga__empresa_contratante=user.empresa_contratante
            ).select_related('vaga__setor__evento', 'vaga__funcao', 'freelance', 'analisado_por')
    
    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_freelancer:
            raise serializers.ValidationError("Apenas freelancers podem se candidatar")
        
        try:
            freelance = user.freelance
        except Freelance.DoesNotExist:
            raise serializers.ValidationError("Perfil freelancer não encontrado")
        
        vaga = serializer.validated_data['vaga']
        
        # Verificar se já existe candidatura
        if Candidatura.objects.filter(freelance=freelance, vaga=vaga).exists():
            raise serializers.ValidationError("Você já se candidatou para esta vaga")
        
        # Verificar se a vaga aceita candidaturas
        if not vaga.pode_candidatar():
            raise serializers.ValidationError("Esta vaga não está mais aceitando candidaturas")
        
        serializer.save(freelance=freelance)
    
    @action(detail=True, methods=['post'])
    def aprovar(self, request, pk=None):
        """
        Aprova uma candidatura (apenas empresas)
        """
        candidatura = self.get_object()
        user = request.user
        
        if not user.is_empresa_user:
            return Response(
                {'error': 'Apenas empresas podem aprovar candidaturas'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if candidatura.vaga.empresa_contratante != user.empresa_contratante:
            return Response(
                {'error': 'Você não pode aprovar esta candidatura'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if candidatura.aprovar(usuario_aprovador=user):
            return Response({'message': 'Candidatura aprovada com sucesso'})
        else:
            return Response(
                {'error': 'Não foi possível aprovar esta candidatura'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def rejeitar(self, request, pk=None):
        """
        Rejeita uma candidatura (apenas empresas)
        """
        candidatura = self.get_object()
        user = request.user
        
        if not user.is_empresa_user:
            return Response(
                {'error': 'Apenas empresas podem rejeitar candidaturas'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if candidatura.vaga.empresa_contratante != user.empresa_contratante:
            return Response(
                {'error': 'Você não pode rejeitar esta candidatura'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        motivo = request.data.get('motivo', '')
        
        if candidatura.rejeitar(motivo=motivo, usuario_rejeitador=user):
            return Response({'message': 'Candidatura rejeitada'})
        else:
            return Response(
                {'error': 'Não foi possível rejeitar esta candidatura'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """
        Cancela uma candidatura (apenas freelancer)
        """
        candidatura = self.get_object()
        user = request.user
        
        if not user.is_freelancer or candidatura.freelance.usuario != user:
            return Response(
                {'error': 'Você não pode cancelar esta candidatura'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if candidatura.cancelar():
            return Response({'message': 'Candidatura cancelada com sucesso'})
        else:
            return Response(
                {'error': 'Não foi possível cancelar esta candidatura'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def avaliar(self, request, pk=None):
        """
        Avalia uma candidatura (apenas empresas)
        """
        candidatura = self.get_object()
        user = request.user
        
        if not user.is_empresa_user:
            return Response(
                {'error': 'Apenas empresas podem avaliar candidaturas'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if candidatura.vaga.empresa_contratante != user.empresa_contratante:
            return Response(
                {'error': 'Você não pode avaliar esta candidatura'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        nota = request.data.get('nota')
        comentarios = request.data.get('comentarios', '')
        
        if not nota or not (1 <= int(nota) <= 5):
            return Response(
                {'error': 'Nota deve ser um número entre 1 e 5'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        candidatura.nota_empresa = int(nota)
        candidatura.comentarios_empresa = comentarios
        candidatura.save()
        
        return Response({'message': 'Avaliação salva com sucesso'})
    
    @action(detail=False, methods=['get'])
    def dashboard_empresa(self, request):
        """
        Dashboard de candidaturas para empresas
        """
        user = request.user
        if not user.is_empresa_user:
            return Response(
                {'error': 'Apenas empresas podem acessar o dashboard'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Estatísticas gerais
        candidaturas = Candidatura.objects.filter(
            vaga__setor__evento__empresa_contratante=user.empresa_contratante
        )
        
        total_candidaturas = candidaturas.count()
        candidaturas_pendentes = candidaturas.filter(status='pendente').count()
        candidaturas_aprovadas = candidaturas.filter(status='aprovado').count()
        candidaturas_rejeitadas = candidaturas.filter(status='rejeitado').count()
        
        # Candidaturas recentes
        candidaturas_recentes = candidaturas.order_by('-data_candidatura')[:10]
        
        # Vagas com mais candidaturas
        vagas_populares = Vaga.objects.filter(
            setor__evento__empresa_contratante=user.empresa_contratante
        ).annotate(
            total_candidaturas=Count('candidaturas')
        ).order_by('-total_candidaturas')[:5]
        
        return Response({
            'estatisticas': {
                'total_candidaturas': total_candidaturas,
                'candidaturas_pendentes': candidaturas_pendentes,
                'candidaturas_aprovadas': candidaturas_aprovadas,
                'candidaturas_rejeitadas': candidaturas_rejeitadas,
            },
            'candidaturas_recentes': CandidaturaSerializer(candidaturas_recentes, many=True).data,
            'vagas_populares': VagaSerializer(vagas_populares, many=True).data,
        })


class FreelancerRecommendationView(APIView):
    """
    View para recomendações de freelancers para vagas
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, vaga_id):
        """
        Retorna freelancers recomendados para uma vaga
        """
        user = request.user
        if not user.is_empresa_user:
            return Response(
                {'error': 'Apenas empresas podem ver recomendações de freelancers'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            vaga = Vaga.objects.get(id=vaga_id)
            
            # Verificar se a vaga pertence à empresa
            if vaga.empresa_contratante != user.empresa_contratante:
                return Response(
                    {'error': 'Você não pode ver recomendações para esta vaga'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            freelancers_recomendados = MatchingService.encontrar_freelancers_para_vaga(vaga)
            
            # Serializar dados
            dados = []
            for item in freelancers_recomendados:
                freelancer_data = FreelanceSerializer(item['freelancer']).data
                freelancer_data['score_compatibilidade'] = item['score']
                freelancer_data['motivos_recomendacao'] = item['motivos']
                dados.append(freelancer_data)
            
            return Response(dados)
            
        except Vaga.DoesNotExist:
            return Response(
                {'error': 'Vaga não encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
