from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("app_eventos", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="OrcamentoOperacional",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("subtotal", models.DecimalField(decimal_places=2, max_digits=12)),
                ("margem", models.DecimalField(decimal_places=2, max_digits=5)),
                ("lucro_minimo", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("total", models.DecimalField(decimal_places=2, max_digits=12)),
                (
                    "tipo_precificacao",
                    models.CharField(
                        choices=[("percentual", "percentual"), ("minimo", "minimo")],
                        max_length=20,
                    ),
                ),
                ("data_calculo", models.DateTimeField(auto_now_add=True)),
                ("detalhes_custos", models.JSONField(default=dict)),
                (
                    "evento",
                    models.OneToOneField(
                        on_delete=models.CASCADE, related_name="orcamento_operacional", to="app_eventos.evento"
                    ),
                ),
            ],
            options={
                "verbose_name": "Orçamento Operacional",
                "verbose_name_plural": "Orçamentos Operacionais",
            },
        ),
    ]

