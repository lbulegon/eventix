# api_desktop/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import datetime, timedelta
import json

from app_eventos.models import (
    User, EmpresaContratante, Evento, Freelance, Vaga, 
    Candidatura, Equipamento, DespesaEvento, ReceitaEvento
)
from app_eventos.permissions.permissions_grupos import (
    IsAdminSistema, IsEmpresaUser, PodeGerenciarUsuarios,
    PodeGerenciarEventos, PodeGerenciarFreelancers, PodeVisualizarRelatorios
)


class UsuarioDesktopViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de usuários no desktop
    """
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, PodeGerenciarUsuarios]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin_sistema:
            return User.objects.all()
        elif user.is_empresa_user:
            return User.objects.filter(empresa_contratante=user.empresa_contratante)
        return User.objects.none()
    
    @action(detail=False, methods=['get'])
    def estatisticas(self, request):
        """Estatísticas de usuários para dashboard"""
        queryset = self.get_queryset()
        
        stats = {
            'total_usuarios': queryset.count(),
            'usuarios_ativos': queryset.filter(ativo=True).count(),
            'freelancers': queryset.filter(tipo_usuario='freelancer').count(),
            'admins_empresa': queryset.filter(tipo_usuario='admin_empresa').count(),
            'operadores': queryset.filter(tipo_usuario='operador_empresa').count(),
            'novos_este_mes': queryset.filter(
                date_joined__gte=timezone.now().replace(day=1)
            ).count(),
        }
        
        return Response(stats)


class EmpresaDesktopViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de empresas no desktop
    """
    queryset = EmpresaContratante.objects.all()
    permission_classes = [IsAuthenticated, IsAdminSistema]
    
    @action(detail=False, methods=['get'])
    def estatisticas(self, request):
        """Estatísticas de empresas para dashboard"""
        stats = {
            'total_empresas': EmpresaContratante.objects.count(),
            'empresas_ativas': EmpresaContratante.objects.filter(ativo=True).count(),
            'empresas_inativas': EmpresaContratante.objects.filter(ativo=False).count(),
            'receita_total': EmpresaContratante.objects.aggregate(
                total=Sum('valor_mensal')
            )['total'] or 0,
        }
        
        return Response(stats)


class EventoDesktopViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de eventos no desktop
    """
    queryset = Evento.objects.all()
    permission_classes = [IsAuthenticated, PodeGerenciarEventos]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin_sistema:
            return Evento.objects.all()
        elif user.is_empresa_user:
            return Evento.objects.filter(empresa_contratante=user.empresa_contratante)
        return Evento.objects.none()
    
    @action(detail=False, methods=['get'])
    def estatisticas(self, request):
        """Estatísticas de eventos para dashboard"""
        queryset = self.get_queryset()
        
        stats = {
            'total_eventos': queryset.count(),
            'eventos_ativos': queryset.filter(ativo=True).count(),
            'eventos_este_mes': queryset.filter(
                data_inicio__gte=timezone.now().replace(day=1)
            ).count(),
            'eventos_proximos': queryset.filter(
                data_inicio__gte=timezone.now(),
                data_inicio__lte=timezone.now() + timedelta(days=30)
            ).count(),
        }
        
        return Response(stats)


class FreelancerDesktopViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de freelancers no desktop
    """
    queryset = Freelance.objects.all()
    permission_classes = [IsAuthenticated, PodeGerenciarFreelancers]
    
    @action(detail=False, methods=['get'])
    def estatisticas(self, request):
        """Estatísticas de freelancers para dashboard"""
        stats = {
            'total_freelancers': Freelance.objects.count(),
            'cadastros_completos': Freelance.objects.filter(cadastro_completo=True).count(),
            'cadastros_pendentes': Freelance.objects.filter(cadastro_completo=False).count(),
            'novos_este_mes': Freelance.objects.filter(
                atualizado_em__gte=timezone.now().replace(day=1)
            ).count(),
        }
        
        return Response(stats)


class VagaDesktopViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de vagas no desktop
    """
    queryset = Vaga.objects.all()
    permission_classes = [IsAuthenticated, PodeGerenciarEventos]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin_sistema:
            return Vaga.objects.all()
        elif user.is_empresa_user:
            return Vaga.objects.filter(setor__evento__empresa_contratante=user.empresa_contratante)
        return Vaga.objects.none()


class EquipamentoDesktopViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de equipamentos no desktop
    """
    queryset = Equipamento.objects.all()
    permission_classes = [IsAuthenticated, PodeGerenciarEventos]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin_sistema:
            return Equipamento.objects.all()
        elif user.is_empresa_user:
            return Equipamento.objects.filter(empresa_contratante=user.empresa_contratante)
        return Equipamento.objects.none()


