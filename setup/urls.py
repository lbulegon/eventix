from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from app_eventos import views  
from app_eventos.views.views_equipamentos_web import equipamentos_setor
from app_eventos.views.views_dashboard import (
    dashboard_redirect, dashboard_empresa, 
    dashboard_freelancer, dashboard_admin_sistema, fluxo_caixa_evento, fornecedores_list
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    
    # Sistema de autenticação única
    path("api/auth/", include("api_v01.urls.urls")),
    
    # Dashboards
    path("dashboard/", dashboard_redirect, name="dashboard_redirect"),
    path("empresa/dashboard/", dashboard_empresa, name="dashboard_empresa"),
    path("freelancer/dashboard/", dashboard_freelancer, name="dashboard_freelancer"),
    path("admin-sistema/dashboard/", dashboard_admin_sistema, name="dashboard_admin_sistema"),
    
    # Fluxo de Caixa
    path("eventos/<int:evento_id>/fluxo-caixa/", fluxo_caixa_evento, name="fluxo_caixa_evento"),
    
    # Fornecedores
    path("fornecedores/", fornecedores_list, name="fornecedores_list"),
    
    # APIs existentes
    path("api/equipamentos/", include("app_eventos.urls.urls_equipamentos")),
    path("setor/<int:setor_id>/equipamentos/", equipamentos_setor, name="equipamentos_setor"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


