"""
Regras de ligação entre presença/faltas e histórico na empresa (FreelancerPrestacaoServico).

Quando o registo tem empresa definida, exige-se par ativo na tabela de prestação de serviço,
para alinhar operação com quem já tem vínculo registado na empresa.
"""
from __future__ import annotations

from django.core.exceptions import ValidationError

from app_eventos.models_freelancer_empresa import FreelancerPrestacaoServico


def validar_prestacao_para_registro_presenca(freelance, empresa) -> None:
    """
    Se `empresa` é None (ex.: admin a registar contexto global), não valida.

    Caso contrário, o freelancer deve ter `FreelancerPrestacaoServico` ativo para essa empresa.
    """
    if empresa is None:
        return
    if FreelancerPrestacaoServico.objects.filter(
        freelance=freelance,
        empresa_contratante=empresa,
        ativo=True,
    ).exists():
        return
    raise ValidationError(
        [
            'Este freelancer não tem histórico ativo (prestação de serviço) nesta empresa. '
            'Associe-o antes de registar presença ou faltas neste contexto.'
        ]
    )


def freelancer_tem_prestacao_ativa(freelance_id: int, empresa_id: int) -> bool:
    """Útil para filtros e evolução (ranking por empresa)."""
    return FreelancerPrestacaoServico.objects.filter(
        freelance_id=freelance_id,
        empresa_contratante_id=empresa_id,
        ativo=True,
    ).exists()
