"""
URLs para Dashboard da Empresa
"""
from django.urls import path
from . import views_dashboard_empresa

app_name = 'dashboard_empresa'

urlpatterns = [
    # Teste do dashboard
    path('test/', views_dashboard_empresa.test_dashboard, name='test_dashboard'),
    
    # Dashboard principal
    path('', views_dashboard_empresa.dashboard_empresa, name='dashboard_empresa'),
    
    # Módulos específicos
    path('eventos/', views_dashboard_empresa.eventos_empresa, name='eventos_empresa'),
    path('candidaturas/', views_dashboard_empresa.candidaturas_empresa, name='candidaturas_empresa'),
    path('freelancers/', views_dashboard_empresa.freelancers_empresa, name='freelancers_empresa'),
    path('equipamentos/', views_dashboard_empresa.equipamentos_empresa, name='equipamentos_empresa'),
    path('financeiro/', views_dashboard_empresa.financeiro_empresa, name='financeiro_empresa'),
    path('usuarios/', views_dashboard_empresa.usuarios_empresa, name='usuarios_empresa'),
]
