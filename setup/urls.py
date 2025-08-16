from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from app_eventos import views  


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)