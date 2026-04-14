from collections import defaultdict
from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Sum
from rest_framework import serializers

from app_eventos.models import Candidatura, ContratoFreelance, Freelance, Vaga
from app_eventos.models_freelancer_empresa import FreelancerPrestacaoServico
from app_eventos.models_pagamento_freelancers import (
    DIA_SEMANA_FECHAMENTO_CHOICES,
    FichamentoSemanaFreelancer,
    LancamentoPagoDiarioFreelancer,
    LancamentoDescontoFreelancer,
    validar_contrato_com_fichamento,
)


def _drf_validate_contrato(fichamento, freelance, contrato):
    if not contrato or not fichamento or not freelance:
        return
    try:
        validar_contrato_com_fichamento(fichamento, freelance, contrato)
    except DjangoValidationError as e:
        if getattr(e, 'message_dict', None):
            raise serializers.ValidationError(e.message_dict)
        raise serializers.ValidationError(str(e))


def _periodo_serializer_ok(fichamento, data):
    if not fichamento or not data:
        return True
    ini = fichamento.data_inicio_periodo
    fim = fichamento.data_fechamento
    if ini is None or fim is None:
        return True
    return ini <= data <= fim


class LancamentoPagoDiarioFreelancerSerializer(serializers.ModelSerializer):
    """Pagamentos diários (coluna Pago da planilha); folga com valor zero."""
    vaga_id = serializers.IntegerField(source='contrato_freelance.vaga_id', read_only=True, allow_null=True)
    vaga_titulo = serializers.CharField(source='contrato_freelance.vaga.titulo', read_only=True, allow_null=True)

    class Meta:
        model = LancamentoPagoDiarioFreelancer
        fields = [
            'id', 'fichamento', 'freelance', 'data', 'valor_bruto', 'eh_folga',
            'contrato_freelance', 'vaga_id', 'vaga_titulo',
        ]

    def validate_fichamento(self, fichamento):
        request = self.context.get('request')
        if request and getattr(request.user, 'is_empresa_user', False) and request.user.empresa_contratante:
            if fichamento.empresa_contratante_id != request.user.empresa_contratante_id:
                raise serializers.ValidationError('Fichamento não pertence à sua empresa.')
        return fichamento

    def validate(self, attrs):
        fichamento = attrs.get('fichamento') or getattr(self.instance, 'fichamento', None)
        data = attrs.get('data')
        if data is None and self.instance:
            data = self.instance.data
        if fichamento and data and not _periodo_serializer_ok(fichamento, data):
            raise serializers.ValidationError(
                {'data': 'Data fora do período de 7 dias deste fichamento.'}
            )
        eh = attrs.get('eh_folga', self.instance.eh_folga if self.instance else False)
        valor = attrs.get('valor_bruto', self.instance.valor_bruto if self.instance else Decimal('0'))
        if eh and valor != Decimal('0'):
            raise serializers.ValidationError({'valor_bruto': 'Em folga o valor deve ser zero.'})
        fichamento = attrs.get('fichamento') or getattr(self.instance, 'fichamento', None)
        freelance = attrs.get('freelance') or getattr(self.instance, 'freelance', None)
        contrato = attrs.get('contrato_freelance') or getattr(self.instance, 'contrato_freelance', None)
        _drf_validate_contrato(fichamento, freelance, contrato)
        return attrs


class LancamentoDescontoFreelancerSerializer(serializers.ModelSerializer):
    """Descontos: tipo vale (adiantamento), consumo, ou outro — alinhado à planilha."""
    tipo_label = serializers.CharField(source='get_tipo_display', read_only=True)
    vaga_id = serializers.IntegerField(source='contrato_freelance.vaga_id', read_only=True, allow_null=True)
    vaga_titulo = serializers.CharField(source='contrato_freelance.vaga.titulo', read_only=True, allow_null=True)

    class Meta:
        model = LancamentoDescontoFreelancer
        fields = [
            'id', 'fichamento', 'freelance', 'tipo', 'tipo_label', 'valor', 'descricao', 'data',
            'contrato_freelance', 'vaga_id', 'vaga_titulo',
        ]

    def validate_fichamento(self, fichamento):
        request = self.context.get('request')
        if request and getattr(request.user, 'is_empresa_user', False) and request.user.empresa_contratante:
            if fichamento.empresa_contratante_id != request.user.empresa_contratante_id:
                raise serializers.ValidationError('Fichamento não pertence à sua empresa.')
        return fichamento

    def validate(self, attrs):
        fichamento = attrs.get('fichamento') or getattr(self.instance, 'fichamento', None)
        data = attrs.get('data')
        if fichamento and data and not _periodo_serializer_ok(fichamento, data):
            raise serializers.ValidationError(
                {'data': 'Data fora do período de 7 dias deste fichamento.'}
            )
        valor = attrs.get('valor', getattr(self.instance, 'valor', None))
        if valor is not None and valor <= 0:
            raise serializers.ValidationError({'valor': 'Informe um valor maior que zero.'})
        fichamento = attrs.get('fichamento') or getattr(self.instance, 'fichamento', None)
        freelance = attrs.get('freelance') or getattr(self.instance, 'freelance', None)
        contrato = attrs.get('contrato_freelance') or getattr(self.instance, 'contrato_freelance', None)
        _drf_validate_contrato(fichamento, freelance, contrato)
        return attrs


