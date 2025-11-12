from django.contrib import admin

from .models import FichaTecnica, Menu, Prato


class FichaTecnicaInline(admin.TabularInline):
    model = FichaTecnica
    extra = 0


class PratoInline(admin.TabularInline):
    model = Prato
    extra = 0


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ("titulo", "evento", "criado_em")
    search_fields = ("titulo", "evento__nome")
    autocomplete_fields = ("evento",)
    inlines = [PratoInline]


@admin.register(Prato)
class PratoAdmin(admin.ModelAdmin):
    list_display = ("nome", "menu", "categoria", "custo_estimado")
    search_fields = ("nome", "menu__titulo")
    list_filter = ("categoria",)
    inlines = [FichaTecnicaInline]


@admin.register(FichaTecnica)
class FichaTecnicaAdmin(admin.ModelAdmin):
    list_display = ("prato", "rendimento", "tempo_execucao")
    search_fields = ("prato__nome",)

