from django.urls import path

from .views import ContratoAssinarView, ContratoGerarView


app_name = "contratos"


urlpatterns = [
    path(
        "eventos/<int:evento_id>/contrato/gerar",
        ContratoGerarView.as_view(),
        name="contrato_gerar",
    ),
    path(
        "eventos/<int:evento_id>/contrato/assinar",
        ContratoAssinarView.as_view(),
        name="contrato_assinar",
    ),
]

