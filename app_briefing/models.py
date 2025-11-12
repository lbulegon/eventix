from django.db import models


class Briefing(models.Model):
    evento = models.OneToOneField(
        "app_eventos.Evento",
        on_delete=models.CASCADE,
        related_name="briefing",
    )
    proposito = models.TextField()
    experiencia_desejada = models.TextField(blank=True)
    tipo_servico = models.CharField(max_length=100)
    publico_estimado = models.PositiveIntegerField(default=0)
    restricoes_alimentares = models.TextField(blank=True)
    orcamento_disponivel = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    infraestrutura_local = models.TextField(blank=True)
    observacoes = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Briefing"
        verbose_name_plural = "Briefings"

    def __str__(self):
        return f"Briefing - {self.evento.nome}"

