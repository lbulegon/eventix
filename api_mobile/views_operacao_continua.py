from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_eventos.services.criar_unidade_recorrencias import criar_unidade_com_recorrencias
from app_eventos.services.motor_recorrencia_turnos import gerar_turnos_janela

from .serializers_operacao_continua import UnidadeOperacionalComRecorrenciasSerializer


class UnidadeOperacionalComRecorrenciasView(APIView):
    """
    POST: cria UnidadeOperacional + regras de recorrência + demandas por função.
    Opcionalmente gera turnos (janela rolante) na mesma requisição.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        ser = UnidadeOperacionalComRecorrenciasSerializer(data=request.data, context={'request': request})
        ser.is_valid(raise_exception=True)
        data = ser.validated_data.copy()

        empresa = data.pop('_empresa_contratante')
        recorrencias = data.pop('recorrencias', []) or []
        gerar_turnos = data.pop('gerar_turnos', False)
        dias_janela = data.pop('dias_janela', 7)
        data_ref = data.pop('data_referencia_turnos', None)
        data.pop('empresa_contratante', None)

        payload_recorrencias = []
        for r in recorrencias:
            vagas = []
            for v in r.get('vagas') or []:
                vagas.append({'funcao': v['funcao'], 'quantidade': v['quantidade']})
            payload_recorrencias.append(
                {
                    'nome': r.get('nome') or '',
                    'dias_semana': r['dias_semana'],
                    'hora_inicio': r['hora_inicio'],
                    'hora_fim': r['hora_fim'],
                    'vagas': vagas,
                }
            )

        try:
            unidade, regras_info = criar_unidade_com_recorrencias(
                empresa,
                tipo=data['tipo'],
                nome=data['nome'],
                descricao=data.get('descricao') or '',
                evento_id=data.get('evento'),
                ponto_operacao_id=data.get('ponto_operacao'),
                data_inicio=data.get('data_inicio'),
                data_fim=data.get('data_fim'),
                ativo=data.get('ativo', True),
                recorrencias=payload_recorrencias,
            )
        except DjangoValidationError as e:
            if hasattr(e, 'message_dict') and e.message_dict:
                raise serializers.ValidationError(e.message_dict)
            raise serializers.ValidationError(list(getattr(e, 'messages', [str(e)])))

        motor_resultado = None
        if gerar_turnos:
            motor_resultado = gerar_turnos_janela(
                unidade,
                dias_a_frente=dias_janela,
                data_referencia=data_ref,
            )

        return Response(
            {
                'unidade': {
                    'id': unidade.pk,
                    'nome': unidade.nome,
                    'tipo': unidade.tipo,
                    'evento': unidade.evento_id,
                    'ponto_operacao': unidade.ponto_operacao_id,
                    'ativo': unidade.ativo,
                },
                'regras_criadas': regras_info,
                'motor_turnos': motor_resultado,
            },
            status=status.HTTP_201_CREATED,
        )
