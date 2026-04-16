"""
Regra de negócio (cadastro privado por estabelecimento):

- Antes da primeira contratação efetiva, o freelancer pode atuar no mercado
  aberto (vagas, candidaturas, atribuição direta) sem vínculo prévio com a
  empresa.
- Depois da primeira contratação (ContratoFreelance ativo ligado à vaga da
  empresa), o par (empresa, freelancer) passa a constar em
  FreelancerPrestacaoServico — base do cadastro/histórico daquele
  estabelecimento; avaliações por empresa (ex.: FeedbackFreelancer) aplicam-se
  nesse contexto.

Este módulo garante a inclusão nessa lista quando:
- há lançamento de pagamento ou desconto no fichamento da empresa; ou
- é criado ou reativado um contrato de vaga com status ativo ou finalizado na empresa
  (finalizado indica que já houve vínculo efetivo).
"""
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from app_eventos.models import ContratoFreelance
from app_eventos.models_freelancer_empresa import FreelancerPrestacaoServico
from app_eventos.models_pagamento_freelancers import (
    FichamentoSemanaFreelancer,
    LancamentoDescontoFreelancer,
    LancamentoPagoDiarioFreelancer,
)

logger = logging.getLogger(__name__)


def registrar_freelancer_na_empresa(
    empresa_contratante_id,
    freelance_id,
    *,
    observacoes_primeira_inclusao=None,
):
    if not empresa_contratante_id or not freelance_id:
        return
    defaults = {'ativo': True}
    if observacoes_primeira_inclusao:
        defaults['observacoes'] = observacoes_primeira_inclusao
    FreelancerPrestacaoServico.objects.get_or_create(
        empresa_contratante_id=empresa_contratante_id,
        freelance_id=freelance_id,
        defaults=defaults,
    )


@receiver(post_save, sender=LancamentoPagoDiarioFreelancer)
def prestacao_ao_lancar_pago(sender, instance, **kwargs):
    if not instance.fichamento_id:
        return
    try:
        f = FichamentoSemanaFreelancer.objects.only('empresa_contratante_id').get(pk=instance.fichamento_id)
        registrar_freelancer_na_empresa(f.empresa_contratante_id, instance.freelance_id)
    except FichamentoSemanaFreelancer.DoesNotExist:
        pass


@receiver(post_save, sender=LancamentoDescontoFreelancer)
def prestacao_ao_lancar_desconto(sender, instance, **kwargs):
    if not instance.fichamento_id:
        return
    try:
        f = FichamentoSemanaFreelancer.objects.only('empresa_contratante_id').get(pk=instance.fichamento_id)
        registrar_freelancer_na_empresa(f.empresa_contratante_id, instance.freelance_id)
    except FichamentoSemanaFreelancer.DoesNotExist:
        pass


@receiver(post_save, sender=ContratoFreelance)
def prestacao_ao_contratar(sender, instance, **kwargs):
    if instance.status not in ('ativo', 'finalizado'):
        return
    if not instance.vaga_id:
        return
    from app_eventos.models import Vaga

    try:
        v = Vaga.objects.only('empresa_contratante_id').get(pk=instance.vaga_id)
        registrar_freelancer_na_empresa(
            v.empresa_contratante_id,
            instance.freelance_id,
            observacoes_primeira_inclusao=(
                'Incluído no cadastro desta empresa após contratação '
                '(histórico e avaliações passam a ser tratados neste contexto).'
            ),
        )
    except Vaga.DoesNotExist:
        pass
