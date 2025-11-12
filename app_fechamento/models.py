from django.db import models


class FechamentoInterno(models.Model):
    evento = models.OneToOneField("app_eventos.Evento", on_delete=models.CASCADE)
    perdas = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    extravios = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    custo_real = models.DecimalField(max_digits=12, decimal_places=2)
    lucro_liquido = models.DecimalField(max_digits=12, decimal_places=2)
    aprendizado = models.TextField(blank=True)
    indicadores = models.JSONField(default=dict)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Fechamento Interno"
        verbose_name_plural = "Fechamentos Internos"

    def __str__(self):
        return f"Fechamento Interno - {self.evento.nome}"

