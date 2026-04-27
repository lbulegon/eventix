"""
Pré-visualização da geração de vagas/turnos a partir da grade semanal.

Objetivo: mostrar ao gestor o impacto antes de aplicar:
- turnos a criar
- turnos existentes a sincronizar
- vagas (funções) a criar/atualizar
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Dict, Iterable, List, Tuple

from app_eventos.models import Funcao
from app_eventos.models_operacao_continua import TurnoOperacional, UnidadeOperacional, VagaTurno


@dataclass(frozen=True)
class DemandaDia:
    weekday: int
    hora_inicio: object
    hora_fim: object
    funcao_id: int
    quantidade: int


def _normalizar_demandas(dias_grade: Iterable[object]) -> List[DemandaDia]:
    out: List[DemandaDia] = []
    for d in dias_grade:
        if not getattr(d, "ativo", False):
            continue
        wd = int(getattr(d, "weekday", -1))
        if wd < 0 or wd > 6:
            continue
        hora_inicio = getattr(d, "hora_inicio", None)
        hora_fim = getattr(d, "hora_fim", None)
        if not hora_inicio or not hora_fim:
            continue
        for item in getattr(d, "demandas", []) or []:
            if not isinstance(item, dict):
                continue
            raw_fid = item.get("funcao_id") or item.get("funcao")
            if raw_fid in (None, ""):
                continue
            try:
                fid = int(raw_fid)
                qtd = int(item.get("quantidade", 0) or 0)
            except (TypeError, ValueError):
                continue
            if fid <= 0 or qtd <= 0:
                continue
            out.append(
                DemandaDia(
                    weekday=wd,
                    hora_inicio=hora_inicio,
                    hora_fim=hora_fim,
                    funcao_id=fid,
                    quantidade=qtd,
                )
            )
    return out


def simular_geracao_programacao(
    unidade: UnidadeOperacional,
    *,
    dias_grade: Iterable[object],
    dias_a_frente: int = 14,
    data_referencia: date | None = None,
) -> dict:
    """
    Retorna um resumo de impacto de geração/sincronização sem gravar nada.
    """
    data_ref = data_referencia or date.today()
    limite = data_ref + timedelta(days=max(1, int(dias_a_frente)))
    demandas = _normalizar_demandas(dias_grade)

    # Desejado por turno(data+intervalo) e função.
    desejado_por_turno: Dict[Tuple[date, object, object], Dict[int, int]] = defaultdict(dict)
    d = data_ref
    while d < limite:
        wd = d.weekday()
        for dem in demandas:
            if dem.weekday != wd:
                continue
            key_t = (d, dem.hora_inicio, dem.hora_fim)
            desejado_por_turno[key_t][dem.funcao_id] = dem.quantidade
        d += timedelta(days=1)

    turnos = list(
        TurnoOperacional.objects.filter(
            unidade=unidade,
            data__gte=data_ref,
            data__lt=limite,
        ).select_related("unidade")
    )
    turnos_por_key = {(t.data, t.hora_inicio, t.hora_fim): t for t in turnos}
    vagas = list(
        VagaTurno.objects.filter(turno__in=turnos).select_related("funcao", "turno")
    )
    vagas_por_turno_funcao = {(v.turno_id, v.funcao_id): v for v in vagas}
    funcao_ids = set()
    for fqs in desejado_por_turno.values():
        funcao_ids.update(fqs.keys())
    funcao_nomes = {
        f.id: f.nome
        for f in Funcao.objects.filter(id__in=funcao_ids).only("id", "nome")
    }

    turnos_criar = 0
    turnos_sincronizar = 0
    vagas_criar = 0
    vagas_atualizar = 0
    vagas_manter = 0
    detalhes: List[dict] = []

    for key_t, funcoes_qtd in sorted(
        desejado_por_turno.items(),
        key=lambda x: (x[0][0], x[0][1], x[0][2]),
    ):
        turno = turnos_por_key.get(key_t)
        if not turno:
            turnos_criar += 1
            vagas_criar += len(funcoes_qtd)
            detalhes.append(
                {
                    "data": key_t[0],
                    "hora_inicio": key_t[1],
                    "hora_fim": key_t[2],
                    "acao_turno": "criar",
                    "funcoes": [
                        {
                            "funcao_id": fid,
                            "funcao_nome": funcao_nomes.get(fid, f"Função #{fid}"),
                            "qtd_desejada": qtd,
                            "acao": "criar",
                        }
                        for fid, qtd in sorted(funcoes_qtd.items())
                    ],
                }
            )
            continue

        turnos_sincronizar += 1
        funcoes_det = []
        for fid, qtd in sorted(funcoes_qtd.items()):
            vaga = vagas_por_turno_funcao.get((turno.id, fid))
            if not vaga:
                vagas_criar += 1
                funcoes_det.append(
                    {
                        "funcao_id": fid,
                        "funcao_nome": funcao_nomes.get(fid, f"Função #{fid}"),
                        "qtd_desejada": qtd,
                        "acao": "criar",
                    }
                )
                continue
            if int(vaga.quantidade_total) != int(qtd):
                vagas_atualizar += 1
                funcoes_det.append(
                    {
                        "funcao_id": fid,
                        "funcao_nome": vaga.funcao.nome,
                        "qtd_atual": int(vaga.quantidade_total),
                        "qtd_desejada": int(qtd),
                        "acao": "atualizar",
                    }
                )
            else:
                vagas_manter += 1
                funcoes_det.append(
                    {
                        "funcao_id": fid,
                        "funcao_nome": vaga.funcao.nome,
                        "qtd_atual": int(vaga.quantidade_total),
                        "qtd_desejada": int(qtd),
                        "acao": "manter",
                    }
                )

        detalhes.append(
            {
                "data": key_t[0],
                "hora_inicio": key_t[1],
                "hora_fim": key_t[2],
                "acao_turno": "sincronizar",
                "funcoes": funcoes_det,
            }
        )

    return {
        "janela": {"inicio": data_ref, "fim_exclusivo": limite, "dias": int(dias_a_frente)},
        "totais": {
            "turnos_criar": turnos_criar,
            "turnos_sincronizar": turnos_sincronizar,
            "vagas_criar": vagas_criar,
            "vagas_atualizar": vagas_atualizar,
            "vagas_manter": vagas_manter,
            "itens_analisados": len(detalhes),
            "vagas_impactadas": int(vagas_criar + vagas_atualizar),
            "vagas_total_planeadas": int(vagas_criar + vagas_atualizar + vagas_manter),
            "funcoes_unicas": len(funcao_ids),
        },
        "detalhes": detalhes,
    }

