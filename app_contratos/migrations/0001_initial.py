from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("app_eventos", "0001_initial"),
        ("app_financeiro", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ContratoEvento",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("pdf_url", models.CharField(blank=True, max_length=255)),
                ("assinatura_cliente", models.BooleanField(default=False)),
                ("data_assinatura", models.DateTimeField(blank=True, null=True)),
                ("condicoes_gerais", models.TextField()),
                (
                    "evento",
                    models.OneToOneField(on_delete=models.CASCADE, to="app_eventos.evento"),
                ),
                (
                    "orcamento",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.SET_NULL,
                        to="app_financeiro.orcamentooperacional",
                    ),
                ),
            ],
            options={
                "verbose_name": "Contrato do Evento",
                "verbose_name_plural": "Contratos de Eventos",
            },
        ),
    ]

