from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("app_eventos", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="FinalizacaoEvento",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("hora_extra", models.BooleanField(default=False)),
                ("observacoes", models.TextField(blank=True)),
                ("fechamento_bebidas", models.JSONField(default=dict)),
                ("materiais_recolhidos", models.BooleanField(default=False)),
                (
                    "evento",
                    models.OneToOneField(on_delete=models.CASCADE, to="app_eventos.evento"),
                ),
            ],
            options={
                "verbose_name": "Finalização do Evento",
                "verbose_name_plural": "Finalizações de Eventos",
            },
        ),
    ]

