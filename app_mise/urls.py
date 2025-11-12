from django.urls import path

from .views import MiseEnPlaceView


app_name = "mise"


urlpatterns = [
    path("eventos/<int:evento_id>/mise/", MiseEnPlaceView.as_view(), name="mise"),
]