class VagaDisponivelPagamentoSerializer(serializers.ModelSerializer):
    """Vagas ainda com lugar livre no estabelecimento (ponto de operação)."""
    vagas_disponiveis = serializers.SerializerMethodField()

    class Meta:
        model = Vaga
        fields = [
            'id', 'titulo', 'remuneracao', 'tipo_remuneracao', 'quantidade',
            'quantidade_preenchida', 'vagas_disponiveis', 'ativa', 'publicada',
            'data_limite_candidatura',
        ]

    def get_vagas_disponiveis(self, obj):
        return obj.vagas_disponiveis


class ContratoPagamentoSerializer(serializers.ModelSerializer):
    """Contrato ativo: freelancer aprovado e contratado para a vaga."""
    vaga_titulo = serializers.CharField(source='vaga.titulo', read_only=True)
    freelance_nome = serializers.CharField(source='freelance.nome_completo', read_only=True)
    candidatura_status = serializers.SerializerMethodField()

    class Meta:
        model = ContratoFreelance
        fields = [
            'id', 'freelance', 'freelance_nome', 'vaga', 'vaga_titulo',
            'status', 'data_contratacao', 'candidatura_status',
        ]

    def get_candidatura_status(self, obj):
        c = Candidatura.objects.filter(freelance_id=obj.freelance_id, vaga_id=obj.vaga_id).first()
        return c.status if c else None


class AtribuicaoFreelancerVagaDiretaSerializer(serializers.Serializer):
    """POST: atribui freelancer a vaga de estabelecimento sem candidatura."""
    vaga = serializers.PrimaryKeyRelatedField(
        queryset=Vaga.objects.select_related('empresa_contratante', 'ponto_operacao')
    )
    freelance = serializers.PrimaryKeyRelatedField(queryset=Freelance.objects.all())
    exigir_historico_empresa = serializers.BooleanField(
        default=False,
        required=False,
        help_text='Se true, exige FreelancerPrestacaoServico ativo para o tenant da vaga (opcional).',
    )
    ignorar_limite_vagas = serializers.BooleanField(
        default=False,
        required=False,
        help_text='Se true, permite atribuir mesmo com vagas_disponiveis = 0 (uso restrito).',
    )

    def validate_vaga(self, vaga):
        request = self.context.get('request')
        user = request.user
        if getattr(user, 'is_empresa_user', False) and user.empresa_contratante:
            if vaga.empresa_contratante_id != user.empresa_contratante_id:
                raise serializers.ValidationError('Vaga não pertence à sua empresa.')
        elif not getattr(user, 'is_admin_sistema', False):
            raise serializers.ValidationError('Sem permissão para usar esta vaga.')
        return vaga


