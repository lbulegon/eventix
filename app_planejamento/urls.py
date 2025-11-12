from django.urls import path

from .views import InsightEventoView


app_name = "planejamento"


urlpatterns = [
    path(
        "eventos/<int:evento_id>/planejamento/insights",
        InsightEventoView.as_view(),
        name="planejamento_insights",
    ),
]

