from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("app_eventos", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Menu",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("titulo", models.CharField(max_length=100)),
                ("observacoes", models.TextField(blank=True)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                (
                    "evento",
                    models.ForeignKey(on_delete=models.CASCADE, related_name="menus", to="app_eventos.evento"),
                ),
            ],
            options={
                "verbose_name": "Menu",
                "verbose_name_plural": "Menus",
                "ordering": ["-criado_em"],
            },
        ),
        migrations.CreateModel(
            name="Prato",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=100)),
                ("categoria", models.CharField(max_length=50)),
                ("custo_estimado", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("tempo_preparo_min", models.IntegerField(default=0)),
                (
                    "menu",
                    models.ForeignKey(on_delete=models.CASCADE, related_name="pratos", to="app_menu.menu"),
                ),
            ],
            options={
                "verbose_name": "Prato",
                "verbose_name_plural": "Pratos",
                "ordering": ["nome"],
            },
        ),
        migrations.CreateModel(
            name="FichaTecnica",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("modo_preparo", models.TextField()),
                ("rendimento", models.DecimalField(decimal_places=2, max_digits=8)),
                ("tempo_execucao", models.IntegerField(default=0)),
                ("insumos", models.JSONField(default=dict)),
                (
                    "prato",
                    models.ForeignKey(on_delete=models.CASCADE, related_name="fichas", to="app_menu.prato"),
                ),
            ],
            options={
                "verbose_name": "Ficha Técnica",
                "verbose_name_plural": "Fichas Técnicas",
            },
        ),
    ]

