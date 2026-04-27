"""
UI «carga semanal»: converte matriz dia a dia em RegraRecorrencia + RegraRecorrenciaFuncao
e o inverso para preencher o ecrã.

Dias: 0 = segunda … 6 = domingo (date.weekday()).
"""
from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime, time
from typing import Any, Dict, List, Optional, Sequence, Tuple

from django.core.exceptions import ValidationError
from django.db import transaction

from app_eventos.models import Funcao
from app_eventos.models_operacao_continua import (
    RegraRecorrencia,
    RegraRecorrenciaFuncao,
    UnidadeOperacional,
)

DIAS_LABEL = (
    'Segunda',
    'Terça',
    'Quarta',
    'Quinta',
    'Sexta',
    'Sábado',
    'Domingo',
)


def _parse_time(s: str) -> Optional[time]:
    s = (s or '').strip()
    if not s:
        return None
    s = s[:5] if len(s) >= 5 else s
    try:
        return datetime.strptime(s, '%H:%M').time()
    except ValueError:
        return None


def _clamp_weekday(raw: Any, default: int) -> int:
    if raw is None or raw == '':
        return max(0, min(6, int(default)))
    try:
        w = int(raw)
    except (TypeError, ValueError):
        w = int(default)
    return max(0, min(6, w))


def _merge_demandas(
    bruto: Any,
) -> "OrderedDict[int, int]":
    """Soma quantidades por função; ignora vazios ou inválidos."""
    out: "OrderedDict[int, int]" = OrderedDict()
    if not bruto or not isinstance(bruto, list):
        return out
    for item in bruto:
        if not isinstance(item, dict):
            continue
        raw = item.get('funcao_id') or item.get('funcao') or 0
        try:
            fid = int(raw)
        except (TypeError, ValueError):
            continue
        if fid <= 0:
            continue
        try:
            q = int(item.get('quantidade', 0) or 0)
        except (TypeError, ValueError):
            q = 0
        if q > 0:
            out[fid] = out.get(fid, 0) + q
    return out


@dataclass
class DiaGrade:
    weekday: int
    ativo: bool
    hora_inicio: str
    hora_fim: str
    demandas: List[Dict[str, Any]] = field(default_factory=list)
    aviso: str = ''


def grade_a_partir_das_regras(unidade: UnidadeOperacional) -> List[DiaGrade]:
    """
    Para cada dia, usa a primeira regra que o inclui em `dias_semana`.
    Sinaliza conflito se mais de uma regra cobre o mesmo dia.
    """
    regras = list(
        RegraRecorrencia.objects.filter(unidade=unidade)
        .prefetch_related('demandas_por_funcao__funcao')
        .order_by('id')
    )
    dias: List[DiaGrade] = []
    for wd in range(7):
        cobrindo = [r for r in regras if wd in (r.dias_semana or [])]
        aviso = ''
        if len(cobrindo) > 1:
            aviso = (
                f'Existem {len(cobrindo)} regras para este dia; a mostrar a primeira. '
                'Assim que guardar na carga semanal, as regras serão unificadas.'
            )
        if cobrindo:
            r = cobrindo[0]
            dem: List[Dict[str, Any]] = []
            for d in r.demandas_por_funcao.all():
                dem.append({'funcao_id': d.funcao_id, 'quantidade': d.quantidade})
            if not dem:
                dem = [{'funcao_id': '', 'quantidade': 1}]
            dias.append(
                DiaGrade(
                    weekday=wd,
                    ativo=True,
                    hora_inicio=r.hora_inicio.strftime('%H:%M'),
                    hora_fim=r.hora_fim.strftime('%H:%M'),
                    demandas=dem,
                    aviso=aviso,
                )
            )
        else:
            dias.append(
                DiaGrade(
                    weekday=wd,
                    ativo=False,
                    hora_inicio='08:00',
                    hora_fim='16:00',
                    demandas=[],
                    aviso=aviso,
                )
            )
    return dias


