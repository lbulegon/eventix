# Generated manually — Grupo empresarial + gestor_grupo

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_eventos', '0037_freelance_confiabilidade_presenca'),
    ]

    operations = [
        migrations.CreateModel(
            name='GrupoEmpresarial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=255, verbose_name='Nome do grupo')),
                ('nome_fantasia', models.CharField(blank=True, max_length=255, verbose_name='Nome fantasia')),
                ('cnpj', models.CharField(blank=True, help_text='CNPJ da holding / grupo, se existir.', max_length=18, null=True, verbose_name='CNPJ (opcional)')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo')),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Grupo empresarial',
                'verbose_name_plural': 'Grupos empresariais',
                'ordering': ['nome'],
            },
        ),
        migrations.AddField(
            model_name='empresacontratante',
            name='grupo_empresarial',
            field=models.ForeignKey(
                blank=True,
                help_text='Opcional. Agrupa este CNPJ (empresa contratante) com outros sob o mesmo grupo; gestores do grupo visualizam todas as operações.',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='empresas_contratantes',
                to='app_eventos.grupoempresarial',
                verbose_name='Grupo empresarial',
            ),
        ),
        migrations.AddField(
            model_name='user',
            name='grupo_empresarial',
            field=models.ForeignKey(
                blank=True,
                help_text='Obrigatório para tipo gestor_grupo: agrupa vários CNPJs; o gestor vê todas as operações.',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='gestores',
                to='app_eventos.grupoempresarial',
                verbose_name='Grupo empresarial',
            ),
        ),
        migrations.AlterField(
            model_name='user',
            name='tipo_usuario',
            field=models.CharField(
                choices=[
                    ('admin_empresa', 'Administrador da Empresa'),
                    ('operador_empresa', 'Operador da Empresa'),
                    ('gestor_grupo', 'Gestor do Grupo Empresarial'),
                    ('freelancer', 'Freelancer'),
                    ('admin_sistema', 'Administrador do Sistema'),
                ],
                default='freelancer',
                max_length=22,
            ),
        ),
    ]
