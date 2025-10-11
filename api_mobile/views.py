# api_mobile/views.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from django.shortcuts import get_object_or_404

from app_eventos.models import (
    Vaga, Candidatura, Evento, Freelance, Empresa, 
    EmpresaContratante, SetorEvento, Funcao
)
from .serializers import (
    VagaSerializer, CandidaturaSerializer, EventoSerializer,
    FreelanceSerializer, EmpresaSerializer, EmpresaContratanteSerializer,
    UserProfileSerializer, PreCadastroFreelancerSerializer,
    PasswordResetSerializer, PasswordResetConfirmSerializer
)

User = get_user_model()


class VagaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para listar vagas disponíveis
    """
    serializer_class = VagaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Vaga.objects.filter(ativa=True).select_related(
            'setor__evento', 'funcao'
        )
        
        # Filtros
        evento_id = self.request.query_params.get('evento_id')
        funcao_id = self.request.query_params.get('funcao_id')
        cidade = self.request.query_params.get('cidade')
        search = self.request.query_params.get('search')
        
        if evento_id:
            queryset = queryset.filter(setor__evento_id=evento_id)
        
        if funcao_id:
            queryset = queryset.filter(funcao_id=funcao_id)
        
        if cidade:
            queryset = queryset.filter(setor__evento__local__cidade__icontains=cidade)
        
        if search:
            queryset = queryset.filter(
                Q(titulo__icontains=search) |
                Q(descricao__icontains=search) |
                Q(funcao__nome__icontains=search)
            )
        
        return queryset.order_by('-setor__evento__data_inicio')


class CandidaturaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar candidaturas
    """
    serializer_class = CandidaturaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_freelancer:
            # Freelancer vê suas próprias candidaturas
            try:
                freelance = user.freelance
                return Candidatura.objects.filter(freelance=freelance).select_related(
                    'vaga__setor__evento', 'vaga__funcao'
                )
            except Freelance.DoesNotExist:
                return Candidatura.objects.none()
        else:
            # Empresa vê candidaturas para suas vagas
            return Candidatura.objects.filter(
                vaga__empresa_contratante=user.empresa_contratante
            ).select_related('vaga__setor__evento', 'vaga__funcao', 'freelance')
    
    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_freelancer:
            raise serializers.ValidationError("Apenas freelancers podem se candidatar")
        
        try:
            freelance = user.freelance
        except Freelance.DoesNotExist:
            raise serializers.ValidationError("Perfil freelancer não encontrado")
        
        vaga_id = serializer.validated_data['vaga_id']
        vaga = Vaga.objects.get(id=vaga_id)
        
        # Verificar se já existe candidatura
        if Candidatura.objects.filter(freelance=freelance, vaga=vaga).exists():
            raise serializers.ValidationError("Você já se candidatou para esta vaga")
        
        serializer.save(freelance=freelance)
    
    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """
        Cancelar candidatura
        """
        candidatura = self.get_object()
        user = request.user
        
        if user.is_freelancer and candidatura.freelance.usuario != user:
            return Response(
                {'error': 'Você não pode cancelar esta candidatura'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        candidatura.delete()
        return Response({'message': 'Candidatura cancelada com sucesso'})
    
    @action(detail=True, methods=['post'])
    def aprovar(self, request, pk=None):
        """
        Aprovar candidatura (apenas empresas)
        """
        candidatura = self.get_object()
        user = request.user
        
        if not user.is_empresa_user:
            return Response(
                {'error': 'Apenas empresas podem aprovar candidaturas'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        candidatura.status = 'aprovado'
        candidatura.save()
        
        return Response({'message': 'Candidatura aprovada com sucesso'})
    
    @action(detail=True, methods=['post'])
    def rejeitar(self, request, pk=None):
        """
        Rejeitar candidatura (apenas empresas)
        """
        candidatura = self.get_object()
        user = request.user
        
        if not user.is_empresa_user:
            return Response(
                {'error': 'Apenas empresas podem rejeitar candidaturas'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        candidatura.status = 'rejeitado'
        candidatura.save()
        
        return Response({'message': 'Candidatura rejeitada'})


class EventoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar eventos
    """
    serializer_class = EventoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_freelancer:
            # Freelancer vê todos os eventos ativos
            return Evento.objects.filter(ativo=True).select_related('local')
        elif user.is_empresa_user:
            # Empresa vê seus próprios eventos
            return Evento.objects.filter(
                empresa_contratante=user.empresa_contratante
            ).select_related('local')
        else:
            # Admin do sistema vê todos
            return Evento.objects.all().select_related('local')
    
    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_empresa_user:
            raise serializers.ValidationError("Apenas empresas podem criar eventos")
        
        serializer.save(empresa_contratante=user.empresa_contratante)
    
    @action(detail=False, methods=['get'])
    def meus_eventos(self, request):
        """
        Listar eventos da empresa do usuário
        """
        user = request.user
        if not user.is_empresa_user:
            return Response(
                {'error': 'Apenas empresas podem acessar seus eventos'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        eventos = Evento.objects.filter(
            empresa_contratante=user.empresa_contratante
        ).select_related('local')
        
        serializer = self.get_serializer(eventos, many=True)
        return Response(serializer.data)


class FreelanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar freelancers
    """
    serializer_class = FreelanceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_freelancer:
            # Freelancer vê apenas seu próprio perfil
            try:
                return Freelance.objects.filter(usuario=user)
            except Freelance.DoesNotExist:
                return Freelance.objects.none()
        else:
            # Empresas e admins veem todos os freelancers
            return Freelance.objects.all().select_related('usuario')
    
    def get_object(self):
        user = self.request.user
        if user.is_freelancer:
            try:
                return user.freelance
            except Freelance.DoesNotExist:
                return None
        return super().get_object()
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def pre_cadastro(self, request):
        """
        Pré-cadastro de freelancer
        """
        serializer = PreCadastroFreelancerSerializer(data=request.data)
        if serializer.is_valid():
            freelance = serializer.save()
            return Response(
                {'message': 'Pré-cadastro realizado com sucesso', 'freelance_id': freelance.id},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmpresaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para listar empresas
    """
    serializer_class = EmpresaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Empresa.objects.filter(ativo=True)


class EmpresaContratanteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar empresa contratante
    """
    serializer_class = EmpresaContratanteSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_empresa_user:
            return EmpresaContratante.objects.filter(id=user.empresa_contratante.id)
        return EmpresaContratante.objects.none()
    
    def get_object(self):
        user = self.request.user
        if user.is_empresa_user:
            return user.empresa_contratante
        return None


class UserProfileView(APIView):
    """
    View para perfil do usuário com dados completos da empresa
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Dados básicos do usuário
        user_data = UserProfileSerializer(user).data
        
        # Dados adicionais da empresa (se disponível no request)
        empresa_data = {}
        if hasattr(request, 'empresa_contratante') and request.empresa_contratante:
            empresa_data = {
                'empresa_id': getattr(request, 'empresa_contratante_id', None),
                'empresa_nome': getattr(request, 'empresa_contratante_nome', None),
                'empresa_cnpj': getattr(request, 'empresa_contratante_cnpj', None),
                'empresa_ativa': getattr(request, 'empresa_contratante_ativa', None),
                'plano_limites': getattr(request, 'empresa_plano_limites', {}),
                'plano_recursos': getattr(request, 'empresa_plano_recursos', {}),
                'empresas_parceiras_count': getattr(request, 'empresas_parceiras', []).count() if hasattr(request, 'empresas_parceiras') else 0,
            }
        
        # Dados do usuário
        usuario_data = {
            'tipo_usuario': getattr(request, 'usuario_tipo', user.tipo_usuario),
            'ativo': getattr(request, 'usuario_ativo', user.ativo),
            'ultimo_acesso': getattr(request, 'usuario_ultimo_acesso', user.data_ultimo_acesso),
        }
        
        # Resposta completa
        response_data = {
            'usuario': user_data,
            'empresa': empresa_data,
            'usuario_info': usuario_data,
            'timestamp': timezone.now().isoformat(),
        }
        
        return Response(response_data)
    
    def put(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmpresaDataView(APIView):
    """
    View para carregar dados completos da empresa após login
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        if not user.is_empresa_user or not user.empresa_contratante:
            return Response(
                {'error': 'Usuário não está associado a uma empresa'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        empresa = user.empresa_contratante
        
        # Dados completos da empresa
        empresa_data = {
            'id': empresa.id,
            'nome': empresa.nome,
            'nome_fantasia': empresa.nome_fantasia,
            'cnpj': empresa.cnpj,
            'razao_social': empresa.razao_social,
            'telefone': empresa.telefone,
            'email': empresa.email,
            'website': empresa.website,
            'endereco': {
                'cep': empresa.cep,
                'logradouro': empresa.logradouro,
                'numero': empresa.numero,
                'complemento': empresa.complemento,
                'bairro': empresa.bairro,
                'cidade': empresa.cidade,
                'uf': empresa.uf,
            },
            'contrato': {
                'data_contratacao': empresa.data_contratacao,
                'data_vencimento': empresa.data_vencimento,
                'valor_mensal': empresa.valor_mensal,
                'ativo': empresa.ativo,
            }
        }
        
        # Dados do plano contratado
        if empresa.plano_contratado_fk:
            plano = empresa.plano_contratado_fk
            empresa_data['plano'] = {
                'id': plano.id,
                'nome': plano.nome,
                'tipo_plano': plano.tipo_plano,
                'descricao': plano.descricao,
                'limites': {
                    'max_eventos_mes': plano.max_eventos_mes,
                    'max_usuarios': plano.max_usuarios,
                    'max_freelancers': plano.max_freelancers,
                    'max_equipamentos': plano.max_equipamentos,
                    'max_locais': plano.max_locais,
                },
                'recursos': {
                    'suporte_24h': plano.suporte_24h,
                    'relatorios_avancados': plano.relatorios_avancados,
                    'integracao_api': plano.integracao_api,
                    'backup_automatico': plano.backup_automatico,
                    'ssl_certificado': plano.ssl_certificado,
                    'dominio_personalizado': plano.dominio_personalizado,
                },
                'precos': {
                    'valor_mensal': plano.valor_mensal,
                    'valor_anual': plano.valor_anual,
                    'desconto_anual': plano.desconto_anual,
                    'valor_anual_calculado': plano.valor_anual_calculado,
                }
            }
        
        # Estatísticas da empresa
        from app_eventos.models import Evento, Vaga, Candidatura
        stats = {
            'eventos_ativos': Evento.objects.filter(
                empresa_contratante=empresa, ativo=True
            ).count(),
            'vagas_ativas': Vaga.objects.filter(
                empresa_contratante=empresa, ativa=True
            ).count(),
            'candidaturas_pendentes': Candidatura.objects.filter(
                vaga__empresa_contratante=empresa,
                status='pendente'
            ).count(),
        }
        
        response_data = {
            'empresa': empresa_data,
            'estatisticas': stats,
            'usuario': {
                'id': user.id,
                'username': user.username,
                'tipo_usuario': user.tipo_usuario,
                'ativo': user.ativo,
                'ultimo_acesso': user.data_ultimo_acesso,
            },
            'timestamp': timezone.now().isoformat(),
        }
        
        return Response(response_data)


class TokenVerifyView(APIView):
    """
    View para verificar token
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        return Response({'valid': True, 'user_id': request.user.id})


class PasswordResetView(APIView):
    """
    View para reset de senha
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
                # Enviar email (implementar conforme necessário)
                reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
                
                send_mail(
                    'Reset de Senha - Eventix',
                    f'Clique no link para resetar sua senha: {reset_url}',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                
                return Response({'message': 'Email de reset enviado'})
            except User.DoesNotExist:
                return Response({'error': 'Usuário não encontrado'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """
    View para confirmar reset de senha
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']
            
            # Decodificar UID do token (implementar conforme necessário)
            # uid = force_str(urlsafe_base64_decode(uidb64))
            # user = User.objects.get(pk=uid)
            
            # if default_token_generator.check_token(user, token):
            #     user.set_password(new_password)
            #     user.save()
            #     return Response({'message': 'Senha alterada com sucesso'})
            
            return Response({'error': 'Token inválido'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    View personalizada para login com JWT
    """
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Adicionar dados do usuário na resposta
            user = User.objects.get(username=request.data.get('username'))
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'tipo_usuario': user.tipo_usuario,
            }
            
            # Adicionar dados específicos do tipo de usuário
            if user.is_freelancer:
                try:
                    freelance = user.freelance
                    user_data.update({
                        'freelance_id': freelance.id,
                        'nome_completo': freelance.nome_completo,
                        'cadastro_completo': freelance.cadastro_completo,
                    })
                except:
                    pass
            elif user.is_empresa_user:
                try:
                    empresa = user.empresa_contratante
                    user_data.update({
                        'empresa_id': empresa.id,
                        'empresa_nome': empresa.nome,
                    })
                except:
                    pass
            
            response.data['user'] = user_data
            response.data['tokens'] = {
                'access': response.data['access'],
                'refresh': response.data['refresh']
            }
            # Remover os tokens do nível raiz
            del response.data['access']
            del response.data['refresh']
        
        return response


class CustomTokenRefreshView(TokenRefreshView):
    """
    View personalizada para refresh de token
    """
    pass


class RegistrarDeviceTokenView(APIView):
    """
    Endpoint para registrar o device token do FCM para notificações push
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Registra ou atualiza o device token do freelancer
        """
        device_token = request.data.get('device_token')
        
        if not device_token:
            return Response(
                {'error': 'device_token é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar se o usuário tem perfil de freelancer
        try:
            freelancer = request.user.freelance
        except Freelance.DoesNotExist:
            return Response(
                {'error': 'Usuário não tem perfil de freelancer'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Atualizar device token
        freelancer.device_token = device_token
        freelancer.notificacoes_ativas = True
        freelancer.save()
        
        return Response({
            'success': True,
            'message': 'Device token registrado com sucesso',
            'device_token': device_token,
            'notificacoes_ativas': freelancer.notificacoes_ativas
        }, status=status.HTTP_200_OK)


class DesativarNotificacoesView(APIView):
    """
    Endpoint para desativar notificações push
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Desativa as notificações push do freelancer
        """
        try:
            freelancer = request.user.freelance
        except Freelance.DoesNotExist:
            return Response(
                {'error': 'Usuário não tem perfil de freelancer'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Desativar notificações
        freelancer.notificacoes_ativas = False
        freelancer.save()
        
        return Response({
            'success': True,
            'message': 'Notificações desativadas com sucesso',
            'notificacoes_ativas': False
        }, status=status.HTTP_200_OK)