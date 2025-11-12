from django.urls import path

from .views import OrcamentoOperacionalView


app_name = "financeiro"


urlpatterns = [
    path(
        "eventos/<int:evento_id>/orcamento/gerar",
        OrcamentoOperacionalView.as_view(),
        name="orcamento_gerar",
    ),
]