class RelatorioDesktopViewSet(viewsets.ViewSet):
    """
    ViewSet para relatórios no desktop
    """
    permission_classes = [IsAuthenticated, PodeVisualizarRelatorios]
    
    @action(detail=False, methods=['get'])
    def financeiro(self, request):
        """Relatório financeiro"""
        user = request.user
        
        if user.is_admin_sistema:
            despesas = DespesaEvento.objects.all()
            receitas = ReceitaEvento.objects.all()
        elif user.is_empresa_user:
            despesas = DespesaEvento.objects.filter(evento__empresa_contratante=user.empresa_contratante)
            receitas = ReceitaEvento.objects.filter(evento__empresa_contratante=user.empresa_contratante)
        else:
            return Response({'error': 'Sem permissão'}, status=status.HTTP_403_FORBIDDEN)
        
        relatorio = {
            'total_despesas': despesas.aggregate(total=Sum('valor'))['total'] or 0,
            'total_receitas': receitas.aggregate(total=Sum('valor'))['total'] or 0,
            'despesas_pendentes': despesas.filter(status='pendente').count(),
            'receitas_pendentes': receitas.filter(status='pendente').count(),
        }
        
        return Response(relatorio)


class DashboardDesktopView(APIView):
    """
    Dashboard principal para o aplicativo desktop
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        dashboard_data = {
            'usuario': {
                'nome': user.get_full_name() or user.username,
                'tipo': user.get_user_type_display_name(),
                'empresa': user.empresa_contratante.nome_fantasia if user.empresa_contratante else None,
                'permissoes': user.get_permissoes(),
            },
            'estatisticas': self._get_estatisticas(user),
            'alertas': self._get_alertas(user),
            'atividades_recentes': self._get_atividades_recentes(user),
        }
        
        return Response(dashboard_data)
    
    def _get_estatisticas(self, user):
        """Obtém estatísticas baseadas no tipo de usuário"""
        if user.is_admin_sistema:
            return {
                'total_usuarios': User.objects.count(),
                'total_empresas': EmpresaContratante.objects.count(),
                'total_eventos': Evento.objects.count(),
                'total_freelancers': Freelance.objects.count(),
            }
        elif user.is_empresa_user:
            return {
                'total_usuarios': User.objects.filter(empresa_contratante=user.empresa_contratante).count(),
                'total_eventos': Evento.objects.filter(empresa_contratante=user.empresa_contratante).count(),
                'total_freelancers': Freelance.objects.count(),
                'total_vagas': Vaga.objects.filter(setor__evento__empresa_contratante=user.empresa_contratante).count(),
            }
        else:
            return {}
    
    def _get_alertas(self, user):
        """Obtém alertas importantes"""
        alertas = []
        
        if user.is_admin_sistema:
            # Alertas para admin do sistema
            empresas_vencendo = EmpresaContratante.objects.filter(
                data_vencimento__lte=timezone.now() + timedelta(days=30),
                ativo=True
            ).count()
            
            if empresas_vencendo > 0:
                alertas.append({
                    'tipo': 'warning',
                    'mensagem': f'{empresas_vencendo} empresa(s) com contrato vencendo em 30 dias'
                })
        
        elif user.is_empresa_user:
            # Alertas para usuários de empresa
            eventos_proximos = Evento.objects.filter(
                empresa_contratante=user.empresa_contratante,
                data_inicio__lte=timezone.now() + timedelta(days=7),
                ativo=True
            ).count()
            
            if eventos_proximos > 0:
                alertas.append({
                    'tipo': 'info',
                    'mensagem': f'{eventos_proximos} evento(s) próximo(s)'
                })
        
        return alertas
    
    def _get_atividades_recentes(self, user):
        """Obtém atividades recentes"""
        atividades = []
        
        if user.is_admin_sistema:
            # Atividades para admin do sistema
            usuarios_recentes = User.objects.filter(
                date_joined__gte=timezone.now() - timedelta(days=7)
            )[:5]
            
            for usuario in usuarios_recentes:
                atividades.append({
                    'tipo': 'usuario_novo',
                    'descricao': f'Novo usuário: {usuario.username}',
                    'data': usuario.date_joined,
                })
        
        return atividades


class EstatisticasDesktopView(APIView):
    """
    View para estatísticas detalhadas do desktop
    """
    permission_classes = [IsAuthenticated, PodeVisualizarRelatorios]
    
    def get(self, request):
        user = request.user
        
        estatisticas = {
            'periodo': request.GET.get('periodo', '30'),  # dias
            'dados': self._get_dados_estatisticos(user, int(request.GET.get('periodo', '30')))
        }
        
        return Response(estatisticas)
    
    def _get_dados_estatisticos(self, user, dias):
        """Obtém dados estatísticos para o período especificado"""
        data_inicio = timezone.now() - timedelta(days=dias)
        
        if user.is_admin_sistema:
            return {
                'usuarios_por_dia': self._get_usuarios_por_dia(data_inicio),
                'eventos_por_dia': self._get_eventos_por_dia(data_inicio),
                'empresas_ativas': EmpresaContratante.objects.filter(ativo=True).count(),
            }
        elif user.is_empresa_user:
            return {
                'eventos_por_dia': self._get_eventos_por_dia(data_inicio, user.empresa_contratante),
                'candidaturas_por_dia': self._get_candidaturas_por_dia(data_inicio, user.empresa_contratante),
            }
        
        return {}
    
    def _get_usuarios_por_dia(self, data_inicio):
        """Obtém usuários criados por dia"""
        # Implementar lógica de agregação por dia
        return []
    
    def _get_eventos_por_dia(self, data_inicio, empresa=None):
        """Obtém eventos criados por dia"""
        # Implementar lógica de agregação por dia
        return []
    
    def _get_candidaturas_por_dia(self, data_inicio, empresa):
        """Obtém candidaturas por dia"""
        # Implementar lógica de agregação por dia
        return []


class ExportarDadosView(APIView):
    """
    View para exportar dados do sistema
    """
    permission_classes = [IsAuthenticated, PodeVisualizarRelatorios]
    
    def post(self, request):
        tipo_exportacao = request.data.get('tipo')
        formato = request.data.get('formato', 'json')
        
        if tipo_exportacao == 'usuarios':
            dados = self._exportar_usuarios(request.user)
        elif tipo_exportacao == 'eventos':
            dados = self._exportar_eventos(request.user)
        elif tipo_exportacao == 'freelancers':
            dados = self._exportar_freelancers()
        else:
            return Response({'error': 'Tipo de exportação inválido'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'dados': dados,
            'formato': formato,
            'timestamp': timezone.now().isoformat(),
        })
    
    def _exportar_usuarios(self, user):
        """Exporta dados de usuários"""
        if user.is_admin_sistema:
            return list(User.objects.values('username', 'email', 'tipo_usuario', 'ativo', 'date_joined'))
        elif user.is_empresa_user:
            return list(User.objects.filter(empresa_contratante=user.empresa_contratante).values(
                'username', 'email', 'tipo_usuario', 'ativo', 'date_joined'
            ))
        return []
    
    def _exportar_eventos(self, user):
        """Exporta dados de eventos"""
        if user.is_admin_sistema:
            return list(Evento.objects.values('nome', 'data_inicio', 'data_fim', 'ativo'))
        elif user.is_empresa_user:
            return list(Evento.objects.filter(empresa_contratante=user.empresa_contratante).values(
                'nome', 'data_inicio', 'data_fim', 'ativo'
            ))
        return []
    
    def _exportar_freelancers(self):
        """Exporta dados de freelancers"""
        return list(Freelance.objects.values('nome_completo', 'cpf', 'telefone', 'cadastro_completo'))


class ConfiguracoesDesktopView(APIView):
    """
    View para configurações do aplicativo desktop
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        configuracoes = {
            'usuario': {
                'nome': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
                'tipo': request.user.tipo_usuario,
            },
            'sistema': {
                'versao': '1.0.0',
                'ambiente': 'desenvolvimento',
            },
            'preferencias': {
                'tema': 'claro',
                'idioma': 'pt-BR',
                'notificacoes': True,
            }
        }
        
        return Response(configuracoes)
    
    def post(self, request):
        # Implementar salvamento de configurações
        return Response({'message': 'Configurações salvas com sucesso'})


