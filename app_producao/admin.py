from django.contrib import admin

from .models import CronogramaPreProducao


@admin.register(CronogramaPreProducao)
class CronogramaPreProducaoAdmin(admin.ModelAdmin):
    list_display = ("evento", "etapa", "prazo", "status")
    search_fields = ("evento__nome", "etapa")
    list_filter = ("status",)
    autocomplete_fields = ("evento", "responsavel")

