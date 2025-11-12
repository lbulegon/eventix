from django.contrib import admin

from .models import FechamentoInterno


@admin.register(FechamentoInterno)
class FechamentoInternoAdmin(admin.ModelAdmin):
    list_display = ("evento", "custo_real", "lucro_liquido", "criado_em")
    search_fields = ("evento__nome",)
    autocomplete_fields = ("evento",)

