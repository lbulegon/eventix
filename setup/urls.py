from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from app_eventos import views  
from app_eventos.views.views_equipamentos_web import equipamentos_setor


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("api/equipamentos/", include("app_eventos.urls.urls_equipamentos")),
    path("setor/<int:setor_id>/equipamentos/", equipamentos_setor, name="equipamentos_setor"),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)