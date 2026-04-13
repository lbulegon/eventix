"""
Aplicação de regras de score de confiabilidade sobre o modelo Freelance.

Regras:
- presente: +1 (score máximo 10)
- falta_com_aviso: -1; incrementa faltas_com_aviso
- falta_sem_aviso: -3; incrementa faltas_sem_aviso

Se score <= 0 → bloqueado = True; se score > 0 → bloqueado = False.

Idempotência: cada RegistroPresencaFreelancer só pode aplicar pontuação uma vez
(campo pontuacao_aplicada).
"""
from __future__ import annotations

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from app_eventos.models_registro_presenca_freelancer import RegistroPresencaFreelancer


def delta_por_status(status: str) -> int:
    if status == RegistroPresencaFreelancer.STATUS_PRESENTE:
        return 1
    if status == RegistroPresencaFreelancer.STATUS_FALTA_AVISO:
        return -1
    if status == RegistroPresencaFreelancer.STATUS_FALTA_SEM_AVISO:
        return -3
    raise ValueError(f'Status inválido para score: {status!r}')


@transaction.atomic
def aplicar_pontuacao_para_registro(registro_id: int) -> bool:
    """
    Aplica o efeito deste registo no Freelance associado.

    Retorna True se a pontuação foi aplicada agora; False se já tinha sido
    aplicada (idempotente).
    """
    locked = (
        RegistroPresencaFreelancer.objects.select_for_update()
        .filter(pk=registro_id, pontuacao_aplicada=False)
        .first()
    )
    if locked is None:
        return False

    from app_eventos.models import Freelance  # evita import circular em apps loading

    fl = Freelance.objects.select_for_update().get(pk=locked.freelance_id)
    delta = delta_por_status(locked.status)

    new_score = fl.score_confiabilidade + delta
    if delta > 0:
        new_score = min(10, new_score)

    updates_fl = {
        'score_confiabilidade': new_score,
        'bloqueado': new_score <= 0,
    }

    if locked.status == RegistroPresencaFreelancer.STATUS_FALTA_AVISO:
        updates_fl['faltas_com_aviso'] = F('faltas_com_aviso') + 1
    elif locked.status == RegistroPresencaFreelancer.STATUS_FALTA_SEM_AVISO:
        updates_fl['faltas_sem_aviso'] = F('faltas_sem_aviso') + 1
    elif locked.status == RegistroPresencaFreelancer.STATUS_PRESENTE:
        updates_fl['data_ultimo_evento'] = timezone.now()

    Freelance.objects.filter(pk=fl.pk).update(**updates_fl)

    RegistroPresencaFreelancer.objects.filter(pk=locked.pk).update(pontuacao_aplicada=True)
    return True


def aplicar_pontuacao_para_registro_instancia(registro: RegistroPresencaFreelancer) -> bool:
    """Atalho quando já se tem a instância em memória."""
    return aplicar_pontuacao_para_registro(registro.pk)


def preview_delta(status: str) -> int:
    """Útil para testes ou UI; não altera dados."""
    return delta_por_status(status)
