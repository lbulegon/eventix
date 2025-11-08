# api_v01/views.py
from rest_framework import viewsets, mixins, permissions, status, generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db import transaction
from django.utils import timezone
from app_eventos.models import Vaga, Candidatura, ContratoFreelance, Freelance, User, EmpresaContratante, Evento, CategoriaFinanceira, DespesaEvento, ReceitaEvento, Fornecedor
from ..serializers.serializers import (
    VagaSerializer, CandidaturaCreateSerializer, CandidaturaListSerializer,
    ContratoFreelanceSerializer, LoginSerializer,
    UserRegistrationSerializer, UserProfileSerializer, EmpresaRegistrationSerializer,
    RegistroUnicoSerializer, CategoriaFinanceiraSerializer, DespesaEventoSerializer, ReceitaEventoSerializer, FluxoCaixaEventoSerializer,
    FornecedorSerializer, FornecedorCreateSerializer, FornecedorUpdateSerializer
)
from ..permissions import IsFreelancer, IsEmpresaUser, IsAdminSistema
from ..filters import EmpresaScopeFilterBackend


class VagaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Freelancer: lista vagas ativas.
    Empresa/Admin: podem ver (e poderiam administrar em outro endpoint, se quiser).
    """
    queryset = Vaga.objects.select_related("setor", "setor__evento", "setor__evento__empresa_contratante")
    serializer_class = VagaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter, EmpresaScopeFilterBackend]
    filterset_fields = ["ativa"]
    search_fields = ["titulo", "descricao", "setor__evento__nome"]
    ordering_fields = ["remuneracao", "id"]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if getattr(user, "is_freelancer", False):
            return qs.filter(ativa=True, setor__evento__ativo=True)
        return qs  # empresa/admin: filtragem extra cai no filter backend

class CandidaturaViewSet(mixins.CreateModelMixin,
                         mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         viewsets.GenericViewSet):
    """
    Freelancer:
      - POST /candidaturas { "vaga": <id> } → cria pré-cadastro
      - GET /candidaturas → vê suas candidaturas
    Empresa/Admin:
      - GET /candidaturas → vê candidaturas da sua empresa (via escopo)
    """
    queryset = Candidatura.objects.select_related(
        "vaga", "vaga__setor", "vaga__setor__evento", "freelance", "freelance__usuario"
    )
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter, EmpresaScopeFilterBackend]
    search_fields = ["vaga__titulo", "freelance__nome_completo"]
    ordering_fields = ["data_candidatura", "id"]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsFreelancer()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CandidaturaCreateSerializer
        return CandidaturaListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if getattr(user, "is_freelancer", False):
            # apenas as candidaturas do próprio freelancer
            try:
                f = Freelance.objects.get(usuario=user)
                return qs.filter(freelance=f)
            except Freelance.DoesNotExist:
                return qs.none()
        if getattr(user, "is_admin_sistema", False):
            return qs
        if getattr(user, "is_empresa_user", False):
            # candidaturas de vagas dos eventos da empresa do usuário
            return qs.filter(vaga__setor__evento__empresa_contratante=user.empresa_contratante)
        return qs.none()

class ContratoFreelanceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Freelancer: vê seus contratos.
    Empresa/Admin: vê contratos da sua empresa (escopo).
    """
    queryset = ContratoFreelance.objects.select_related(
        "vaga", "vaga__setor", "vaga__setor__evento", "freelance", "freelance__usuario"
    )
    serializer_class = ContratoFreelanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter, EmpresaScopeFilterBackend]
    search_fields = ["vaga__titulo", "freelance__nome_completo"]
    ordering_fields = ["data_contratacao", "id"]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if getattr(user, "is_freelancer", False):
            try:
                f = Freelance.objects.get(usuario=user)
                return qs.filter(freelance=f)
            except Freelance.DoesNotExist:
                return qs.none()
        if getattr(user, "is_admin_sistema", False):
            return qs
        if getattr(user, "is_empresa_user", False):
            return qs.filter(vaga__setor__evento__empresa_contratante=user.empresa_contratante)
        return qs.none()


