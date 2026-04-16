# Um PontoOperacao por EmpresaContratante: merge de duplicados + OneToOneField

from decimal import Decimal

from django.db import migrations
from django.db.models import Count


def _merge_fichamentos(keeper_id, dup_id, apps):
    Fichamento = apps.get_model('app_eventos', 'FichamentoSemanaFreelancer')
    LancamentoPago = apps.get_model('app_eventos', 'LancamentoPagoDiarioFreelancer')
    LancamentoDesc = apps.get_model('app_eventos', 'LancamentoDescontoFreelancer')

    for fich_dup in list(Fichamento.objects.filter(ponto_operacao_id=dup_id)):
        fich_keep = Fichamento.objects.filter(
            empresa_contratante_id=fich_dup.empresa_contratante_id,
            ponto_operacao_id=keeper_id,
            data_fechamento=fich_dup.data_fechamento,
        ).first()
        if fich_keep is None:
            fich_dup.ponto_operacao_id = keeper_id
            fich_dup.save(update_fields=['ponto_operacao_id'])
            continue

        for lp in list(LancamentoPago.objects.filter(fichamento_id=fich_dup.id)):
            other = LancamentoPago.objects.filter(
                fichamento_id=fich_keep.id,
                freelance_id=lp.freelance_id,
                data=lp.data,
            ).first()
            if other is None:
                lp.fichamento_id = fich_keep.id
                lp.save(update_fields=['fichamento_id'])
            elif lp.eh_folga and other.eh_folga:
                lp.delete()
            elif other.eh_folga and not lp.eh_folga:
                other.eh_folga = False
                other.valor_bruto = lp.valor_bruto
                if lp.contrato_freelance_id:
                    other.contrato_freelance_id = lp.contrato_freelance_id
                other.save()
                lp.delete()
            elif not other.eh_folga and lp.eh_folga:
                lp.delete()
            else:
                other.valor_bruto = (other.valor_bruto or Decimal('0')) + (lp.valor_bruto or Decimal('0'))
                other.save(update_fields=['valor_bruto'])
                lp.delete()

        for ld in LancamentoDesc.objects.filter(fichamento_id=fich_dup.id):
            ld.fichamento_id = fich_keep.id
            ld.save(update_fields=['fichamento_id'])

        fich_dup.delete()


def _merge_tarifas_e_calendario(keeper_id, dup_id, apps):
    Tarifa = apps.get_model('app_eventos', 'TarifaDiariaPorFuncaoPonto')
    DataCal = apps.get_model('app_eventos', 'DataCalendarioTarifa')

    for t in list(Tarifa.objects.filter(ponto_operacao_id=dup_id)):
        exists = Tarifa.objects.filter(
            empresa_contratante_id=t.empresa_contratante_id,
            ponto_operacao_id=keeper_id,
            funcao_id=t.funcao_id,
        ).exists()
        if exists:
            t.delete()
        else:
            t.ponto_operacao_id = keeper_id
            t.save(update_fields=['ponto_operacao_id'])

    for d in list(DataCal.objects.filter(ponto_operacao_id=dup_id)):
        exists = DataCal.objects.filter(
            ponto_operacao_id=keeper_id,
            data=d.data,
        ).exists()
        if exists:
            d.delete()
        else:
            d.ponto_operacao_id = keeper_id
            d.save(update_fields=['ponto_operacao_id'])


def _merge_into(keeper_id, dup_id, apps):
    Vaga = apps.get_model('app_eventos', 'Vaga')
    UnidadeOperacional = apps.get_model('app_eventos', 'UnidadeOperacional')
    PontoOperacao = apps.get_model('app_eventos', 'PontoOperacao')

    _merge_fichamentos(keeper_id, dup_id, apps)
    _merge_tarifas_e_calendario(keeper_id, dup_id, apps)
    Vaga.objects.filter(ponto_operacao_id=dup_id).update(ponto_operacao_id=keeper_id)
    UnidadeOperacional.objects.filter(ponto_operacao_id=dup_id).update(ponto_operacao_id=keeper_id)
    PontoOperacao.objects.filter(pk=dup_id).delete()


def merge_duplicate_pontos(apps, schema_editor):
    PontoOperacao = apps.get_model('app_eventos', 'PontoOperacao')
    dup_ec = (
        PontoOperacao.objects.values('empresa_contratante_id')
        .annotate(c=Count('id'))
        .filter(c__gt=1)
    )
    for row in dup_ec:
        ec_id = row['empresa_contratante_id']
        pontos = list(
            PontoOperacao.objects.filter(empresa_contratante_id=ec_id).order_by('-ativo', 'id')
        )
        if len(pontos) < 2:
            continue
        keeper_id = pontos[0].id
        for dup in pontos[1:]:
            _merge_into(keeper_id, dup.id, apps)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('app_eventos', '0038_grupo_empresarial_gestor'),
    ]

    operations = [
        migrations.RunPython(merge_duplicate_pontos, noop_reverse),
    ]
