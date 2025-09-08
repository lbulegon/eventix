# api_desktop/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router para APIs do desktop
router = DefaultRouter()
router.register(r'usuarios', views.UsuarioDesktopViewSet, basename='usuario-desktop')
router.register(r'empresas', views.EmpresaDesktopViewSet, basename='empresa-desktop')
router.register(r'eventos', views.EventoDesktopViewSet, basename='evento-desktop')
router.register(r'freelancers', views.FreelancerDesktopViewSet, basename='freelancer-desktop')
router.register(r'vagas', views.VagaDesktopViewSet, basename='vaga-desktop')
router.register(r'equipamentos', views.EquipamentoDesktopViewSet, basename='equipamento-desktop')
router.register(r'relatorios', views.RelatorioDesktopViewSet, basename='relatorio-desktop')

app_name = 'api_desktop'

urlpatterns = [
    # APIs do router
    path('', include(router.urls)),
    
    # APIs específicas do desktop
    path('dashboard/', views.DashboardDesktopView.as_view(), name='dashboard-desktop'),
    path('estatisticas/', views.EstatisticasDesktopView.as_view(), name='estatisticas-desktop'),
    path('exportar-dados/', views.ExportarDadosView.as_view(), name='exportar-dados'),
    path('configuracoes/', views.ConfiguracoesDesktopView.as_view(), name='configuracoes-desktop'),
    path('backup/', views.BackupDesktopView.as_view(), name='backup-desktop'),
    path('logs/', views.LogsDesktopView.as_view(), name='logs-desktop'),
    
    # APIs de autenticação específicas para desktop
    path('auth/login/', views.LoginDesktopView.as_view(), name='login-desktop'),
    path('auth/logout/', views.LogoutDesktopView.as_view(), name='logout-desktop'),
    path('auth/refresh/', views.RefreshTokenDesktopView.as_view(), name='refresh-desktop'),
    path('auth/verify/', views.VerifyTokenDesktopView.as_view(), name='verify-desktop'),
]