@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def login_unico(request):
    """
    Login único para todos os tipos de usuário
    """
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        user = authenticate(username=username, password=password)
        
        if user and user.is_active and user.ativo:
            # Atualiza último acesso
            user.data_ultimo_acesso = timezone.now()
            user.save(update_fields=['data_ultimo_acesso'])
            
            # Gera tokens JWT
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'success': True,
                'message': 'Login realizado com sucesso!',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'tipo_usuario': user.tipo_usuario,
                    'tipo_usuario_display': user.get_user_type_display_name(),
                    'is_freelancer': user.is_freelancer,
                    'is_empresa_user': user.is_empresa_user,
                    'is_admin_sistema': user.is_admin_sistema,
                    'empresa_contratante': user.empresa_contratante.nome_fantasia if user.empresa_contratante else None,
                    'dashboard_url': user.get_dashboard_url(),
                },
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                }
            })
        else:
            return Response({
                'success': False,
                'message': 'Credenciais inválidas ou usuário inativo.'
            }, status=status.HTTP_401_UNAUTHORIZED)
    
    return Response({
        'success': False,
        'message': 'Dados inválidos.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def registro_freelancer(request):
    """
    Registro de freelancer
    """
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        try:
            with transaction.atomic():
                # Cria o usuário
                user_data = serializer.validated_data.copy()
                user_data['tipo_usuario'] = 'freelancer'
                
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password'],
                    first_name=user_data.get('first_name', ''),
                    last_name=user_data.get('last_name', ''),
                    tipo_usuario='freelancer'
                )
                
                # Cria o perfil de freelancer
                Freelance.objects.create(
                    usuario=user,
                    nome_completo=user_data.get('nome_completo', f"{user.first_name} {user.last_name}"),
                    telefone=user_data.get('telefone', ''),
                    cpf=user_data.get('cpf', '')
                )
                
                # Gera tokens
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    'success': True,
                    'message': 'Freelancer registrado com sucesso!',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'tipo_usuario': user.tipo_usuario,
                        'tipo_usuario_display': user.get_user_type_display_name(),
                        'is_freelancer': user.is_freelancer,
                        'dashboard_url': user.get_dashboard_url(),
                    },
                    'tokens': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh),
                    }
                })
                
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Erro ao criar conta: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'success': False,
        'message': 'Dados inválidos.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def registro_empresa(request):
    """
    Registro de empresa contratante
    """
    serializer = EmpresaRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        try:
            with transaction.atomic():
                # Cria a empresa
                empresa_data = serializer.validated_data['empresa']
                empresa = EmpresaContratante.objects.create(**empresa_data)
                
                # Cria o usuário administrador da empresa
                user_data = serializer.validated_data['usuario']
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password'],
                    first_name=user_data.get('first_name', ''),
                    last_name=user_data.get('last_name', ''),
                    tipo_usuario='admin_empresa',
                    empresa_contratante=empresa
                )
                
                # Gera tokens
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    'success': True,
                    'message': 'Empresa registrada com sucesso!',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'tipo_usuario': user.tipo_usuario,
                        'tipo_usuario_display': user.get_user_type_display_name(),
                        'is_empresa_user': user.is_empresa_user,
                        'empresa_contratante': empresa.nome_fantasia,
                        'dashboard_url': user.get_dashboard_url(),
                    },
                    'empresa': {
                        'id': empresa.id,
                        'nome_fantasia': empresa.nome_fantasia,
                        'cnpj': empresa.cnpj,
                    },
                    'tokens': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh),
                    }
                })
                
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Erro ao criar empresa: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'success': False,
        'message': 'Dados inválidos.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def perfil_usuario(request):
    """
    Retorna o perfil do usuário logado
    """
    user = request.user
    
    # Atualiza último acesso
    user.data_ultimo_acesso = timezone.now()
    user.save(update_fields=['data_ultimo_acesso'])
    
    serializer = UserProfileSerializer(user)
    
    return Response({
        'success': True,
        'user': serializer.data,
        'dashboard_url': user.get_dashboard_url(),
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    Logout do usuário
    """
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        return Response({
            'success': True,
            'message': 'Logout realizado com sucesso!'
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': 'Erro ao fazer logout.'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verificar_tipo_usuario(request):
    """
    Verifica o tipo de usuário e retorna informações específicas
    """
    user = request.user
    
    response_data = {
        'success': True,
        'user_type': user.tipo_usuario,
        'user_type_display': user.get_user_type_display_name(),
        'is_freelancer': user.is_freelancer,
        'is_empresa_user': user.is_empresa_user,
        'is_admin_sistema': user.is_admin_sistema,
        'empresa_contratante': user.empresa_contratante.nome_fantasia if user.empresa_contratante else None,
        'empresa_owner': user.empresa_owner.nome_fantasia if user.empresa_owner else None,
        'dashboard_url': user.get_dashboard_url(),
    }
    
    # Adiciona informações específicas por tipo
    if user.is_freelancer:
        try:
            freelance = user.freelance
            response_data['freelance_info'] = {
                'id': freelance.id,
                'nome_completo': freelance.nome_completo,
                'cpf': freelance.cpf,
                'cadastro_completo': freelance.cadastro_completo,
            }
        except Freelance.DoesNotExist:
            response_data['freelance_info'] = None
    
    elif user.is_empresa_user:
        if user.empresa_contratante:
            response_data['empresa_info'] = {
                'id': user.empresa_contratante.id,
                'nome_fantasia': user.empresa_contratante.nome_fantasia,
                'cnpj': user.empresa_contratante.cnpj,
                'ativo': user.empresa_contratante.ativo,
            }
    
    return Response(response_data)


@api_view(['GET'])
@permission_classes([AllowAny])
def listar_empresas(request):
    """Lista empresas ativas para seleção"""
    empresas = EmpresaContratante.objects.filter(ativo=True)
    data = []
    
    for empresa in empresas:
        data.append({
            'id': empresa.id,
            'nome_fantasia': empresa.nome_fantasia,
            'razao_social': empresa.razao_social,
            'cnpj': empresa.cnpj,
            'email': empresa.email
        })
    
    return Response({
        'success': True,
        'empresas': data
    })


# Views para o sistema financeiro
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def categorias_financeiras(request):
    """Lista categorias financeiras da empresa do usuário"""
    user = request.user
    empresa = user.empresa_owner
    
    if not empresa:
        return Response({
            'success': False,
            'message': 'Usuário não possui empresa associada.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    categorias = CategoriaFinanceira.objects.filter(
        empresa_contratante=empresa,
        ativo=True
    )
    
    serializer = CategoriaFinanceiraSerializer(categorias, many=True)
    
    return Response({
        'success': True,
        'categorias': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def despesas_evento(request, evento_id):
    """Lista despesas de um evento específico"""
    try:
        evento = Evento.objects.get(id=evento_id)
        
        # Verificar permissão de acesso ao evento
        user = request.user
        if not user.is_admin_sistema and evento.empresa_contratante != user.empresa_owner:
            return Response({
                'success': False,
                'message': 'Acesso negado a este evento.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        despesas = evento.despesas.all()
        serializer = DespesaEventoSerializer(despesas, many=True)
        
        return Response({
            'success': True,
            'despesas': serializer.data
        })
        
    except Evento.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Evento não encontrado.'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def criar_despesa(request):
    """Cria uma nova despesa para um evento"""
    serializer = DespesaEventoSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            evento = Evento.objects.get(id=serializer.validated_data['evento'].id)
            
            # Verificar permissão de acesso ao evento
            user = request.user
            if not user.is_admin_sistema and evento.empresa_contratante != user.empresa_owner:
                return Response({
                    'success': False,
                    'message': 'Acesso negado a este evento.'
                }, status=status.HTTP_403_FORBIDDEN)
            
            despesa = serializer.save()
            
            return Response({
                'success': True,
                'message': 'Despesa criada com sucesso.',
                'despesa': DespesaEventoSerializer(despesa).data
            }, status=status.HTTP_201_CREATED)
            
        except Evento.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Evento não encontrado.'
            }, status=status.HTTP_404_NOT_FOUND)
    
    return Response({
        'success': False,
        'message': 'Dados inválidos.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def atualizar_despesa(request, despesa_id):
    """Atualiza uma despesa existente"""
    try:
        despesa = DespesaEvento.objects.get(id=despesa_id)
        
        # Verificar permissão de acesso
        user = request.user
        if not user.is_admin_sistema and despesa.evento.empresa_contratante != user.empresa_owner:
            return Response({
                'success': False,
                'message': 'Acesso negado a esta despesa.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = DespesaEventoSerializer(despesa, data=request.data, partial=True)
        
        if serializer.is_valid():
            despesa = serializer.save()
            
            return Response({
                'success': True,
                'message': 'Despesa atualizada com sucesso.',
                'despesa': DespesaEventoSerializer(despesa).data
            })
        
        return Response({
            'success': False,
            'message': 'Dados inválidos.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except DespesaEvento.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Despesa não encontrada.'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def receitas_evento(request, evento_id):
    """Lista receitas de um evento específico"""
    try:
        evento = Evento.objects.get(id=evento_id)
        
        # Verificar permissão de acesso ao evento
        user = request.user
        if not user.is_admin_sistema and evento.empresa_contratante != user.empresa_owner:
            return Response({
                'success': False,
                'message': 'Acesso negado a este evento.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        receitas = evento.receitas.all()
        serializer = ReceitaEventoSerializer(receitas, many=True)
        
        return Response({
            'success': True,
            'receitas': serializer.data
        })
        
    except Evento.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Evento não encontrado.'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def criar_receita(request):
    """Cria uma nova receita para um evento"""
    serializer = ReceitaEventoSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            evento = Evento.objects.get(id=serializer.validated_data['evento'].id)
            
            # Verificar permissão de acesso ao evento
            user = request.user
            if not user.is_admin_sistema and evento.empresa_contratante != user.empresa_owner:
                return Response({
                    'success': False,
                    'message': 'Acesso negado a este evento.'
                }, status=status.HTTP_403_FORBIDDEN)
            
            receita = serializer.save()
            
            return Response({
                'success': True,
                'message': 'Receita criada com sucesso.',
                'receita': ReceitaEventoSerializer(receita).data
            }, status=status.HTTP_201_CREATED)
            
        except Evento.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Evento não encontrado.'
            }, status=status.HTTP_404_NOT_FOUND)
    
    return Response({
        'success': False,
        'message': 'Dados inválidos.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def atualizar_receita(request, receita_id):
    """Atualiza uma receita existente"""
    try:
        receita = ReceitaEvento.objects.get(id=receita_id)
        
        # Verificar permissão de acesso
        user = request.user
        if not user.is_admin_sistema and receita.evento.empresa_contratante != user.empresa_owner:
            return Response({
                'success': False,
                'message': 'Acesso negado a esta receita.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ReceitaEventoSerializer(receita, data=request.data, partial=True)
        
        if serializer.is_valid():
            receita = serializer.save()
            
            return Response({
                'success': True,
                'message': 'Receita atualizada com sucesso.',
                'receita': ReceitaEventoSerializer(receita).data
            })
        
        return Response({
            'success': False,
            'message': 'Dados inválidos.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except ReceitaEvento.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Receita não encontrada.'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fluxo_caixa_evento(request, evento_id):
    """Retorna o resumo do fluxo de caixa de um evento"""
    try:
        evento = Evento.objects.get(id=evento_id)
        
        # Verificar permissão de acesso ao evento
        user = request.user
        if not user.is_admin_sistema and evento.empresa_contratante != user.empresa_owner:
            return Response({
                'success': False,
                'message': 'Acesso negado a este evento.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        data = {
            'evento_id': evento.id,
            'evento_nome': evento.nome,
            'total_despesas': evento.total_despesas,
            'total_receitas': evento.total_receitas,
            'saldo_financeiro': evento.saldo_financeiro,
            'despesas_pagas': evento.despesas_pagas,
            'receitas_recebidas': evento.receitas_recebidas,
            'saldo_realizado': evento.saldo_realizado,
            'despesas_pendentes': evento.despesas_pendentes,
            'receitas_pendentes': evento.receitas_pendentes,
            'despesas_atrasadas_count': evento.despesas_atrasadas.count(),
            'receitas_atrasadas_count': evento.receitas_atrasadas.count(),
        }
        
        serializer = FluxoCaixaEventoSerializer(data)
        
        return Response({
            'success': True,
            'fluxo_caixa': serializer.data
        })
        
    except Evento.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Evento não encontrado.'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fluxo_caixa_empresa(request):
    """Retorna o resumo do fluxo de caixa de todos os eventos da empresa"""
    user = request.user
    empresa = user.empresa_owner
    
    if not empresa:
        return Response({
            'success': False,
            'message': 'Usuário não possui empresa associada.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    eventos = Evento.objects.filter(empresa_contratante=empresa, ativo=True)
    resumos = []
    
    for evento in eventos:
        data = {
            'evento_id': evento.id,
            'evento_nome': evento.nome,
            'total_despesas': evento.total_despesas,
            'total_receitas': evento.total_receitas,
            'saldo_financeiro': evento.saldo_financeiro,
            'despesas_pagas': evento.despesas_pagas,
            'receitas_recebidas': evento.receitas_recebidas,
            'saldo_realizado': evento.saldo_realizado,
            'despesas_pendentes': evento.despesas_pendentes,
            'receitas_pendentes': evento.receitas_pendentes,
            'despesas_atrasadas_count': evento.despesas_atrasadas.count(),
            'receitas_atrasadas_count': evento.receitas_atrasadas.count(),
        }
        resumos.append(data)
    
    # Calcular totais da empresa
    total_despesas = sum(r['total_despesas'] for r in resumos)
    total_receitas = sum(r['total_receitas'] for r in resumos)
    total_saldo = sum(r['saldo_financeiro'] for r in resumos)
    
    return Response({
        'success': True,
        'eventos': resumos,
        'totais_empresa': {
            'total_despesas': total_despesas,
            'total_receitas': total_receitas,
            'saldo_financeiro': total_saldo,
        }
    })


# Views para Fornecedores
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_fornecedores(request):
    """Lista fornecedores da empresa do usuário"""
    user = request.user
    empresa = user.empresa_owner
    
    if not empresa:
        return Response({
            'success': False,
            'message': 'Usuário não possui empresa associada.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Filtros opcionais
    tipo_fornecedor = request.GET.get('tipo_fornecedor')
    ativo = request.GET.get('ativo')
    
    fornecedores = Fornecedor.objects.filter(empresa_contratante=empresa)
    
    if tipo_fornecedor:
        fornecedores = fornecedores.filter(tipo_fornecedor=tipo_fornecedor)
    
    if ativo is not None:
        fornecedores = fornecedores.filter(ativo=ativo.lower() == 'true')
    
    serializer = FornecedorSerializer(fornecedores, many=True)
    
    return Response({
        'success': True,
        'fornecedores': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def detalhes_fornecedor(request, fornecedor_id):
    """Retorna detalhes de um fornecedor específico"""
    try:
        fornecedor = Fornecedor.objects.get(id=fornecedor_id)
        
        # Verificar permissão de acesso
        user = request.user
        if not user.is_admin_sistema and fornecedor.empresa_contratante != user.empresa_owner:
            return Response({
                'success': False,
                'message': 'Acesso negado a este fornecedor.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = FornecedorSerializer(fornecedor)
        
        return Response({
            'success': True,
            'fornecedor': serializer.data
        })
        
    except Fornecedor.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Fornecedor não encontrado.'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def criar_fornecedor(request):
    """Cria um novo fornecedor"""
    serializer = FornecedorCreateSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        fornecedor = serializer.save()
        
        return Response({
            'success': True,
            'message': 'Fornecedor criado com sucesso.',
            'fornecedor': FornecedorSerializer(fornecedor).data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'message': 'Dados inválidos.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def atualizar_fornecedor(request, fornecedor_id):
    """Atualiza um fornecedor existente"""
    try:
        fornecedor = Fornecedor.objects.get(id=fornecedor_id)
        
        # Verificar permissão de acesso
        user = request.user
        if not user.is_admin_sistema and fornecedor.empresa_contratante != user.empresa_owner:
            return Response({
                'success': False,
                'message': 'Acesso negado a este fornecedor.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = FornecedorUpdateSerializer(fornecedor, data=request.data, partial=True)
        
        if serializer.is_valid():
            fornecedor = serializer.save()
            
            return Response({
                'success': True,
                'message': 'Fornecedor atualizado com sucesso.',
                'fornecedor': FornecedorSerializer(fornecedor).data
            })
        
        return Response({
            'success': False,
            'message': 'Dados inválidos.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Fornecedor.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Fornecedor não encontrado.'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fornecedor_despesas(request, fornecedor_id):
    """Lista despesas de um fornecedor específico"""
    try:
        fornecedor = Fornecedor.objects.get(id=fornecedor_id)
        
        # Verificar permissão de acesso
        user = request.user
        if not user.is_admin_sistema and fornecedor.empresa_contratante != user.empresa_owner:
            return Response({
                'success': False,
                'message': 'Acesso negado a este fornecedor.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        despesas = fornecedor.despesas.all()
        serializer = DespesaEventoSerializer(despesas, many=True)
        
        return Response({
            'success': True,
            'fornecedor': FornecedorSerializer(fornecedor).data,
            'despesas': serializer.data
        })
        
    except Fornecedor.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Fornecedor não encontrado.'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def registro_unico(request):
    """
    Registro único para qualquer tipo de usuário
    """
    serializer = RegistroUnicoSerializer(data=request.data)
    if serializer.is_valid():
        try:
            with transaction.atomic():
                data = serializer.validated_data
                tipo_usuario = data['tipo_usuario']
                
                # Cria ou obtém a empresa se necessário
                empresa = None
                if tipo_usuario in ['admin_empresa', 'operador_empresa']:
                    if data.get('empresa_id'):
                        empresa = EmpresaContratante.objects.get(id=data['empresa_id'])
                    elif data.get('empresa_nova'):
                        empresa = EmpresaContratante.objects.create(**data['empresa_nova'])
                elif tipo_usuario == 'freelancer':
                    # Freelancers são sempre vinculados à Eventix
                    empresa = EmpresaContratante.objects.filter(nome_fantasia__icontains='Eventix').first()
                
                # Cria o usuário
                user = User.objects.create_user(
                    username=data['username'],
                    email=data['email'],
                    password=data['password'],
                    first_name=data.get('first_name', ''),
                    last_name=data.get('last_name', ''),
                    tipo_usuario=tipo_usuario,
                    empresa_contratante=empresa
                )
                
                # Cria perfil específico se necessário
                if tipo_usuario == 'freelancer':
                    Freelance.objects.create(
                        usuario=user,
                        nome_completo=data.get('nome_completo', f"{user.first_name} {user.last_name}"),
                        telefone=data.get('telefone', ''),
                        cpf=data.get('cpf', '')
                    )
                
                # Gera tokens
                refresh = RefreshToken.for_user(user)
                
                response_data = {
                    'success': True,
                    'message': f'{user.get_user_type_display_name()} registrado com sucesso!',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'tipo_usuario': user.tipo_usuario,
                        'tipo_usuario_display': user.get_user_type_display_name(),
                        'is_freelancer': user.is_freelancer,
                        'is_empresa_user': user.is_empresa_user,
                        'is_admin_sistema': user.is_admin_sistema,
                        'empresa_contratante': empresa.nome_fantasia if empresa else None,
                        'empresa_owner': user.empresa_owner.nome_fantasia if user.empresa_owner else None,
                        'dashboard_url': user.get_dashboard_url(),
                    },
                    'tokens': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh),
                    }
                }
                
                # Adiciona informações da empresa se foi criada
                if empresa and data.get('empresa_nova'):
                    response_data['empresa'] = {
                        'id': empresa.id,
                        'nome_fantasia': empresa.nome_fantasia,
                        'cnpj': empresa.cnpj,
                    }
                
                return Response(response_data)
                
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Erro ao criar conta: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'success': False,
        'message': 'Dados inválidos.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)
