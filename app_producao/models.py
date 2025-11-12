from django.db import models


class CronogramaPreProducao(models.Model):
    STATUS_CHOICES = [
        ("pendente", "Pendente"),
        ("em_andamento", "Em andamento"),
        ("concluido", "Concluído"),
    ]

    evento = models.ForeignKey("app_eventos.Evento", on_delete=models.CASCADE)
    etapa = models.CharField(max_length=100)
    prazo = models.DateTimeField()
    responsavel = models.ForeignKey(
        "app_eventos.Freelance",
        null=True,
        on_delete=models.SET_NULL,
        blank=True,
    )
    status = models.CharField(max_length=15, default="pendente", choices=STATUS_CHOICES)
    observacoes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Cronograma de Pré-produção"
        verbose_name_plural = "Cronogramas de Pré-produção"
        ordering = ["prazo"]

    def __str__(self):
        return f"{self.etapa} - {self.evento.nome}"

