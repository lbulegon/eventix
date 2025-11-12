from django.contrib import admin

from .models import InsightEvento


@admin.register(InsightEvento)
class InsightEventoAdmin(admin.ModelAdmin):
    list_display = ("evento_base", "relevancia", "criado_em")
    search_fields = ("evento_base__nome", "recomendacao")
    list_filter = ("relevancia",)
    autocomplete_fields = ("evento_base",)

