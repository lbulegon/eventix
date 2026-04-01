import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_eventos', '0030_dia_fechamento_configuravel'),
    ]

    operations = [
        migrations.AddField(
            model_name='lancamentopagodiariofreelancer',
            name='contrato_freelance',
            field=models.ForeignKey(
                blank=True,
                help_text='Opcional: vínculo com a vaga em que o freelancer foi aprovado e contratado.',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='lancamentos_pago',
                to='app_eventos.contratofreelance',
                verbose_name='Contrato (vaga contratada)',
            ),
        ),
        migrations.AddField(
            model_name='lancamentodescontofreelancer',
            name='contrato_freelance',
            field=models.ForeignKey(
                blank=True,
                help_text='Opcional: desconto associado ao contrato de uma vaga específica.',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='lancamentos_desconto',
                to='app_eventos.contratofreelance',
                verbose_name='Contrato (vaga contratada)',
            ),
        ),
    ]
