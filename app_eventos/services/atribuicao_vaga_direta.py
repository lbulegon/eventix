"""
Atribuição de freelancer a uma vaga de estabelecimento (ponto de operação) sem candidatura.

Cria ContratoFreelance ativo e incrementa quantidade_preenchida da vaga, como em Candidatura.aprovar().
"""
from django.core.exceptions import ValidationError
from django.db import transaction

from app_eventos.models import ContratoFreelance, Freelance, Vaga
from app_eventos.models_freelancer_empresa import FreelancerPrestacaoServico


def atribuir_freelancer_a_vaga_direto(
    freelance: Freelance,
    vaga: Vaga,
    *,
    exigir_prestacao_servico: bool = False,
    ignorar_limite_vagas: bool = False,
    exigir_vaga_ativa: bool = True,
):
    """
    Vincula o freelancer à vaga com contrato ativo, sem passar por Candidatura.

    Regras:
    - Vaga deve ser de Ponto de Operação (estabelecimento), não de evento isolado.
    - Opcionalmente exige registo em FreelancerPrestacaoServico para o mesmo tenant.
    - Não duplica contrato ativo para o mesmo par (freelance, vaga).
    - Respeita limite quantidade / quantidade_preenchida salvo se ignorar_limite_vagas=False.

    Returns:
        tuple: (ContratoFreelance, dict meta) onde meta inclui 'criado' (bool) e 'mensagem' (str).
    """
    if not vaga.ponto_operacao_id:
        raise ValidationError(
            'Esta rotina aplica-se a vagas de estabelecimento (ponto de operação). '
            'A vaga indicada está ligada a evento, não a um ponto de operação.'
        )

    if exigir_vaga_ativa and not vaga.ativa:
        raise ValidationError('A vaga não está ativa.')

    if exigir_prestacao_servico:
        tem_hist = FreelancerPrestacaoServico.objects.filter(
            empresa_contratante_id=vaga.empresa_contratante_id,
            freelance_id=freelance.pk,
            ativo=True,
        ).exists()
        if not tem_hist:
            raise ValidationError(
                'O freelancer não está na lista de quem já prestou serviço a esta empresa. '
                'Inclua-o no histórico ou desative a exigência de histórico na atribuição.'
            )

    existente_ativo = ContratoFreelance.objects.filter(
        freelance_id=freelance.pk,
        vaga_id=vaga.pk,
        status='ativo',
    ).first()
    if existente_ativo:
        return existente_ativo, {
            'criado': False,
            'mensagem': 'Já existe contrato ativo para este freelancer nesta vaga.',
        }

    if not ignorar_limite_vagas and not vaga.tem_vagas_disponiveis:
        raise ValidationError('Não há vagas disponíveis nesta posição (limite preenchido).')

    with transaction.atomic():
        vaga_locked = Vaga.objects.select_for_update().get(pk=vaga.pk)
        if not ignorar_limite_vagas and not (
            vaga_locked.quantidade_preenchida < vaga_locked.quantidade
        ):
            raise ValidationError('Não há vagas disponíveis nesta posição (limite preenchido).')

        contrato = ContratoFreelance.objects.create(
            freelance=freelance,
            vaga=vaga_locked,
            status='ativo',
        )
        vaga_locked.incrementar_preenchida()

    return contrato, {
        'criado': True,
        'mensagem': 'Freelancer atribuído à vaga com sucesso.',
    }
