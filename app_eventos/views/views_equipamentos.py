from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q, Sum, Count
from django.utils import timezone

from app_eventos.models import (
    CategoriaEquipamento, Equipamento, EquipamentoSetor, ManutencaoEquipamento,
    SetorEvento
)
from app_eventos.serializers.serializers_equipamentos import (
    CategoriaEquipamentoSerializer, EquipamentoSerializer, EquipamentoSetorSerializer,
    ManutencaoEquipamentoSerializer, EquipamentoSetorCreateSerializer,
    EquipamentoSetorUpdateSerializer
)


class CategoriaEquipamentoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar categorias de equipamentos
    """
    queryset = CategoriaEquipamento.objects.all()
    serializer_class = CategoriaEquipamentoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = CategoriaEquipamento.objects.all()
        nome = self.request.query_params.get('nome', None)
        if nome:
            queryset = queryset.filter(nome__icontains=nome)
        return queryset


class EquipamentoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar equipamentos
    """
    queryset = Equipamento.objects.all()
    serializer_class = EquipamentoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Equipamento.objects.select_related('categoria', 'empresa_proprietaria')
        
        # Filtros
        categoria = self.request.query_params.get('categoria', None)
        estado = self.request.query_params.get('estado_conservacao', None)
        ativo = self.request.query_params.get('ativo', None)
        codigo = self.request.query_params.get('codigo', None)
        empresa = self.request.query_params.get('empresa', None)
        
        if categoria:
            queryset = queryset.filter(categoria__id=categoria)
        if estado:
            queryset = queryset.filter(estado_conservacao=estado)
        if ativo is not None:
            queryset = queryset.filter(ativo=ativo.lower() == 'true')
        if codigo:
            queryset = queryset.filter(codigo_patrimonial__icontains=codigo)
        if empresa:
            queryset = queryset.filter(empresa_proprietaria__id=empresa)
            
        return queryset
    
    @action(detail=True, methods=['get'])
    def setores_utilizacao(self, request, pk=None):
        """Lista os setores onde o equipamento está sendo utilizado"""
        equipamento = self.get_object()
        equipamentos_setor = EquipamentoSetor.objects.filter(
            equipamento=equipamento
        ).select_related('setor', 'setor__evento')
        
        serializer = EquipamentoSetorSerializer(equipamentos_setor, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def manutencoes(self, request, pk=None):
        """Lista as manutenções do equipamento"""
        equipamento = self.get_object()
        manutencoes = ManutencaoEquipamento.objects.filter(
            equipamento=equipamento
        ).select_related('responsavel')
        
        serializer = ManutencaoEquipamentoSerializer(manutencoes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def por_empresa(self, request):
        """Lista equipamentos de uma empresa específica"""
        empresa_id = request.query_params.get('empresa_id')
        if not empresa_id:
            return Response(
                {'error': 'empresa_id é obrigatório'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        equipamentos = self.get_queryset().filter(empresa_proprietaria__id=empresa_id)
        serializer = self.get_serializer(equipamentos, many=True)
        return Response(serializer.data)


class EquipamentoSetorViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar equipamentos em setores
    """
    queryset = EquipamentoSetor.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return EquipamentoSetorCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return EquipamentoSetorUpdateSerializer
        return EquipamentoSetorSerializer
    
    def get_queryset(self):
        queryset = EquipamentoSetor.objects.select_related(
            'setor', 'setor__evento', 'setor__evento__empresa_contratante', 
            'equipamento', 'equipamento__categoria', 'equipamento__empresa_proprietaria',
            'responsavel_equipamento'
        )
        
        # Filtros
        setor = self.request.query_params.get('setor', None)
        evento = self.request.query_params.get('evento', None)
        categoria = self.request.query_params.get('categoria', None)
        status = self.request.query_params.get('status', None)
        empresa = self.request.query_params.get('empresa', None)
        
        if setor:
            queryset = queryset.filter(setor__id=setor)
        if evento:
            queryset = queryset.filter(setor__evento__id=evento)
        if categoria:
            queryset = queryset.filter(equipamento__categoria__id=categoria)
        if status:
            queryset = queryset.filter(status=status)
        if empresa:
            queryset = queryset.filter(equipamento__empresa_proprietaria__id=empresa)
            
        return queryset
    
    @action(detail=False, methods=['get'])
    def por_setor(self, request):
        """Lista equipamentos de um setor específico"""
        setor_id = request.query_params.get('setor_id')
        if not setor_id:
            return Response(
                {'error': 'setor_id é obrigatório'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        equipamentos = self.get_queryset().filter(setor__id=setor_id)
        serializer = self.get_serializer(equipamentos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def por_evento(self, request):
        """Lista equipamentos de um evento específico"""
        evento_id = request.query_params.get('evento_id')
        if not evento_id:
            return Response(
                {'error': 'evento_id é obrigatório'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        equipamentos = self.get_queryset().filter(setor__evento__id=evento_id)
        serializer = self.get_serializer(equipamentos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def resumo_evento(self, request):
        """Retorna resumo dos equipamentos de um evento"""
        evento_id = request.query_params.get('evento_id')
        if not evento_id:
            return Response(
                {'error': 'evento_id é obrigatório'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        equipamentos = self.get_queryset().filter(setor__evento__id=evento_id)
        
        # Estatísticas
        total_equipamentos = equipamentos.count()
        total_necessario = equipamentos.aggregate(
            total=Sum('quantidade_necessaria')
        )['total'] or 0
        total_disponivel = equipamentos.aggregate(
            total=Sum('quantidade_disponivel')
        )['total'] or 0
        
        # Por categoria
        por_categoria = equipamentos.values(
            'equipamento__categoria__nome'
        ).annotate(
            total_necessario=Sum('quantidade_necessaria'),
            total_disponivel=Sum('quantidade_disponivel')
        )
        
        # Por status
        por_status = equipamentos.values('status').annotate(
            count=Count('id')
        )
        
        return Response({
            'total_equipamentos': total_equipamentos,
            'total_necessario': total_necessario,
            'total_disponivel': total_disponivel,
            'total_faltante': total_necessario - total_disponivel,
            'percentual_cobertura': (total_disponivel / total_necessario * 100) if total_necessario > 0 else 100,
            'por_categoria': por_categoria,
            'por_status': por_status
        })


class ManutencaoEquipamentoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar manutenções de equipamentos
    """
    queryset = ManutencaoEquipamento.objects.all()
    serializer_class = ManutencaoEquipamentoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = ManutencaoEquipamento.objects.select_related(
            'equipamento', 'equipamento__categoria', 'responsavel'
        )
        
        # Filtros
        equipamento = self.request.query_params.get('equipamento', None)
        tipo = self.request.query_params.get('tipo_manutencao', None)
        status = self.request.query_params.get('status', None)
        
        if equipamento:
            queryset = queryset.filter(equipamento__id=equipamento)
        if tipo:
            queryset = queryset.filter(tipo_manutencao=tipo)
        if status:
            queryset = queryset.filter(status=status)
            
        return queryset
    
    @action(detail=True, methods=['post'])
    def finalizar(self, request, pk=None):
        """Finaliza uma manutenção"""
        manutencao = self.get_object()
        manutencao.status = 'concluida'
        manutencao.data_fim = timezone.now().date()
        manutencao.save()
        
        serializer = self.get_serializer(manutencao)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def agendadas(self, request):
        """Lista manutenções agendadas"""
        manutencoes = self.get_queryset().filter(status='agendada')
        serializer = self.get_serializer(manutencoes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def em_andamento(self, request):
        """Lista manutenções em andamento"""
        manutencoes = self.get_queryset().filter(status='em_andamento')
        serializer = self.get_serializer(manutencoes, many=True)
        return Response(serializer.data)
