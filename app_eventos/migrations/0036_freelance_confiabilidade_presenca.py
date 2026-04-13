# Generated manually for Eventix — score de confiabilidade e registos de presença

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_eventos', '0035_empresa_modo_dashboard'),
    ]

    operations = [
        migrations.AddField(
            model_name='freelance',
            name='score_confiabilidade',
            field=models.IntegerField(default=5, verbose_name='Score de confiabilidade'),
        ),
        migrations.AddField(
            model_name='freelance',
            name='faltas_com_aviso',
            field=models.PositiveIntegerField(default=0, verbose_name='Faltas com aviso'),
        ),
        migrations.AddField(
            model_name='freelance',
            name='faltas_sem_aviso',
            field=models.PositiveIntegerField(default=0, verbose_name='Faltas sem aviso'),
        ),
        migrations.AddField(
            model_name='freelance',
            name='bloqueado',
            field=models.BooleanField(
                default=False,
                help_text='Definido automaticamente quando o score é ≤ 0.',
                verbose_name='Bloqueado (confiabilidade)',
            ),
        ),
        migrations.AddField(
            model_name='freelance',
            name='data_ultimo_evento',
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name='Data do último registo de presença',
            ),
        ),
        migrations.CreateModel(
            name='RegistroPresencaFreelancer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(verbose_name='Data')),
                (
                    'status',
                    models.CharField(
                        choices=[
                            ('presente', 'Presente'),
                            ('falta_com_aviso', 'Falta com aviso'),
                            ('falta_sem_aviso', 'Falta sem aviso'),
                        ],
                        max_length=30,
                        verbose_name='Status',
                    ),
                ),
                ('observacao', models.TextField(blank=True, null=True, verbose_name='Observação')),
                (
                    'pontuacao_aplicada',
                    models.BooleanField(
                        default=False,
                        help_text='Uso interno: garante idempotência ao aplicar o score no Freelance.',
                        verbose_name='Pontuação já aplicada',
                    ),
                ),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                (
                    'empresa',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='registros_presenca_freelancer',
                        to='app_eventos.empresacontratante',
                        verbose_name='Empresa',
                        help_text='Opcional; recomendado quando o registo é feito no contexto de uma empresa.',
                    ),
                ),
                (
                    'freelance',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='registros_presenca',
                        to='app_eventos.freelance',
                        verbose_name='Freelancer',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Registo de presença (freelancer)',
                'verbose_name_plural': 'Registos de presença (freelancers)',
                'ordering': ['-data', '-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='registropresencafreelancer',
            index=models.Index(fields=['freelance', 'data'], name='app_eventos_freelanc_2b8c8e_idx'),
        ),
        migrations.AddIndex(
            model_name='registropresencafreelancer',
            index=models.Index(fields=['empresa', 'data'], name='app_eventos_empresa_9f1a2b_idx'),
        ),
    ]
