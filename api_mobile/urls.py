# api_mobile/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VagaViewSet, CandidaturaViewSet, EventoViewSet, FreelanceViewSet,
    EmpresaViewSet, EmpresaContratanteViewSet, UserProfileView, EmpresaDataView,
    TokenVerifyView, PasswordResetView, PasswordResetConfirmView,
    CustomTokenObtainPairView, CustomTokenRefreshView,
    RegistrarDeviceTokenView, DesativarNotificacoesView
)
from .views_funcoes import FuncaoViewSet, FreelancerFuncaoViewSet
from .views_avancadas import VagaAvancadaViewSet, CandidaturaAvancadaViewSet

router = DefaultRouter()
router.register(r'vagas', VagaViewSet, basename='vaga')
router.register(r'vagas-avancadas', VagaAvancadaViewSet, basename='vaga-avancada')
router.register(r'candidaturas', CandidaturaViewSet, basename='candidatura')
router.register(r'candidaturas-avancadas', CandidaturaAvancadaViewSet, basename='candidatura-avancada')
router.register(r'eventos', EventoViewSet, basename='evento')
router.register(r'freelancers', FreelanceViewSet, basename='freelancer')
router.register(r'empresas', EmpresaViewSet, basename='empresa')
router.register(r'empresas-contratantes', EmpresaContratanteViewSet, basename='empresa-contratante')
router.register(r'funcoes', FuncaoViewSet, basename='funcao')
router.register(r'freelancers/funcoes', FreelancerFuncaoViewSet, basename='freelancer-funcao')

urlpatterns = [
    # URLs do router
    path('', include(router.urls)),
    
    # URLs de autenticação
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('auth/refresh/', CustomTokenRefreshView.as_view(), name='token-refresh'),
    path('auth/logout/', TokenVerifyView.as_view(), name='token-logout'),
    
    # URLs específicas
    path('users/profile/', UserProfileView.as_view(), name='user-profile'),
    path('users/empresa-data/', EmpresaDataView.as_view(), name='empresa-data'),
    path('token/verify/', TokenVerifyView.as_view(), name='token-verify'),
    path('password/password-reset/', PasswordResetView.as_view(), name='password-reset'),
    path('password/password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    
    # Notificações Push
    path('notificacoes/registrar-token/', RegistrarDeviceTokenView.as_view(), name='registrar-device-token'),
    path('notificacoes/desativar/', DesativarNotificacoesView.as_view(), name='desativar-notificacoes'),
]
