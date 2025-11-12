from django.contrib import admin

from .models import OperacaoEvento


@admin.register(OperacaoEvento)
class OperacaoEventoAdmin(admin.ModelAdmin):
    list_display = ("evento", "status", "inicio_real", "fim_real")
    search_fields = ("evento__nome",)
    autocomplete_fields = ("evento",)

