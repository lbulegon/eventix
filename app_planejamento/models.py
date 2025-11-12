from django.db import models


class InsightEvento(models.Model):
    evento_base = models.ForeignKey("app_eventos.Evento", on_delete=models.CASCADE)
    recomendacao = models.TextField()
    relevancia = models.IntegerField(default=0)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Insight de Evento"
        verbose_name_plural = "Insights de Eventos"
        ordering = ["-relevancia", "-criado_em"]

    def __str__(self):
        return f"Insight - {self.evento_base.nome}"

