import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_eventos', '0039_ponto_operacao_one_per_empresa'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pontooperacao',
            name='empresa_contratante',
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='ponto_operacao',
                to='app_eventos.empresacontratante',
                verbose_name='Empresa Contratante',
            ),
        ),
    ]
