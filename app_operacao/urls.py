from django.urls import path

from .views import OperacaoEventoView


app_name = "operacao"


urlpatterns = [
    path(
        "eventos/<int:evento_id>/operacao/timeline",
        OperacaoEventoView.as_view(),
        name="operacao_timeline",
    ),
]

