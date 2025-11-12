from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("app_eventos", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="MiseEnPlace",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("tarefa", models.CharField(max_length=255)),
                ("tempo_estimado_min", models.IntegerField(default=0)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pendente", "Pendente"),
                            ("em_execucao", "Em execução"),
                            ("concluido", "Concluído"),
                        ],
                        default="pendente",
                        max_length=15,
                    ),
                ),
                ("qr_code_url", models.CharField(blank=True, max_length=255)),
                (
                    "evento",
                    models.ForeignKey(on_delete=models.CASCADE, to="app_eventos.evento"),
                ),
                (
                    "responsavel",
                    models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, to="app_eventos.freelance"),
                ),
                (
                    "setor",
                    models.ForeignKey(on_delete=models.PROTECT, to="app_eventos.setorevento"),
                ),
            ],
            options={
                "verbose_name": "Mise en Place",
                "verbose_name_plural": "Mise en Place",
                "ordering": ["setor__nome", "tarefa"],
            },
        ),
    ]

