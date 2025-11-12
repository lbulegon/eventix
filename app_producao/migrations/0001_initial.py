from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("app_eventos", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="CronogramaPreProducao",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("etapa", models.CharField(max_length=100)),
                ("prazo", models.DateTimeField()),
                (
                    "responsavel",
                    models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, to="app_eventos.freelance"),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pendente", "Pendente"),
                            ("em_andamento", "Em andamento"),
                            ("concluido", "Concluído"),
                        ],
                        default="pendente",
                        max_length=15,
                    ),
                ),
                ("observacoes", models.TextField(blank=True)),
                ("evento", models.ForeignKey(on_delete=models.CASCADE, to="app_eventos.evento")),
            ],
            options={
                "verbose_name": "Cronograma de Pré-produção",
                "verbose_name_plural": "Cronogramas de Pré-produção",
                "ordering": ["prazo"],
            },
        ),
    ]

