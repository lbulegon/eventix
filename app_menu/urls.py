from django.urls import path

from .views import FichaTecnicaListCreateView, MenuListCreateView, PratoListCreateView


app_name = "menu"


urlpatterns = [
    path("eventos/<int:evento_id>/menu/", MenuListCreateView.as_view(), name="menu_list_create"),
    path(
        "eventos/<int:evento_id>/menu/<int:menu_id>/pratos/",
        PratoListCreateView.as_view(),
        name="menu_pratos",
    ),
    path(
        "eventos/<int:evento_id>/menu/<int:menu_id>/pratos/<int:prato_id>/fichas/",
        FichaTecnicaListCreateView.as_view(),
        name="menu_fichas",
    ),
]