def dias_dataclass_para_contexto(dias: List[DiaGrade]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for d in dias:
        dems: List[Dict[str, Any]] = []
        for x in d.demandas:
            if not isinstance(x, dict):
                continue
            raw = x.get('funcao_id') or x.get('funcao')
            fid: Any = ''
            if raw not in (None, ''):
                try:
                    fid = int(raw)
                except (TypeError, ValueError):
                    fid = ''
            try:
                q = int(x.get('quantidade', 0) or 0)
            except (TypeError, ValueError):
                q = 0
            if fid != '' and q < 0:
                q = 0
            dems.append({'funcao_id': fid, 'quantidade': q if q > 0 else 0})
        out.append(
            {
                'weekday': d.weekday,
                'label': DIAS_LABEL[d.weekday],
                'ativo': d.ativo,
                'hora_inicio': d.hora_inicio,
                'hora_fim': d.hora_fim,
                'demandas': dems,
                'aviso': d.aviso,
            }
        )
    return out


def payload_lista_para_dias(payload: Any) -> List[DiaGrade]:
    if not payload or not isinstance(payload, dict):
        return [DiaGrade(wd, False, '08:00', '16:00', []) for wd in range(7)]
    partes = payload.get('dias') or []
    if not isinstance(partes, list):
        partes = []
    while len(partes) < 7:
        partes.append({})
    partes = partes[:7]
    out: List[DiaGrade] = []
    for i, p in enumerate(partes):
        if not isinstance(p, dict):
            p = {}
        dmds = p.get('demandas') or []
        if not isinstance(dmds, list):
            dmds = []
        dem_norm: List[Dict[str, Any]] = []
        for x in dmds:
            if not isinstance(x, dict):
                continue
            try:
                q = int(x.get('quantidade', 0) or 0)
            except (TypeError, ValueError):
                q = 0
            dem_norm.append({'funcao_id': x.get('funcao_id') or x.get('funcao'), 'quantidade': max(0, q)})
        out.append(
            DiaGrade(
                weekday=_clamp_weekday(p.get('weekday'), i),
                ativo=bool(p.get('ativo', False)),
                hora_inicio=(p.get('hora_inicio') or '08:00')[:5],
                hora_fim=(p.get('hora_fim') or '16:00')[:5],
                demandas=dem_norm,
                aviso='',
            )
        )
    return out


def _nome_regra_para_grupo(weekdays: List[int]) -> str:
    ordered = sorted(set(weekdays))
    partes = [DIAS_LABEL[w] for w in ordered]
    nome = ' · '.join(partes)
    return (f'Carga semanal: {nome}')[:120]


def agrupar_carga_para_regras(
    dias: Sequence[DiaGrade],
) -> List[Tuple[List[int], time, time, "OrderedDict[int, int]"]]:
    """
    Reúne dias com o mesmo (hora_inicio, hora_fim, funções+quantidades).
    Levanta ValidationError se algum dia ativo tiver problemas.
    """
    chave_por_dia: "OrderedDict[Tuple[time, time, Tuple[Tuple[int, int], ...]], List[int]]" = OrderedDict()
    erros: List[str] = []

    for d in dias:
        if not d.ativo:
            continue
        t_ini = _parse_time(d.hora_inicio)
        t_fim = _parse_time(d.hora_fim)
        if t_ini is None or t_fim is None:
            erros.append(f'«{DIAS_LABEL[d.weekday]}»: hora inválida (use HH:MM).')
            continue
        if t_ini >= t_fim:
            erros.append(f'«{DIAS_LABEL[d.weekday]}»: o início do turno deve ser antes do fim.')
            continue
        m = _merge_demandas(d.demandas)
        if not m:
            erros.append(
                f'«{DIAS_LABEL[d.weekday]}»: com o dia ativo, indique ao menos uma função com quantidade > 0.'
            )
            continue
        carga_t = tuple(sorted(m.items()))
        k = (t_ini, t_fim, carga_t)
        if k not in chave_por_dia:
            chave_por_dia[k] = []
        chave_por_dia[k].append(d.weekday)

    if erros:
        raise ValidationError(erros)

    resultado: List[Tuple[List[int], time, time, "OrderedDict[int, int]"]] = []
    for (t_ini, t_fim, carga_t), wds in chave_por_dia.items():
        carga = OrderedDict((a, b) for a, b in carga_t)
        resultado.append((sorted(set(wds)), t_ini, t_fim, carga))
    return resultado


@transaction.atomic
def substituir_regras_pela_carga(
    unidade: UnidadeOperacional,
    *,
    empresa,
    grupos: List[Tuple[List[int], time, time, "OrderedDict[int, int]"]],
) -> int:
    """
    Apaga regras existentes e cria novas. Valida funções (tenant + ativo).
    """
    for _wds, _t0, _t1, carga in grupos:
        for fid in carga:
            f = (
                Funcao.objects.filter(
                    pk=fid,
                    ativo=True,
                )
                .select_related('empresa_contratante')
                .first()
            )
            if f is None:
                raise ValidationError(f'Função id={fid} inexistente ou inativa.')
            if f.empresa_contratante_id and f.empresa_contratante_id != empresa.id:
                raise ValidationError(f'A função «{f.nome}» não pertence à sua empresa.')

    RegraRecorrencia.objects.filter(unidade=unidade).delete()
    n_criadas = 0
    for wds, t_ini, t_fim, carga in grupos:
        if not carga or not wds:
            continue
        nome = _nome_regra_para_grupo(wds)
        r = RegraRecorrencia.objects.create(
            unidade=unidade,
            nome=nome,
            dias_semana=sorted(wds),
            hora_inicio=t_ini,
            hora_fim=t_fim,
            ativo=True,
        )
        n_criadas += 1
        for fid, q in carga.items():
            RegraRecorrenciaFuncao.objects.create(
                regra=r,
                funcao_id=fid,
                quantidade=int(q),
            )
    return n_criadas