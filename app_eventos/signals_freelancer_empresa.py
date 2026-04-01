"""
Garante que freelancers entram na lista "já prestaram serviço" ao:
- ter lançamento de pagamento ou desconto no fichamento da empresa;
- ter contrato de vaga na empresa.
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


def registrar_freelancer_na_empresa(empresa_contratante_id, freelance_id):
    if not empresa_contratante_id or not freelance_id:
        return
    FreelancerPrestacaoServico.objects.get_or_create(
        empresa_contratante_id=empresa_contratante_id,
        freelance_id=freelance_id,
        defaults={'ativo': True},
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
    if not instance.vaga_id:
        return
    from app_eventos.models import Vaga

    try:
        v = Vaga.objects.only('empresa_contratante_id').get(pk=instance.vaga_id)
        registrar_freelancer_na_empresa(v.empresa_contratante_id, instance.freelance_id)
    except Vaga.DoesNotExist:
        pass
