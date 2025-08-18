# api_v01/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from ..views.views import (
    login_unico, registro_freelancer, registro_empresa,
    perfil_usuario, logout, verificar_tipo_usuario, registro_unico, listar_empresas
)

app_name = 'api_v01'

urlpatterns = [
    # Autenticação única
    path('login/', login_unico, name='login_unico'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', logout, name='logout'),
    
    # Registro
    path('registro/', registro_unico, name='registro_unico'),
    path('registro/freelancer/', registro_freelancer, name='registro_freelancer'),
    path('registro/empresa/', registro_empresa, name='registro_empresa'),
    
    # Empresas
    path('empresas/', listar_empresas, name='listar_empresas'),
    
    # Perfil e informações do usuário
    path('perfil/', perfil_usuario, name='perfil_usuario'),
    path('tipo-usuario/', verificar_tipo_usuario, name='verificar_tipo_usuario'),
]
