from django.urls import path

from .views import FinalizacaoEventoView


app_name = "finalizacao"


urlpatterns = [
    path(
        "eventos/<int:evento_id>/finalizacao/",
        FinalizacaoEventoView.as_view(),
        name="finalizacao",
    ),
]

