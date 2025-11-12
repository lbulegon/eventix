from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("app_eventos", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Briefing",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("proposito", models.TextField()),
                ("experiencia_desejada", models.TextField(blank=True)),
                ("tipo_servico", models.CharField(max_length=100)),
                ("publico_estimado", models.PositiveIntegerField(default=0)),
                ("restricoes_alimentares", models.TextField(blank=True)),
                ("orcamento_disponivel", models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ("infraestrutura_local", models.TextField(blank=True)),
                ("observacoes", models.TextField(blank=True)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                (
                    "evento",
                    models.OneToOneField(on_delete=models.CASCADE, related_name="briefing", to="app_eventos.evento"),
                ),
            ],
            options={
                "verbose_name": "Briefing",
                "verbose_name_plural": "Briefings",
            },
        ),
    ]

