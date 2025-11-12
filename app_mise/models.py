from django.db import models


class MiseEnPlace(models.Model):
    STATUS_CHOICES = [
        ("pendente", "Pendente"),
        ("em_execucao", "Em execução"),
        ("concluido", "Concluído"),
    ]

    evento = models.ForeignKey("app_eventos.Evento", on_delete=models.CASCADE)
    setor = models.ForeignKey("app_eventos.SetorEvento", on_delete=models.PROTECT)
    tarefa = models.CharField(max_length=255)
    responsavel = models.ForeignKey(
        "app_eventos.Freelance",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    tempo_estimado_min = models.IntegerField(default=0)
    status = models.CharField(max_length=15, default="pendente", choices=STATUS_CHOICES)
    qr_code_url = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Mise en Place"
        verbose_name_plural = "Mise en Place"
        ordering = ["setor__nome", "tarefa"]

    def __str__(self):
        return f"{self.tarefa} - {self.setor.nome}"
