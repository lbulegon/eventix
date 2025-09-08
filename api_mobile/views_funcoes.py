# api_mobile/views_funcoes.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q

from app_eventos.models import Freelance, Funcao, TipoFuncao, FreelancerFuncao
from .serializers import FuncaoSerializer, FreelancerFuncaoSerializer

class FuncaoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para listar funções disponíveis para freelancers
    """
    serializer_class = FuncaoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Funcao.objects.filter(ativo=True).select_related('tipo_funcao')
        
        # Filtrar apenas funções de segurança
        queryset = queryset.filter(
            Q(nome__icontains='segurança') |
            Q(nome__icontains='seguranca') |
            Q(nome__icontains='security') |
            Q(tipo_funcao__nome__icontains='segurança') |
            Q(tipo_funcao__nome__icontains='seguranca') |
            Q(tipo_funcao__nome__icontains='security')
        )
        
        return queryset.order_by('tipo_funcao__nome', 'nome')

class FreelancerFuncaoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar funções do freelancer
    """
    serializer_class = FreelancerFuncaoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if not user.is_freelancer:
            return FreelancerFuncao.objects.none()
        
        try:
            freelance = user.freelance
            return FreelancerFuncao.objects.filter(
                freelancer=freelance,
                ativo=True
            ).select_related('funcao__tipo_funcao')
        except Freelance.DoesNotExist:
            return FreelancerFuncao.objects.none()
    
    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_freelancer:
            raise serializers.ValidationError("Apenas freelancers podem adicionar funções")
        
        try:
            freelance = user.freelance
        except Freelance.DoesNotExist:
            raise serializers.ValidationError("Perfil freelancer não encontrado")
        
        # Verificar se já existe
        funcao = serializer.validated_data['funcao']
        if FreelancerFuncao.objects.filter(freelancer=freelance, funcao=funcao).exists():
            raise serializers.ValidationError("Você já possui esta função")
        
        serializer.save(freelancer=freelance)
    
    @action(detail=False, methods=['get'])
    def minhas_funcoes(self, request):
        """
        Retorna as funções do freelancer logado
        """
        user = request.user
        if not user.is_freelancer:
            return Response(
                {'error': 'Apenas freelancers podem acessar suas funções'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            freelance = user.freelance
            funcoes = FreelancerFuncao.objects.filter(
                freelancer=freelance,
                ativo=True
            ).select_related('funcao__tipo_funcao')
            
            serializer = self.get_serializer(funcoes, many=True)
            return Response(serializer.data)
            
        except Freelance.DoesNotExist:
            return Response(
                {'error': 'Perfil freelancer não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def adicionar_funcao(self, request):
        """
        Adiciona uma função ao freelancer
        """
        user = request.user
        if not user.is_freelancer:
            return Response(
                {'error': 'Apenas freelancers podem adicionar funções'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        funcao_id = request.data.get('funcao_id')
        nivel = request.data.get('nivel', 'iniciante')
        
        if not funcao_id:
            return Response(
                {'error': 'funcao_id é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            freelance = user.freelance
            funcao = get_object_or_404(Funcao, id=funcao_id, ativo=True)
            
            # Verificar se já existe
            if FreelancerFuncao.objects.filter(freelancer=freelance, funcao=funcao).exists():
                return Response(
                    {'error': 'Você já possui esta função'},
                    status=status.HTTP_409_CONFLICT
                )
            
            # Criar relação
            freelancer_funcao = FreelancerFuncao.objects.create(
                freelancer=freelance,
                funcao=funcao,
                nivel=nivel
            )
            
            serializer = self.get_serializer(freelancer_funcao)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Freelance.DoesNotExist:
            return Response(
                {'error': 'Perfil freelancer não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['delete'])
    def remover_funcao(self, request, pk=None):
        """
        Remove uma função do freelancer
        """
        user = request.user
        if not user.is_freelancer:
            return Response(
                {'error': 'Apenas freelancers podem remover funções'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            freelance = user.freelance
            freelancer_funcao = get_object_or_404(
                FreelancerFuncao,
                id=pk,
                freelancer=freelance
            )
            
            freelancer_funcao.ativo = False
            freelancer_funcao.save()
            
            return Response({'message': 'Função removida com sucesso'})
            
        except Freelance.DoesNotExist:
            return Response(
                {'error': 'Perfil freelancer não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['patch'])
    def atualizar_nivel(self, request, pk=None):
        """
        Atualiza o nível de uma função
        """
        user = request.user
        if not user.is_freelancer:
            return Response(
                {'error': 'Apenas freelancers podem atualizar níveis'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        nivel = request.data.get('nivel')
        if not nivel:
            return Response(
                {'error': 'nivel é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            freelance = user.freelance
            freelancer_funcao = get_object_or_404(
                FreelancerFuncao,
                id=pk,
                freelancer=freelance
            )
            
            freelancer_funcao.nivel = nivel
            freelancer_funcao.save()
            
            serializer = self.get_serializer(freelancer_funcao)
            return Response(serializer.data)
            
        except Freelance.DoesNotExist:
            return Response(
                {'error': 'Perfil freelancer não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
