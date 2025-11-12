from django.urls import path

from .views import FechamentoInternoView


app_name = "fechamento"


urlpatterns = [
    path(
        "eventos/<int:evento_id>/fechamento/",
        FechamentoInternoView.as_view(),
        name="fechamento",
    ),
]

