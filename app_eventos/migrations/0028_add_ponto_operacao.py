# Generated manually for PontoOperacao (operação permanente)

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_eventos', '0027_modulosistema_empresacontratante_modulos_contratados'),
    ]

    operations = [
        migrations.CreateModel(
            name='PontoOperacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(help_text='Ex: Restaurante Centro - Operação Diária', max_length=200, verbose_name='Nome')),
                ('descricao', models.TextField(blank=True, null=True, verbose_name='Descrição')),
                ('endereco', models.CharField(max_length=255, verbose_name='Endereço')),
                ('cidade', models.CharField(max_length=100, verbose_name='Cidade')),
                ('uf', models.CharField(max_length=2, verbose_name='UF')),
                ('cep', models.CharField(blank=True, max_length=9, null=True, verbose_name='CEP')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')),
                ('data_atualizacao', models.DateTimeField(auto_now=True, verbose_name='Data de Atualização')),
                ('empresa_contratante', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pontos_operacao', to='app_eventos.empresacontratante', verbose_name='Empresa Contratante')),
                ('local', models.ForeignKey(blank=True, help_text='Vincule a um LocalEvento existente, ou use endereço acima', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pontos_operacao', to='app_eventos.localevento', verbose_name='Local (opcional)')),
            ],
            options={
                'verbose_name': 'Ponto de Operação',
                'verbose_name_plural': 'Pontos de Operação',
                'ordering': ['nome'],
            },
        ),
        migrations.AddField(
            model_name='vaga',
            name='ponto_operacao',
            field=models.ForeignKey(blank=True, help_text='Para operação permanente (restaurante, etc.) - sem evento nem setor', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='vagas', to='app_eventos.pontooperacao', verbose_name='Ponto de Operação'),
        ),
        migrations.AddConstraint(
            model_name='vaga',
            constraint=models.CheckConstraint(
                check=(
                    models.Q(evento__isnull=False, ponto_operacao__isnull=True) |
                    models.Q(evento__isnull=True, ponto_operacao__isnull=False)
                ),
                name='vaga_evento_ou_ponto_operacao',
            ),
        ),
    ]