class FichamentoSemanaFreelancerSerializer(serializers.ModelSerializer):
    ponto_operacao_nome = serializers.CharField(source='ponto_operacao.nome', read_only=True)
    data_inicio_periodo = serializers.SerializerMethodField(read_only=True)
    dia_semana_fechamento_efetivo = serializers.SerializerMethodField(read_only=True)
    totais_por_freelance = serializers.SerializerMethodField(read_only=True)
    resumo_planilha = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = FichamentoSemanaFreelancer
        fields = [
            'id',
            'empresa_contratante',
            'ponto_operacao',
            'ponto_operacao_nome',
            'dia_semana_fechamento',
            'dia_semana_fechamento_efetivo',
            'data_fechamento',
            'data_inicio_periodo',
            'observacoes',
            'criado_em',
            'atualizado_em',
            'totais_por_freelance',
            'resumo_planilha',
        ]
        read_only_fields = ['empresa_contratante', 'criado_em', 'atualizado_em']

    def get_data_inicio_periodo(self, obj):
        return obj.data_inicio_periodo

    def get_dia_semana_fechamento_efetivo(self, obj):
        d = obj.dia_fechamento_resolvido()
        if d is None:
            return None
        return {'codigo': d, 'label': dict(DIA_SEMANA_FECHAMENTO_CHOICES).get(d, str(d))}

    def get_totais_por_freelance(self, obj):
        """Pago (bruto), vales, consumos, outros descontos e líquido por freelancer."""
        from app_eventos.models import Freelance

        brutos = (
            obj.lancamentos_pago.values('freelance_id')
            .annotate(total=Sum('valor_bruto'))
        )
        map_bruto = {row['freelance_id']: row['total'] or Decimal('0') for row in brutos}

        desc_rows = obj.lancamentos_desconto.values('freelance_id', 'tipo').annotate(total=Sum('valor'))
        desc_por_f = defaultdict(
            lambda: {'vale': Decimal('0'), 'consumo': Decimal('0'), 'outro': Decimal('0')}
        )
        for row in desc_rows:
            fid = row['freelance_id']
            t = row['tipo']
            v = row['total'] or Decimal('0')
            if t in desc_por_f[fid]:
                desc_por_f[fid][t] = v

        ids = set(map_bruto) | set(desc_por_f.keys())
        out = []
        for fid in sorted(ids):
            b = map_bruto.get(fid, Decimal('0'))
            dv = desc_por_f[fid]['vale']
            dc = desc_por_f[fid]['consumo']
            dout = desc_por_f[fid]['outro']
            d = dv + dc + dout
            try:
                nome = Freelance.objects.only('nome_completo').get(pk=fid).nome_completo
            except Freelance.DoesNotExist:
                nome = str(fid)
            out.append({
                'freelance_id': fid,
                'freelance_nome': nome,
                'total_bruto': str(b),
                'total_vales': str(dv),
                'total_consumos': str(dc),
                'total_outros_descontos': str(dout),
                'total_descontos': str(d),
                'a_pagar': str(b - d),
            })
        return out

    def get_resumo_planilha(self, obj):
        """Totais do período: soma de pagamentos, vales, consumos e líquido global."""
        total_bruto = obj.lancamentos_pago.aggregate(s=Sum('valor_bruto'))['s'] or Decimal('0')
        ag = obj.lancamentos_desconto.values('tipo').annotate(s=Sum('valor'))
        by_tipo = {r['tipo']: r['s'] or Decimal('0') for r in ag}
        tv = by_tipo.get('vale', Decimal('0'))
        tc = by_tipo.get('consumo', Decimal('0'))
        to = by_tipo.get('outro', Decimal('0'))
        td = tv + tc + to
        return {
            'total_pago_bruto': str(total_bruto),
            'total_vales': str(tv),
            'total_consumos': str(tc),
            'total_outros_descontos': str(to),
            'total_descontos': str(td),
            'total_liquido_periodo': str(total_bruto - td),
        }

    def validate_ponto_operacao(self, ponto):
        request = self.context.get('request')
        if request and getattr(request.user, 'is_empresa_user', False) and request.user.empresa_contratante:
            if ponto.empresa_contratante_id != request.user.empresa_contratante_id:
                raise serializers.ValidationError('Estabelecimento não pertence à sua empresa.')
        return ponto

    def validate(self, attrs):
        ponto = attrs.get('ponto_operacao') or getattr(self.instance, 'ponto_operacao', None)
        empresa = attrs.get('empresa_contratante') or getattr(self.instance, 'empresa_contratante', None)
        if ponto and empresa and ponto.empresa_contratante_id != empresa.id:
            raise serializers.ValidationError(
                {'ponto_operacao': 'O estabelecimento deve pertencer ao mesmo tenant (empresa).'}
            )
        data_fech = attrs.get('data_fechamento')
        if self.instance and data_fech is None:
            data_fech = self.instance.data_fechamento
        dia_ov = attrs.get('dia_semana_fechamento')
        if dia_ov is None and self.instance:
            dia_ov = self.instance.dia_semana_fechamento
        dia = dia_ov
        if dia is None and ponto is not None:
            dia = ponto.dia_semana_fechamento
        if data_fech is not None and dia is not None and data_fech.weekday() != dia:
            raise serializers.ValidationError(
                {
                    'data_fechamento': (
                        'A data deve ser o mesmo dia da semana do fechamento configurado '
                        f'({dict(DIA_SEMANA_FECHAMENTO_CHOICES).get(dia, dia)}).'
                    )
                }
            )
        if data_fech is not None and dia is None:
            raise serializers.ValidationError(
                'Defina o dia da semana de fechamento no estabelecimento (ponto de operação) ou neste fichamento.'
            )
        return attrs


class FreelancerPrestacaoServicoSerializer(serializers.ModelSerializer):
    """Freelancers que já prestaram serviço (ou estão na base operacional) da empresa."""
    freelance_nome = serializers.CharField(source='freelance.nome_completo', read_only=True)

    class Meta:
        model = FreelancerPrestacaoServico
        fields = [
            'id', 'empresa_contratante', 'freelance', 'freelance_nome',
            'ativo', 'observacoes', 'criado_em', 'atualizado_em',
        ]
        read_only_fields = ['criado_em', 'atualizado_em']

    def validate_freelance(self, freelance):
        return freelance

    def validate(self, attrs):
        request = self.context.get('request')
        emp = attrs.get('empresa_contratante') or getattr(self.instance, 'empresa_contratante', None)
        if request and getattr(request.user, 'is_empresa_user', False) and request.user.empresa_contratante:
            if emp and emp.id != request.user.empresa_contratante_id:
                raise serializers.ValidationError(
                    {'empresa_contratante': 'Só pode gerir a sua empresa.'}
                )
        return attrs
