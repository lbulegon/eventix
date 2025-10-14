"""
URLs para Dashboard da Empresa
"""
from django.urls import path, include
from . import views_dashboard_empresa

app_name = 'dashboard_empresa'

urlpatterns = [
    # Autenticação
    path('login/', views_dashboard_empresa.login_empresa, name='login_empresa'),
    path('logout/', views_dashboard_empresa.logout_empresa, name='logout_empresa'),
    
    # Teste do dashboard
    path('test/', views_dashboard_empresa.test_dashboard, name='test_dashboard'),
    
    # Dashboard principal
    path('', views_dashboard_empresa.dashboard_empresa, name='dashboard_empresa'),
    
    # Módulos específicos
    path('eventos/', views_dashboard_empresa.eventos_empresa, name='eventos_empresa'),
    path('eventos/<int:evento_id>/', views_dashboard_empresa.detalhe_evento, name='detalhe_evento'),
    path('eventos/<int:evento_id>/criar-setor/', views_dashboard_empresa.criar_setor, name='criar_setor'),
    path('setores/<int:setor_id>/criar-vaga/', views_dashboard_empresa.criar_vaga, name='criar_vaga'),
    path('candidaturas/', views_dashboard_empresa.candidaturas_empresa, name='candidaturas_empresa'),
    path('candidaturas/<int:candidatura_id>/', views_dashboard_empresa.detalhe_candidatura, name='detalhe_candidatura'),
    path('candidaturas/<int:candidatura_id>/aprovar/', views_dashboard_empresa.aprovar_candidatura, name='aprovar_candidatura'),
    path('candidaturas/<int:candidatura_id>/rejeitar/', views_dashboard_empresa.rejeitar_candidatura, name='rejeitar_candidatura'),
    path('freelancers/', views_dashboard_empresa.freelancers_empresa, name='freelancers_empresa'),
    path('equipamentos/', views_dashboard_empresa.equipamentos_empresa, name='equipamentos_empresa'),
    path('financeiro/', views_dashboard_empresa.financeiro_empresa, name='financeiro_empresa'),
    path('usuarios/', views_dashboard_empresa.usuarios_empresa, name='usuarios_empresa'),
    
    # Sistema de Documentos
    path('documentos/', include('app_eventos.urls.urls_documentos_empresa')),
]
