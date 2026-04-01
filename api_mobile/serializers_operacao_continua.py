from django.utils.dateparse import parse_time
from rest_framework import serializers

from app_eventos.models import EmpresaContratante, Evento, PontoOperacao


class RecorrenciaDemandaSerializer(serializers.Serializer):
    """Demanda por função dentro de uma regra (equivale a tipo de vaga + quantidade)."""
    funcao = serializers.IntegerField(min_value=1)
    quantidade = serializers.IntegerField(min_value=1, default=1)


class RecorrenciaItemSerializer(serializers.Serializer):
    nome = serializers.CharField(max_length=120, required=False, allow_blank=True, default='')
    dias_semana = serializers.ListField(
        child=serializers.IntegerField(min_value=0, max_value=6),
        min_length=1,
        help_text='0=segunda … 6=domingo (date.weekday()).',
    )
    hora_inicio = serializers.CharField()
    hora_fim = serializers.CharField()
    vagas = RecorrenciaDemandaSerializer(many=True, required=False, default=list)

    def validate(self, attrs):
        for key in ('hora_inicio', 'hora_fim'):
            v = attrs[key]
            if hasattr(v, 'hour'):
                continue
            t = parse_time(str(v).strip())
            if t is None:
                raise serializers.ValidationError({key: 'Use HH:MM ou HH:MM:SS.'})
            attrs[key] = t
        return attrs


class UnidadeOperacionalComRecorrenciasSerializer(serializers.Serializer):
    """
    Payload alinhado ao fluxo: unidade + lista de recorrências com demandas por função.

    Administrador do sistema deve enviar empresa_contratante (id).
    Usuário da empresa usa o tenant do token.
    """
    tipo = serializers.ChoiceField(choices=['evento', 'operacao'])
    nome = serializers.CharField(max_length=255)
    descricao = serializers.CharField(required=False, allow_blank=True, default='')
    evento = serializers.IntegerField(required=False, allow_null=True)
    ponto_operacao = serializers.IntegerField(required=False, allow_null=True)
    data_inicio = serializers.DateTimeField(required=False, allow_null=True)
    data_fim = serializers.DateTimeField(required=False, allow_null=True)
    ativo = serializers.BooleanField(default=True)
    recorrencias = RecorrenciaItemSerializer(many=True, required=False, default=list)

    gerar_turnos = serializers.BooleanField(
        default=False,
        help_text='Se true, após criar regras chama o motor (janela rolante).',
    )
    dias_janela = serializers.IntegerField(default=7, min_value=1, max_value=120)
    data_referencia_turnos = serializers.DateField(required=False, allow_null=True)
    empresa_contratante = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text='Obrigatório para admin_sistema; ignorado para usuário de empresa.',
    )

    def validate(self, attrs):
        request = self.context.get('request')
        user = request.user if request else None
        if not user or not user.is_authenticated:
            raise serializers.ValidationError('Autenticação obrigatória.')

        empresa = None
        if getattr(user, 'is_empresa_user', False) and getattr(user, 'empresa_contratante', None):
            empresa = user.empresa_contratante
            if attrs.get('empresa_contratante') and attrs['empresa_contratante'] != empresa.pk:
                raise serializers.ValidationError(
                    {'empresa_contratante': 'Não pode criar para outra empresa.'}
                )
        elif getattr(user, 'is_admin_sistema', False) or getattr(user, 'is_superuser', False):
            ecid = attrs.get('empresa_contratante')
            if not ecid:
                raise serializers.ValidationError(
                    {'empresa_contratante': 'Obrigatório para administrador / superusuário.'}
                )
            empresa = EmpresaContratante.objects.filter(pk=ecid).first()
            if not empresa:
                raise serializers.ValidationError({'empresa_contratante': 'Empresa não encontrada.'})
        else:
            raise serializers.ValidationError('Sem permissão para criar unidade operacional.')

        attrs['_empresa_contratante'] = empresa

        tipo = attrs['tipo']
        if tipo == 'evento':
            eid = attrs.get('evento')
            if not eid:
                raise serializers.ValidationError({'evento': 'Obrigatório para tipo evento.'})
            ev = Evento.objects.filter(pk=eid).first()
            if not ev:
                raise serializers.ValidationError({'evento': 'Evento não encontrado.'})
            if ev.empresa_contratante_id != empresa.pk:
                raise serializers.ValidationError({'evento': 'Evento não pertence à empresa.'})
            attrs['evento'] = eid
            attrs['ponto_operacao'] = None
        elif tipo == 'operacao':
            pid = attrs.get('ponto_operacao')
            if not pid:
                raise serializers.ValidationError(
                    {'ponto_operacao': 'Obrigatório para tipo operação contínua.'}
                )
            po = PontoOperacao.objects.filter(pk=pid).first()
            if not po:
                raise serializers.ValidationError({'ponto_operacao': 'Ponto de operação não encontrado.'})
            if po.empresa_contratante_id != empresa.pk:
                raise serializers.ValidationError(
                    {'ponto_operacao': 'Estabelecimento não pertence à empresa.'}
                )
            attrs['ponto_operacao'] = pid
            attrs['evento'] = None

        return attrs
