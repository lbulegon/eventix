from django.db import models


class OperacaoEvento(models.Model):
    STATUS_CHOICES = [
        ("em_preparacao", "Em preparação"),
        ("em_execucao", "Em execução"),
        ("finalizado", "Finalizado"),
    ]

    evento = models.OneToOneField("app_eventos.Evento", on_delete=models.CASCADE)
    inicio_real = models.DateTimeField(null=True, blank=True)
    fim_real = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=15, default="em_preparacao", choices=STATUS_CHOICES)
    timeline = models.JSONField(default=dict)

    class Meta:
        verbose_name = "Operação do Evento"
        verbose_name_plural = "Operações do Evento"

    def __str__(self):
        return f"Operação - {self.evento.nome}"

