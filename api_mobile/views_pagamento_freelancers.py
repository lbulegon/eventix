from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import F
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from rest_framework import generics, serializers, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_eventos.services.atribuicao_vaga_direta import atribuir_freelancer_a_vaga_direto
from app_eventos.services.tarifa_diaria_turno import parse_hora, resolver_tarifa_diaria

from app_eventos.models import ContratoFreelance, Freelance, Funcao, PontoOperacao, Vaga
from app_eventos.models_freelancer_empresa import FreelancerPrestacaoServico
from app_eventos.models_pagamento_freelancers import (
    FichamentoSemanaFreelancer,
    LancamentoPagoDiarioFreelancer,
    LancamentoDescontoFreelancer,
)
from .serializers_pagamento_freelancers import (
    AtribuicaoFreelancerVagaDiretaSerializer,
    ContratoPagamentoSerializer,
    FichamentoSemanaFreelancerSerializer,
    FreelancerPrestacaoServicoSerializer,
    LancamentoPagoDiarioFreelancerSerializer,
    LancamentoDescontoFreelancerSerializer,
    VagaDisponivelPagamentoSerializer,
)


def _base_fichamento_queryset(user):
    if getattr(user, 'is_admin_sistema', False):
        return FichamentoSemanaFreelancer.objects.select_related(
            'empresa_contratante', 'ponto_operacao'
        )
    if getattr(user, 'is_empresa_user', False) and user.empresa_contratante:
        return FichamentoSemanaFreelancer.objects.filter(
            empresa_contratante=user.empresa_contratante
        ).select_related('empresa_contratante', 'ponto_operacao')
    return FichamentoSemanaFreelancer.objects.none()


class FichamentoSemanaFreelancerViewSet(viewsets.ModelViewSet):
    """
    CRUD de fichamentos semanais (7 dias; dia de fechamento configurável) por tenant e estabelecimento.
    """
    serializer_class = FichamentoSemanaFreelancerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = _base_fichamento_queryset(self.request.user)
        ponto_id = self.request.query_params.get('ponto_operacao')
        if ponto_id:
            qs = qs.filter(ponto_operacao_id=ponto_id)
        return qs

    def perform_create(self, serializer):
        user = self.request.user
        if not getattr(user, 'is_empresa_user', False) and not getattr(user, 'is_admin_sistema', False):
            raise serializers.ValidationError('Apenas usuários da empresa ou administrador do sistema podem criar fichamentos.')
        ponto = serializer.validated_data.get('ponto_operacao')
        if getattr(user, 'is_empresa_user', False) and user.empresa_contratante:
            serializer.save(empresa_contratante=user.empresa_contratante)
        elif getattr(user, 'is_admin_sistema', False):
            if not ponto:
                raise serializers.ValidationError({'ponto_operacao': 'Obrigatório para definir o tenant.'})
            serializer.save(empresa_contratante=ponto.empresa_contratante)
        else:
            raise serializers.ValidationError('Sem permissão para criar fichamentos.')

    def perform_update(self, serializer):
        user = self.request.user
        if not getattr(user, 'is_empresa_user', False) and not getattr(user, 'is_admin_sistema', False):
            raise serializers.ValidationError('Sem permissão para alterar fichamentos.')
        serializer.save()


class LancamentoPagoDiarioFreelancerViewSet(viewsets.ModelViewSet):
    serializer_class = LancamentoPagoDiarioFreelancerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        base = LancamentoPagoDiarioFreelancer.objects.select_related(
            'fichamento', 'freelance', 'contrato_freelance', 'contrato_freelance__vaga'
        )
        if getattr(user, 'is_admin_sistema', False):
            qs = base
        elif getattr(user, 'is_empresa_user', False) and user.empresa_contratante:
            qs = base.filter(fichamento__empresa_contratante=user.empresa_contratante)
        else:
            return LancamentoPagoDiarioFreelancer.objects.none()

        fichamento_id = self.request.query_params.get('fichamento')
        if fichamento_id:
            qs = qs.filter(fichamento_id=fichamento_id)
        return qs

    def perform_create(self, serializer):
        user = self.request.user
        if not getattr(user, 'is_empresa_user', False) and not getattr(user, 'is_admin_sistema', False):
            raise serializers.ValidationError('Sem permissão.')
        serializer.save()

    def perform_update(self, serializer):
        user = self.request.user
        if not getattr(user, 'is_empresa_user', False) and not getattr(user, 'is_admin_sistema', False):
            raise serializers.ValidationError('Sem permissão.')
        serializer.save()


