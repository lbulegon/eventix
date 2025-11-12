from django.contrib import admin

from .models import Briefing


@admin.register(Briefing)
class BriefingAdmin(admin.ModelAdmin):
    list_display = ("evento", "tipo_servico", "publico_estimado", "criado_em")
    search_fields = ("evento__nome", "tipo_servico")
    autocomplete_fields = ("evento",)

