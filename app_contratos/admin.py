from django.contrib import admin

from .models import ContratoEvento


@admin.register(ContratoEvento)
class ContratoEventoAdmin(admin.ModelAdmin):
    list_display = ("evento", "assinatura_cliente", "data_assinatura")
    search_fields = ("evento__nome",)
    autocomplete_fields = ("evento", "orcamento")

