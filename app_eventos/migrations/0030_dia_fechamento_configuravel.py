# Generated manually for configurable weekly closing day

import datetime
from django.db import migrations, models


def forwards_preencher_data_fechamento(apps, schema_editor):
    Fichamento = apps.get_model('app_eventos', 'FichamentoSemanaFreelancer')
    for row in Fichamento.objects.all():
        q = row.data_quarta_inicio
        fechamento = q + datetime.timedelta(days=6)
        row.data_fechamento = fechamento
        row.dia_semana_fechamento = fechamento.weekday()
        row.save(update_fields=['data_fechamento', 'dia_semana_fechamento'])


def backwards_noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('app_eventos', '0029_pagamento_freelancer_por_estabelecimento'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='fichamentosemanafreelancer',
            name='uniq_fichamento_semana_por_estabelecimento',
        ),
        migrations.RemoveIndex(
            model_name='fichamentosemanafreelancer',
            name='app_eventos_empresa_8d2891_idx',
        ),
        migrations.AddField(
            model_name='pontooperacao',
            name='dia_semana_fechamento',
            field=models.PositiveSmallIntegerField(
                blank=True,
                choices=[
                    (0, 'Segunda-feira'),
                    (1, 'Terça-feira'),
                    (2, 'Quarta-feira'),
                    (3, 'Quinta-feira'),
                    (4, 'Sexta-feira'),
                    (5, 'Sábado'),
                    (6, 'Domingo'),
                ],
                help_text='Dia em que termina cada período semanal de 7 dias. Pode ser sobrescrito por fichamento.',
                null=True,
                verbose_name='Dia da semana de fechamento (pagamento freelancer)',
            ),
        ),
        migrations.AddField(
            model_name='fichamentosemanafreelancer',
            name='data_fechamento',
            field=models.DateField(
                help_text='Último dia da semana de pagamento (7 dias), deve ser o mesmo dia da semana configurado.',
                null=True,
                verbose_name='Data de fechamento do período',
            ),
        ),
        migrations.AddField(
            model_name='fichamentosemanafreelancer',
            name='dia_semana_fechamento',
            field=models.PositiveSmallIntegerField(
                blank=True,
                choices=[
                    (0, 'Segunda-feira'),
                    (1, 'Terça-feira'),
                    (2, 'Quarta-feira'),
                    (3, 'Quinta-feira'),
                    (4, 'Sexta-feira'),
                    (5, 'Sábado'),
                    (6, 'Domingo'),
                ],
                help_text='Se vazio, usa o dia configurado no ponto de operação.',
                null=True,
                verbose_name='Dia de fechamento (sobrescreve o estabelecimento)',
            ),
        ),
        migrations.RunPython(forwards_preencher_data_fechamento, backwards_noop),
        migrations.RemoveField(
            model_name='fichamentosemanafreelancer',
            name='data_quarta_inicio',
        ),
        migrations.AlterField(
            model_name='fichamentosemanafreelancer',
            name='data_fechamento',
            field=models.DateField(
                help_text='Último dia da semana de pagamento (7 dias), deve ser o mesmo dia da semana configurado.',
                verbose_name='Data de fechamento do período',
            ),
        ),
        migrations.AddIndex(
            model_name='fichamentosemanafreelancer',
            index=models.Index(
                fields=['empresa_contratante', 'ponto_operacao', 'data_fechamento'],
                name='app_eventos_empresa_fe_idx',
            ),
        ),
        migrations.AddConstraint(
            model_name='fichamentosemanafreelancer',
            constraint=models.UniqueConstraint(
                fields=('empresa_contratante', 'ponto_operacao', 'data_fechamento'),
                name='uniq_fichamento_semana_por_estabelecimento',
            ),
        ),
    ]
