from django.db import models


class ContratoEvento(models.Model):
    evento = models.OneToOneField("app_eventos.Evento", on_delete=models.CASCADE)
    orcamento = models.ForeignKey(
        "app_financeiro.OrcamentoOperacional",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    pdf_url = models.CharField(max_length=255, blank=True)
    assinatura_cliente = models.BooleanField(default=False)
    data_assinatura = models.DateTimeField(null=True, blank=True)
    condicoes_gerais = models.TextField()

    class Meta:
        verbose_name = "Contrato do Evento"
        verbose_name_plural = "Contratos de Eventos"

    def __str__(self):
        return f"Contrato - {self.evento.nome}"

