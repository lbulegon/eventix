from django.contrib import admin

from .models import MiseEnPlace


@admin.register(MiseEnPlace)
class MiseEnPlaceAdmin(admin.ModelAdmin):
    list_display = ("evento", "setor", "tarefa", "status")
    search_fields = ("tarefa", "setor__nome", "evento__nome")
    list_filter = ("status", "setor__nome")
    autocomplete_fields = ("evento", "setor", "responsavel")

