"""
Motor de recorrência: materializa turnos e VagaTurno numa janela rolante (ex.: próximos N dias).

Não gera infinito: apenas [data_referencia, data_referencia + dias_a_frente).
Idempotente: não duplica turno nem vaga por (unidade, data, intervalo, função).
"""
from datetime import date, timedelta
from typing import Optional

from django.db import transaction

from app_eventos.models_operacao_continua import (
    RegraRecorrencia,
    RegraRecorrenciaFuncao,
    TurnoOperacional,
    UnidadeOperacional,
    VagaTurno,
)


def _criar_vagas_para_turno(turno, regra: RegraRecorrencia):
    """Cria linhas VagaTurno a partir das demandas da regra."""
    demandas = RegraRecorrenciaFuncao.objects.filter(regra=regra).select_related('funcao')
    for d in demandas:
        VagaTurno.objects.get_or_create(
            turno=turno,
            funcao_id=d.funcao_id,
            defaults={
                'quantidade_total': d.quantidade,
                'quantidade_preenchida': 0,
            },
        )


def gerar_turnos_janela(
    unidade: UnidadeOperacional,
    *,
    dias_a_frente: int = 7,
    data_referencia: Optional[date] = None,
) -> dict:
    """
    Para cada regra ativa da unidade, gera turnos nos dias que batem dias_semana.

    Returns:
        dict com chaves: turnos_criados, vagas_turno_criadas, turnos_existentes_ignorados
    """
    if not unidade.ativo:
        return {'erro': 'Unidade inativa.', 'turnos_criados': 0, 'vagas_turno_criadas': 0, 'turnos_existentes_ignorados': 0}

    data_ref = data_referencia or date.today()
    limite = data_ref + timedelta(days=max(0, dias_a_frente))

    turnos_criados = 0
    vagas_criadas = 0
    ignorados = 0

    regras = RegraRecorrencia.objects.filter(unidade=unidade, ativo=True).prefetch_related('demandas_por_funcao')

    with transaction.atomic():
        unidade_locked = UnidadeOperacional.objects.select_for_update().get(pk=unidade.pk)

        for regra in regras:
            dias = regra.dias_semana or []
            if not dias:
                continue

            d = data_ref
            while d < limite:
                if d.weekday() not in dias:
                    d += timedelta(days=1)
                    continue

                existente = TurnoOperacional.objects.filter(
                    unidade_id=unidade_locked.pk,
                    data=d,
                    hora_inicio=regra.hora_inicio,
                    hora_fim=regra.hora_fim,
                ).first()

                if existente:
                    ignorados += 1
                    d += timedelta(days=1)
                    continue

                turno = TurnoOperacional.objects.create(
                    unidade=unidade_locked,
                    data=d,
                    hora_inicio=regra.hora_inicio,
                    hora_fim=regra.hora_fim,
                    origem=TurnoOperacional.ORIGEM_RECORRENCIA,
                    regra_recorrencia=regra,
                    status=TurnoOperacional.STATUS_ABERTO,
                )
                turnos_criados += 1

                antes = VagaTurno.objects.filter(turno=turno).count()
                _criar_vagas_para_turno(turno, regra)
                depois = VagaTurno.objects.filter(turno=turno).count()
                vagas_criadas += max(0, depois - antes)

                d += timedelta(days=1)

    return {
        'turnos_criados': turnos_criados,
        'vagas_turno_criadas': vagas_criadas,
        'turnos_existentes_ignorados': ignorados,
    }
