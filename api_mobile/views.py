# api_mobile/views.py
from rest_framework import viewsets, status, permissions, serializers
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
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
from django.db.models import Q, Count
import logging

from app_eventos.utils_empresa_ativa import empresa_contexto_api, is_api_empresa_actor
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError as DjangoValidationError

from app_eventos.models import (
    Vaga, Candidatura, Evento, Freelance, Empresa,
    EmpresaContratante, SetorEvento, Funcao, PontoOperacao, FreelancerFuncao,
    RegistroPresencaFreelancer,
)
from app_eventos.services.freelancer_score import aplicar_pontuacao_para_registro
from app_eventos.services.onboarding_freelance import (
    FREELANCE_ONBOARDING_NIVEL2_WRITE_FIELDS,
    calcular_marcadores_onboarding,
    gerar_texto_assistente_nivel2,
    listar_pendentes_nivel2,
)
from app_eventos.services.prestacao_presenca import validar_prestacao_para_registro_presenca
from api_v01.permissions import IsEmpresaOrAdminSistema
from .serializers import (
    VagaSerializer, CandidaturaSerializer, EventoSerializer,
    FreelanceSerializer, FreelanceOnboardingNivel2Serializer,
    EmpresaSerializer, EmpresaContratanteSerializer,
    UserProfileSerializer, PreCadastroFreelancerSerializer,
    PasswordResetSerializer, PasswordResetConfirmSerializer,
    PontoOperacaoSerializer,
    RegistroPresencaFreelancerSerializer,
    RegistroPresencaManualSerializer,
)

User = get_user_model()
logger = logging.getLogger(__name__)


class VagaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Lista vagas ativas no mercado aberto: todas as empresas contratantes expõem
    vagas a todo freelancer autenticado; o queryset não filtra por vínculo
    FreelancerPrestacaoServico. Especialidade: use funcao_id / search (e no app,
    cruzar com as funções do freelancer) — não restringir por empresa aqui.
    """
    serializer_class = VagaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        now = timezone.now()
        today = timezone.localdate()
        queryset = (
            Vaga.objects.filter(
                ativa=True,
            )
            .filter(
                Q(data_limite_candidatura__isnull=True) | Q(data_limite_candidatura__gte=now)
            )
            .filter(
                Q(data_inicio_trabalho__gte=now)
                # Fallback legado: sem data_inicio_trabalho, respeitar data de início do evento.
                | Q(data_inicio_trabalho__isnull=True, setor__evento__data_inicio__gte=today)
                | Q(data_inicio_trabalho__isnull=True, evento__data_inicio__gte=today)
                # Vagas de operação contínua (ponto de operação) podem não ter data de evento.
                | Q(data_inicio_trabalho__isnull=True, ponto_operacao__isnull=False)
            )
            .annotate(_candidaturas_count=Count('candidaturas'))
            .select_related(
                'setor__evento',
                'setor__evento__empresa_contratante',
                'setor__evento__local',
                'evento',
                'evento__empresa_contratante',
                'evento__local',
                'funcao',
                'ponto_operacao',
                'empresa_contratante',
                'empresa_contratante__plano_contratado',
            )
        )
        
        # Filtros
        evento_id = self.request.query_params.get('evento_id')
        funcao_id = self.request.query_params.get('funcao_id')
        cidade = self.request.query_params.get('cidade')
        search = self.request.query_params.get('search')
        
        if evento_id:
            queryset = queryset.filter(
                Q(setor__evento_id=evento_id) | Q(evento_id=evento_id)
            )
        
        if funcao_id:
            queryset = queryset.filter(funcao_id=funcao_id)
        
        if cidade:
            queryset = queryset.filter(
                Q(setor__evento__local__cidade__icontains=cidade) |
                Q(evento__local__cidade__icontains=cidade) |
                Q(ponto_operacao__cidade__icontains=cidade)
            )
        
        if search:
            queryset = queryset.filter(
                Q(titulo__icontains=search) |
                Q(descricao__icontains=search) |
                Q(funcao__nome__icontains=search)
            )

        # Marketplace global para freelancer, mas filtrado por especialidades ativas.
        user = self.request.user
        if getattr(user, 'is_freelancer', False):
            try:
                freelance = user.freelance
            except Freelance.DoesNotExist:
                return Vaga.objects.none()
            funcao_ids = list(
                FreelancerFuncao.objects.filter(freelancer=freelance, ativo=True)
                .values_list('funcao_id', flat=True)
            )
            if not funcao_ids:
                return Vaga.objects.none()
            queryset = queryset.filter(funcao_id__in=funcao_ids)
        
        return queryset.order_by('-data_criacao')


class CandidaturaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar candidaturas
    """
    serializer_class = CandidaturaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        base = Candidatura.objects.select_related(
            'vaga__setor__evento',
            'vaga__setor__evento__empresa_contratante',
            'vaga__evento',
            'vaga__evento__empresa_contratante',
            'vaga__ponto_operacao',
            'vaga__ponto_operacao__empresa_contratante',
            'vaga__funcao',
            'vaga__empresa_contratante',
            'freelance',
        )
        if getattr(user, 'is_freelancer', False):
            try:
                freelance = user.freelance
                return base.filter(freelance=freelance)
            except Freelance.DoesNotExist:
                return Candidatura.objects.none()
        if getattr(user, 'is_admin_sistema', False):
            return base
        if is_api_empresa_actor(self.request):
            emp = empresa_contexto_api(self.request)
            return base.filter(vaga__empresa_contratante=emp)
        return Candidatura.objects.none()
    
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

        if not vaga.pode_candidatar():
            raise serializers.ValidationError(
                "Esta vaga não está mais disponível para candidatura (prazo/turno encerrado)."
            )

        # Freelancer só pode candidatar se possuir a especialidade da vaga.
        if vaga.funcao_id and not FreelancerFuncao.objects.filter(
            freelancer=freelance,
            funcao_id=vaga.funcao_id,
            ativo=True,
        ).exists():
            raise serializers.ValidationError(
                "Você não possui a especialidade exigida para esta vaga."
            )
        
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
        
        if not is_api_empresa_actor(request):
            return Response(
                {'error': 'Apenas utilizadores com escopo de empresa podem aprovar candidaturas.'},
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
        
        if not is_api_empresa_actor(request):
            return Response(
                {'error': 'Apenas utilizadores com escopo de empresa podem rejeitar candidaturas.'},
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


class PontoOperacaoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerir o estabelecimento (ponto de operação) da empresa.
    """
    serializer_class = PontoOperacaoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_empresa_user:
            return PontoOperacao.objects.filter(
                empresa_contratante=user.empresa_contratante
            )
        elif user.is_admin_sistema:
            return PontoOperacao.objects.all()
        return PontoOperacao.objects.none()
    
    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_empresa_user:
            raise serializers.ValidationError("Apenas empresas podem cadastrar estabelecimento")
        if PontoOperacao.objects.filter(empresa_contratante=user.empresa_contratante).exists():
            raise serializers.ValidationError(
                "Já existe estabelecimento para esta empresa; use PATCH ou PUT para atualizar."
            )
        serializer.save(empresa_contratante=user.empresa_contratante)

    def perform_destroy(self, instance):
        if not self.request.user.is_admin_sistema:
            raise serializers.ValidationError(
                "Não é permitido excluir o estabelecimento; cada empresa possui um único ponto."
            )
        return super().perform_destroy(instance)


class FreelanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar freelancers
    """
    serializer_class = FreelanceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = [
        'id',
        'nome_completo',
        'score_confiabilidade',
        'data_ultimo_evento',
        'faltas_com_aviso',
        'faltas_sem_aviso',
    ]
    ordering = ['nome_completo']

    def get_queryset(self):
        user = self.request.user

        if user.is_freelancer:
            try:
                qs = Freelance.objects.filter(usuario=user).select_related('usuario')
            except Freelance.DoesNotExist:
                return Freelance.objects.none()
            return qs

        qs = Freelance.objects.all().select_related('usuario')

        if getattr(user, 'is_empresa_user', False) and user.empresa_contratante_id:
            qs = qs.filter(
                prestacao_servico_empresas__empresa_contratante_id=user.empresa_contratante_id,
                prestacao_servico_empresas__ativo=True,
            ).distinct()
        elif getattr(user, 'is_gestor_grupo', False):
            ec = empresa_contexto_api(self.request)
            if ec:
                qs = qs.filter(
                    prestacao_servico_empresas__empresa_contratante_id=ec.id,
                    prestacao_servico_empresas__ativo=True,
                ).distinct()
            else:
                qs = Freelance.objects.none()

        bloqueado = self.request.query_params.get('bloqueado')
        if bloqueado is not None:
            qs = qs.filter(bloqueado=bloqueado.lower() in ('1', 'true', 'yes'))

        score_min = self.request.query_params.get('score_min')
        score_max = self.request.query_params.get('score_max')
        if score_min is not None and str(score_min).strip() != '':
            try:
                qs = qs.filter(score_confiabilidade__gte=int(score_min))
            except ValueError:
                pass
        if score_max is not None and str(score_max).strip() != '':
            try:
                qs = qs.filter(score_confiabilidade__lte=int(score_max))
            except ValueError:
                pass

        prestacao_empresa = self.request.query_params.get('prestacao_empresa')
        if prestacao_empresa is not None and str(prestacao_empresa).strip() != '':
            if getattr(user, 'is_admin_sistema', False):
                try:
                    eid = int(prestacao_empresa)
                    qs = qs.filter(
                        prestacao_servico_empresas__empresa_contratante_id=eid,
                        prestacao_servico_empresas__ativo=True,
                    ).distinct()
                except ValueError:
                    pass

        return qs
    
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
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            freelance = serializer.save()
            return Response(
                {'message': 'Pré-cadastro realizado com sucesso', 'freelance_id': freelance.id},
                status=status.HTTP_201_CREATED
            )
        except Exception as exc:
            logger.exception('Falha inesperada no pre_cadastro de freelancer')
            return Response(
                {
                    'detail': 'Falha ao processar o pré-cadastro.',
                    'erro': str(exc),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(
        detail=True,
        methods=['post'],
        url_path='registrar-presenca',
        permission_classes=[IsAuthenticated, IsEmpresaOrAdminSistema],
    )
    def registrar_presenca(self, request, pk=None):
        """
        Registo manual de presença/falta; atualiza score no Freelance.
        Apenas utilizadores de empresa ou admin de sistema.
        """
        freelance = super().get_object()
        if freelance is None:
            return Response({'detail': 'Freelancer não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        body = RegistroPresencaManualSerializer(data=request.data)
        body.is_valid(raise_exception=True)
        vd = body.validated_data

        empresa = None
        if getattr(request.user, 'is_empresa_user', False) and request.user.empresa_contratante_id:
            empresa = request.user.empresa_contratante
        elif getattr(request.user, 'is_admin_sistema', False):
            eid = vd.get('empresa_id')
            if eid is not None:
                empresa = get_object_or_404(EmpresaContratante, pk=eid)

        try:
            validar_prestacao_para_registro_presenca(freelance, empresa)
        except DjangoValidationError as exc:
            return Response(
                {'detail': list(exc.messages) if hasattr(exc, 'messages') else [str(exc)]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        registro = RegistroPresencaFreelancer.objects.create(
            freelance=freelance,
            empresa=empresa,
            data=vd['data'],
            status=vd['status'],
            observacao=vd.get('observacao') or None,
        )
        aplicar_pontuacao_para_registro(registro.id)
        freelance.refresh_from_db()
        return Response(
            {
                'registro': RegistroPresencaFreelancerSerializer(registro).data,
                'freelance': FreelanceSerializer(freelance).data,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=['get'],
        url_path='historico-presenca',
        permission_classes=[IsAuthenticated],
    )
    def historico_presenca(self, request, pk=None):
        freelance = super().get_object()
        if freelance is None:
            return Response({'detail': 'Freelancer não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        qs = RegistroPresencaFreelancer.objects.filter(freelance=freelance).select_related('empresa')
        user = request.user
        if getattr(user, 'is_freelancer', False):
            pass
        elif getattr(user, 'is_empresa_user', False) and user.empresa_contratante_id:
            qs = qs.filter(empresa_id=user.empresa_contratante_id)
        elif getattr(user, 'is_admin_sistema', False):
            pass
        else:
            return Response({'detail': 'Sem permissão.'}, status=status.HTTP_403_FORBIDDEN)

        qs = qs.order_by('-data', '-created_at')
        page = self.paginate_queryset(qs)
        ser = RegistroPresencaFreelancerSerializer(page if page is not None else qs, many=True)
        if page is not None:
            return self.get_paginated_response(ser.data)
        return Response(ser.data)

    @action(
        detail=False,
        methods=['get', 'patch'],
        url_path='onboarding',
        permission_classes=[IsAuthenticated],
    )
    def onboarding(self, request):
        """
        Nível 2: estado do onboarding + (PATCH) complemento de dados pessoais/endereço
        sem substituir PUT geral de /freelancers/{id}/.
        Apenas o próprio freelancer (autenticado como freelancer) pode acessar.
        """
        if not getattr(request.user, 'is_freelancer', False):
            return Response(
                {'detail': 'Apenas freelancers.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            fl = request.user.freelance
        except Freelance.DoesNotExist:
            return Response(
                {'detail': 'Perfil de freelancer não encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        if request.method == 'GET':
            pendentes = listar_pendentes_nivel2(fl)
            return Response(
                {
                    'onboarding': calcular_marcadores_onboarding(fl),
                    'nivel2_campos_permitidos': list(FREELANCE_ONBOARDING_NIVEL2_WRITE_FIELDS),
                    'perfil_nivel2': FreelanceOnboardingNivel2Serializer(fl).data,
                    'prompt_suporte_nivel2': gerar_texto_assistente_nivel2(
                        fl.nome_completo, pendentes=pendentes
                    ),
                }
            )
        ser = FreelanceOnboardingNivel2Serializer(
            fl, data=request.data, partial=True, context={'request': request}
        )
        ser.is_valid(raise_exception=True)
        ser.save()
        fl.refresh_from_db()
        pendentes = listar_pendentes_nivel2(fl)
        return Response(
            {
                'success': True,
                'onboarding': calcular_marcadores_onboarding(fl),
                'perfil_nivel2': FreelanceOnboardingNivel2Serializer(fl).data,
                'prompt_suporte_nivel2': gerar_texto_assistente_nivel2(
                    fl.nome_completo, pendentes=pendentes
                ),
            }
        )


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