class LancamentoDescontoFreelancerViewSet(viewsets.ModelViewSet):
    serializer_class = LancamentoDescontoFreelancerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        base = LancamentoDescontoFreelancer.objects.select_related(
            'fichamento', 'freelance', 'contrato_freelance', 'contrato_freelance__vaga'
        )
        if getattr(user, 'is_admin_sistema', False):
            qs = base
        elif getattr(user, 'is_empresa_user', False) and user.empresa_contratante:
            qs = base.filter(fichamento__empresa_contratante=user.empresa_contratante)
        else:
            return LancamentoDescontoFreelancer.objects.none()

        fichamento_id = self.request.query_params.get('fichamento')
        if fichamento_id:
            qs = qs.filter(fichamento_id=fichamento_id)
        return qs

    def perform_create(self, serializer):
        user = self.request.user
        if not getattr(user, 'is_empresa_user', False) and not getattr(user, 'is_admin_sistema', False):
            raise serializers.ValidationError('Sem permissão.')
        serializer.save()

    def perform_update(self, serializer):
        user = self.request.user
        if not getattr(user, 'is_empresa_user', False) and not getattr(user, 'is_admin_sistema', False):
            raise serializers.ValidationError('Sem permissão.')
        serializer.save()


class VagasDisponiveisPagamentoListView(generics.ListAPIView):
    """
    Vagas com vagas_disponiveis > 0 no ponto de operação (para contexto de pagamento / candidatura).
    Query: ?ponto_operacao=<id> obrigatório. Empresa: ?todas=1 inclui não publicadas.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = VagaDisponivelPagamentoSerializer

    def get_queryset(self):
        ponto_id = self.request.query_params.get('ponto_operacao')
        user = self.request.user
        if not ponto_id:
            return Vaga.objects.none()

        todas = self.request.query_params.get('todas') == '1'
        base = Vaga.objects.filter(ponto_operacao_id=ponto_id).filter(
            quantidade__gt=F('quantidade_preenchida'),
            ativa=True,
        )

        if getattr(user, 'is_admin_sistema', False):
            qs = base
        elif getattr(user, 'is_empresa_user', False) and user.empresa_contratante:
            qs = base.filter(empresa_contratante=user.empresa_contratante)
        elif getattr(user, 'is_freelancer', False):
            qs = base.filter(publicada=True, empresa_contratante__ativo=True)
        else:
            return Vaga.objects.none()

        if not todas or not getattr(user, 'is_empresa_user', False):
            qs = qs.filter(publicada=True)
        return qs.select_related('funcao', 'ponto_operacao').order_by('-data_criacao')


class SugerirTarifaDiariaView(APIView):
    """
    Sugere valor de diária (dia / noite / noite especial) para estabelecimento + função + data + hora de início.

    Query: ``ponto_operacao``, ``funcao``, ``data`` (YYYY-MM-DD), ``hora_inicio`` (HH:MM, default 08:00).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        ponto_id = request.query_params.get('ponto_operacao')
        funcao_id = request.query_params.get('funcao')
        data_str = request.query_params.get('data')
        hora_str = request.query_params.get('hora_inicio', '08:00')
        if not ponto_id or not funcao_id or not data_str:
            return Response(
                {'detail': 'Informe ponto_operacao, funcao e data (YYYY-MM-DD).'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        d = parse_date(data_str)
        if not d:
            return Response({'detail': 'Data inválida. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            hora = parse_hora(hora_str)
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        if getattr(user, 'is_admin_sistema', False):
            ponto = get_object_or_404(PontoOperacao.objects.select_related('empresa_contratante'), pk=ponto_id)
        elif getattr(user, 'is_empresa_user', False) and user.empresa_contratante:
            ponto = get_object_or_404(
                PontoOperacao.objects.select_related('empresa_contratante'),
                pk=ponto_id,
                empresa_contratante=user.empresa_contratante,
            )
        else:
            return Response({'detail': 'Sem permissão.'}, status=status.HTTP_403_FORBIDDEN)

        if getattr(user, 'is_admin_sistema', False):
            funcao = get_object_or_404(Funcao, pk=funcao_id)
        else:
            funcao = get_object_or_404(
                Funcao,
                pk=funcao_id,
                empresa_contratante=user.empresa_contratante,
            )

        if funcao.empresa_contratante_id and funcao.empresa_contratante_id != ponto.empresa_contratante_id:
            return Response(
                {'detail': 'Função e estabelecimento devem ser da mesma empresa.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        out = resolver_tarifa_diaria(
            empresa_contratante_id=ponto.empresa_contratante_id,
            ponto_operacao_id=int(ponto_id),
            funcao_id=int(funcao_id),
            data=d,
            hora_inicio=hora,
        )
        return Response(out)


class ContratosPagamentoListView(generics.ListAPIView):
    """
    Contratos ativos (freelancer contratado na vaga). Filtra por estabelecimento e/ou freelancer.
    Query: ?ponto_operacao=<id> opcional, ?freelance=<id> opcional (empresa/admin).
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ContratoPagamentoSerializer

    def get_queryset(self):
        user = self.request.user
        ponto_id = self.request.query_params.get('ponto_operacao')
        freelance_id = self.request.query_params.get('freelance')

        qs = ContratoFreelance.objects.filter(status='ativo').select_related(
            'vaga', 'freelance', 'vaga__ponto_operacao'
        )

        if getattr(user, 'is_freelancer', False):
            try:
                fl = user.freelance
            except Freelance.DoesNotExist:
                return ContratoFreelance.objects.none()
            qs = qs.filter(freelance=fl)
        elif getattr(user, 'is_empresa_user', False) and user.empresa_contratante:
            qs = qs.filter(vaga__empresa_contratante=user.empresa_contratante)
        elif getattr(user, 'is_admin_sistema', False):
            pass
        else:
            return ContratoFreelance.objects.none()

        if ponto_id:
            qs = qs.filter(vaga__ponto_operacao_id=ponto_id)
        if freelance_id and (getattr(user, 'is_empresa_user', False) or getattr(user, 'is_admin_sistema', False)):
            qs = qs.filter(freelance_id=freelance_id)

        return qs.order_by('-data_contratacao')


class AtribuirFreelancerVagaDiretoView(APIView):
    """
    Atribui um freelancer a uma vaga de ponto de operação (estabelecimento) sem candidatura.
    Cria ContratoFreelance ativo e incrementa o preenchimento da vaga.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        if not (
            getattr(user, 'is_empresa_user', False) or getattr(user, 'is_admin_sistema', False)
        ):
            return Response(
                {'detail': 'Apenas usuários da empresa ou administrador do sistema podem atribuir.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        ser = AtribuicaoFreelancerVagaDiretaSerializer(data=request.data, context={'request': request})
        ser.is_valid(raise_exception=True)
        vaga = ser.validated_data['vaga']
        freelance = ser.validated_data['freelance']
        exigir_hist = ser.validated_data.get('exigir_historico_empresa', False)
        ignorar_limite = ser.validated_data.get('ignorar_limite_vagas', False)
        if ignorar_limite and not getattr(user, 'is_admin_sistema', False):
            return Response(
                {'detail': 'Só administrador do sistema pode ignorar o limite de vagas.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            contrato, meta = atribuir_freelancer_a_vaga_direto(
                freelance,
                vaga,
                exigir_prestacao_servico=exigir_hist,
                ignorar_limite_vagas=ignorar_limite,
            )
        except DjangoValidationError as e:
            if hasattr(e, 'message_dict') and e.message_dict:
                raise serializers.ValidationError(e.message_dict)
            msgs = list(getattr(e, 'messages', []) or [str(e)])
            raise serializers.ValidationError(msgs[0] if len(msgs) == 1 else msgs)

        out = ContratoPagamentoSerializer(contrato, context={'request': request})
        code = status.HTTP_201_CREATED if meta.get('criado') else status.HTTP_200_OK
        return Response(
            {'contrato': out.data, 'criado': meta.get('criado'), 'mensagem': meta.get('mensagem', '')},
            status=code,
        )


class FreelancerPrestacaoServicoViewSet(viewsets.ModelViewSet):
    """
    Lista e gere freelancers que já prestaram serviço à empresa (histórico operacional).
    Também preenchido automaticamente ao lançar pagamento/desconto ou contrato.
    """
    serializer_class = FreelancerPrestacaoServicoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = FreelancerPrestacaoServico.objects.select_related('freelance', 'empresa_contratante')
        if getattr(user, 'is_admin_sistema', False):
            out = qs
        elif getattr(user, 'is_empresa_user', False) and user.empresa_contratante:
            out = qs.filter(empresa_contratante=user.empresa_contratante)
        elif getattr(user, 'is_freelancer', False):
            try:
                fl = user.freelance
            except Freelance.DoesNotExist:
                return FreelancerPrestacaoServico.objects.none()
            out = qs.filter(freelance=fl, ativo=True)
        else:
            return FreelancerPrestacaoServico.objects.none()
        if self.request.query_params.get('incluir_inativos') != '1':
            out = out.filter(ativo=True)
        return out.order_by('freelance__nome_completo')

    def perform_create(self, serializer):
        user = self.request.user
        if getattr(user, 'is_empresa_user', False) and user.empresa_contratante:
            serializer.save(empresa_contratante=user.empresa_contratante)
        elif getattr(user, 'is_admin_sistema', False):
            serializer.save()
        else:
            raise serializers.ValidationError('Sem permissão para criar.')

    def perform_update(self, serializer):
        user = self.request.user
        if not getattr(user, 'is_empresa_user', False) and not getattr(user, 'is_admin_sistema', False):
            raise serializers.ValidationError('Sem permissão.')
        serializer.save()
