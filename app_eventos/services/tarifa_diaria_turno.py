"""
Resolve qual valor de diária aplicar (dia / noite / noite especial) a partir da tarifa cadastrada.
"""
from datetime import datetime, time
from typing import Any, Dict

from app_eventos.models_tarifa_diaria_turno import DataCalendarioTarifa, TarifaDiariaPorFuncaoPonto


def _eh_noite(hora_inicio: time, tarifa: TarifaDiariaPorFuncaoPonto) -> bool:
    corte = tarifa.hora_corte_dia_noite
    fim_mad = tarifa.hora_fim_madrugada_noite
    if hora_inicio >= corte:
        return True
    if hora_inicio < fim_mad:
        return True
    return False


def _eh_sexta_sabado_noite(weekday: int, eh_noite: bool) -> bool:
    return eh_noite and weekday in (4, 5)


def _eh_data_especial_noite(ponto_id: int, data) -> bool:
    """Véspera / data cadastrada: usa tarifa especial quando for noite."""
    return DataCalendarioTarifa.objects.filter(
        ponto_operacao_id=ponto_id,
        data=data,
        ativo=True,
    ).exists()


def resolver_tarifa_diaria(
    *,
    empresa_contratante_id: int,
    ponto_operacao_id: int,
    funcao_id: int,
    data,
    hora_inicio: time,
) -> Dict[str, Any]:
    """
    Retorna valor sugerido e motivo.

    Prioridade noite especial: (sexta/sáb noite) OU (data em calendário especial) — ambos exigem turno noite.
    """
    try:
        tarifa = TarifaDiariaPorFuncaoPonto.objects.get(
            empresa_contratante_id=empresa_contratante_id,
            ponto_operacao_id=ponto_operacao_id,
            funcao_id=funcao_id,
            ativo=True,
        )
    except TarifaDiariaPorFuncaoPonto.DoesNotExist:
        return {
            'encontrou': False,
            'valor': None,
            'tipo': None,
            'motivo': 'Não há tarifa cadastrada para este estabelecimento e função.',
        }

    noite = _eh_noite(hora_inicio, tarifa)
    wd = data.weekday()

    if noite:
        especial_fs = _eh_sexta_sabado_noite(wd, True)
        especial_cal = _eh_data_especial_noite(ponto_operacao_id, data)
        if especial_fs or especial_cal:
            partes = []
            if especial_fs:
                partes.append('sexta/sábado noite')
            if especial_cal:
                partes.append('véspera ou data especial (calendário)')
            return {
                'encontrou': True,
                'valor': tarifa.valor_noite_especial,
                'tipo': 'noite_especial',
                'motivo': '; '.join(partes) if partes else 'noite especial',
                'tarifa_id': tarifa.pk,
            }

    if noite:
        return {
            'encontrou': True,
            'valor': tarifa.valor_turno_noite,
            'tipo': 'noite',
            'motivo': 'turno noite',
            'tarifa_id': tarifa.pk,
        }

    return {
        'encontrou': True,
        'valor': tarifa.valor_turno_dia,
        'tipo': 'dia',
        'motivo': 'turno dia',
        'tarifa_id': tarifa.pk,
    }


def parse_hora(valor: str) -> time:
    """Aceita HH:MM ou HH:MM:SS."""
    for fmt in ('%H:%M', '%H:%M:%S'):
        try:
            return datetime.strptime(valor.strip(), fmt).time()
        except ValueError:
            continue
    raise ValueError('Hora inválida. Use HH:MM.')
