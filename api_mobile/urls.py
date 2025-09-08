# api_mobile/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VagaViewSet, CandidaturaViewSet, EventoViewSet, FreelanceViewSet,
    EmpresaViewSet, EmpresaContratanteViewSet, UserProfileView,
    TokenVerifyView, PasswordResetView, PasswordResetConfirmView
)
from .views_funcoes import FuncaoViewSet, FreelancerFuncaoViewSet

router = DefaultRouter()
router.register(r'vagas', VagaViewSet, basename='vaga')
router.register(r'candidaturas', CandidaturaViewSet, basename='candidatura')
router.register(r'eventos', EventoViewSet, basename='evento')
router.register(r'freelancers', FreelanceViewSet, basename='freelancer')
router.register(r'empresas', EmpresaViewSet, basename='empresa')
router.register(r'empresas-contratantes', EmpresaContratanteViewSet, basename='empresa-contratante')
router.register(r'funcoes', FuncaoViewSet, basename='funcao')
router.register(r'freelancers/funcoes', FreelancerFuncaoViewSet, basename='freelancer-funcao')

urlpatterns = [
    # URLs do router
    path('', include(router.urls)),
    
    # URLs específicas
    path('users/profile/', UserProfileView.as_view(), name='user-profile'),
    path('token/verify/', TokenVerifyView.as_view(), name='token-verify'),
    path('password/password-reset/', PasswordResetView.as_view(), name='password-reset'),
    path('password/password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
]