class BackupDesktopView(APIView):
    """
    View para backup do sistema
    """
    permission_classes = [IsAuthenticated, IsAdminSistema]
    
    def post(self, request):
        # Implementar lógica de backup
        return Response({
            'message': 'Backup iniciado com sucesso',
            'timestamp': timezone.now().isoformat(),
        })


class LogsDesktopView(APIView):
    """
    View para visualização de logs do sistema
    """
    permission_classes = [IsAuthenticated, IsAdminSistema]
    
    def get(self, request):
        # Implementar lógica de logs
        logs = [
            {
                'timestamp': timezone.now().isoformat(),
                'nivel': 'INFO',
                'mensagem': 'Sistema iniciado',
                'usuario': request.user.username,
            }
        ]
        
        return Response({'logs': logs})


# Views de autenticação específicas para desktop
class LoginDesktopView(APIView):
    """
    Login específico para aplicativo desktop
    """
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response(
                {'error': 'Username e password são obrigatórios'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(username=username, password=password)
        
        if user and user.is_active:
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'tipo_usuario': user.tipo_usuario,
                    'empresa': user.empresa_contratante.nome_fantasia if user.empresa_contratante else None,
                    'permissoes': user.get_permissoes(),
                }
            })
        
        return Response(
            {'error': 'Credenciais inválidas'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )


class LogoutDesktopView(APIView):
    """
    Logout específico para aplicativo desktop
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Implementar lógica de logout
        return Response({'message': 'Logout realizado com sucesso'})


class RefreshTokenDesktopView(APIView):
    """
    Refresh token específico para aplicativo desktop
    """
    
    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        
        if not refresh_token:
            return Response(
                {'error': 'Refresh token é obrigatório'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            
            return Response({
                'access_token': access_token,
                'refresh_token': str(refresh),
            })
        except Exception as e:
            return Response(
                {'error': 'Token inválido'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )


class VerifyTokenDesktopView(APIView):
    """
    Verificação de token específica para aplicativo desktop
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({
            'valid': True,
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'tipo_usuario': request.user.tipo_usuario,
            }
        })
