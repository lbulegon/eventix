from django.db import models


class FinalizacaoEvento(models.Model):
    evento = models.OneToOneField("app_eventos.Evento", on_delete=models.CASCADE)
    hora_extra = models.BooleanField(default=False)
    observacoes = models.TextField(blank=True)
    fechamento_bebidas = models.JSONField(default=dict)
    materiais_recolhidos = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Finalização do Evento"
        verbose_name_plural = "Finalizações de Eventos"

    def __str__(self):
        return f"Finalização - {self.evento.nome}"

