from django.db import models


class OrcamentoOperacional(models.Model):
    TIPO_PRECIFICACAO_CHOICES = [
        ("percentual", "percentual"),
        ("minimo", "minimo"),
    ]

    evento = models.OneToOneField(
        "app_eventos.Evento",
        on_delete=models.CASCADE,
        related_name="orcamento_operacional",
    )
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    margem = models.DecimalField(max_digits=5, decimal_places=2)
    lucro_minimo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    tipo_precificacao = models.CharField(max_length=20, choices=TIPO_PRECIFICACAO_CHOICES)
    data_calculo = models.DateTimeField(auto_now_add=True)
    detalhes_custos = models.JSONField(default=dict)

    class Meta:
        verbose_name = "Orçamento Operacional"
        verbose_name_plural = "Orçamentos Operacionais"

    def __str__(self):
        return f"Orçamento {self.evento.nome}"

