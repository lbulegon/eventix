from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("app_eventos", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="FechamentoInterno",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("perdas", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("extravios", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("custo_real", models.DecimalField(decimal_places=2, max_digits=12)),
                ("lucro_liquido", models.DecimalField(decimal_places=2, max_digits=12)),
                ("aprendizado", models.TextField(blank=True)),
                ("indicadores", models.JSONField(default=dict)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                (
                    "evento",
                    models.OneToOneField(on_delete=models.CASCADE, to="app_eventos.evento"),
                ),
            ],
            options={
                "verbose_name": "Fechamento Interno",
                "verbose_name_plural": "Fechamentos Internos",
            },
        ),
    ]

