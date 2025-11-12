from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("app_eventos", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="OperacaoEvento",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("inicio_real", models.DateTimeField(blank=True, null=True)),
                ("fim_real", models.DateTimeField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("em_preparacao", "Em preparação"),
                            ("em_execucao", "Em execução"),
                            ("finalizado", "Finalizado"),
                        ],
                        default="em_preparacao",
                        max_length=15,
                    ),
                ),
                ("timeline", models.JSONField(default=dict)),
                (
                    "evento",
                    models.OneToOneField(on_delete=models.CASCADE, to="app_eventos.evento"),
                ),
            ],
            options={
                "verbose_name": "Operação do Evento",
                "verbose_name_plural": "Operações do Evento",
            },
        ),
    ]

