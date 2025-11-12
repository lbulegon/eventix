from django.db import models


class Menu(models.Model):
    evento = models.ForeignKey(
        "app_eventos.Evento",
        on_delete=models.CASCADE,
        related_name="menus",
    )
    titulo = models.CharField(max_length=100)
    observacoes = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Menu"
        verbose_name_plural = "Menus"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.titulo} - {self.evento.nome}"


class Prato(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name="pratos")
    nome = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50)
    custo_estimado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tempo_preparo_min = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Prato"
        verbose_name_plural = "Pratos"
        ordering = ["nome"]

    def __str__(self):
        return f"{self.nome} ({self.menu.titulo})"


class FichaTecnica(models.Model):
    prato = models.ForeignKey(Prato, on_delete=models.CASCADE, related_name="fichas")
    modo_preparo = models.TextField()
    rendimento = models.DecimalField(max_digits=8, decimal_places=2)
    tempo_execucao = models.IntegerField(default=0)
    insumos = models.JSONField(default=dict)

    class Meta:
        verbose_name = "Ficha Técnica"
        verbose_name_plural = "Fichas Técnicas"

    def __str__(self):
        return f"Ficha - {self.prato.nome}"

