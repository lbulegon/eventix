from django.contrib import admin

from .models import FinalizacaoEvento


@admin.register(FinalizacaoEvento)
class FinalizacaoEventoAdmin(admin.ModelAdmin):
    list_display = ("evento", "hora_extra", "materiais_recolhidos")
    search_fields = ("evento__nome",)
    autocomplete_fields = ("evento",)

