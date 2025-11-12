from django.contrib import admin

from .models import OrcamentoOperacional


@admin.register(OrcamentoOperacional)
class OrcamentoOperacionalAdmin(admin.ModelAdmin):
    list_display = ("evento", "subtotal", "margem", "total", "tipo_precificacao", "data_calculo")
    search_fields = ("evento__nome",)
    autocomplete_fields = ("evento",)

