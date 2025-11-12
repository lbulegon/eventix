from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("app_eventos", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="InsightEvento",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("recomendacao", models.TextField()),
                ("relevancia", models.IntegerField(default=0)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                (
                    "evento_base",
                    models.ForeignKey(on_delete=models.CASCADE, to="app_eventos.evento"),
                ),
            ],
            options={
                "verbose_name": "Insight de Evento",
                "verbose_name_plural": "Insights de Eventos",
                "ordering": ["-relevancia", "-criado_em"],
            },
        ),
    ]

