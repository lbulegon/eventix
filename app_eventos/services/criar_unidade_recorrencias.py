"""
Cria UnidadeOperacional + RegraRecorrencia + RegraRecorrenciaFuncao numa única transação.
"""
from typing import List, Optional

from django.core.exceptions import ValidationError
from django.db import transaction

from app_eventos.models import EmpresaContratante, Funcao
from app_eventos.models_operacao_continua import (
    RegraRecorrencia,
    RegraRecorrenciaFuncao,
    UnidadeOperacional,
)


def _validar_funcao_tenant(funcao: Funcao, empresa: EmpresaContratante):
    if not funcao.empresa_contratante_id:
        raise ValidationError(
            {'funcao': f'Função id={funcao.pk} não está vinculada a uma empresa; use uma função do tenant.'}
        )
    if funcao.empresa_contratante_id != empresa.pk:
        raise ValidationError({'funcao': f'Função id={funcao.pk} não pertence à empresa contratante.'})


@transaction.atomic
def criar_unidade_com_recorrencias(
    empresa_contratante: EmpresaContratante,
    *,
    tipo: str,
    nome: str,
    descricao: str,
    evento_id: Optional[int],
    ponto_operacao_id: Optional[int],
    data_inicio,
    data_fim,
    ativo: bool,
    recorrencias: List[dict],
):
    """
    recorrencias: list of dicts with keys:
      nome (optional), dias_semana, hora_inicio, hora_fim (time), vagas: [{funcao_id, quantidade}, ...]
    """
    unidade = UnidadeOperacional(
        empresa_contratante=empresa_contratante,
        nome=nome,
        descricao=descricao or None,
        tipo=tipo,
        evento_id=evento_id if tipo == UnidadeOperacional.TIPO_EVENTO else None,
        ponto_operacao_id=ponto_operacao_id if tipo == UnidadeOperacional.TIPO_OPERACAO else None,
        data_inicio=data_inicio,
        data_fim=data_fim,
        ativo=ativo,
    )
    unidade.full_clean()
    unidade.save()

    regras_criadas = []

    for item in recorrencias:
        regra = RegraRecorrencia(
            unidade=unidade,
            nome=(item.get('nome') or '')[:120],
            dias_semana=item['dias_semana'],
            hora_inicio=item['hora_inicio'],
            hora_fim=item['hora_fim'],
            ativo=True,
        )
        regra.full_clean()
        regra.save()

        demandas = item.get('vagas') or []
        n_dem = 0
        for d in demandas:
            fid = d.get('funcao')
            if fid is None:
                fid = d.get('funcao_id')
            q = int(d.get('quantidade', 1))
            try:
                funcao = Funcao.objects.get(pk=fid)
            except Funcao.DoesNotExist:
                raise ValidationError({'funcao': f'Função id={fid} não encontrada.'}) from None
            _validar_funcao_tenant(funcao, empresa_contratante)
            rf = RegraRecorrenciaFuncao(regra=regra, funcao=funcao, quantidade=q)
            rf.full_clean()
            rf.save()
            n_dem += 1

        regras_criadas.append(
            {
                'id': regra.pk,
                'nome': regra.nome,
                'demandas_criadas': n_dem,
            }
        )

    return unidade, regras_criadas
