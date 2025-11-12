from django.urls import path

from .views import BriefingView


app_name = "briefing"


urlpatterns = [
    path("eventos/<int:evento_id>/briefing/", BriefingView.as_view(), name="evento_briefing"),
]
