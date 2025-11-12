from django.urls import path

from .views import CronogramaPreProducaoView


app_name = "producao"


urlpatterns = [
    path(
        "eventos/<int:evento_id>/preproducao/cronograma",
        CronogramaPreProducaoView.as_view(),
        name="preproducao_cronograma",
    ),
]

