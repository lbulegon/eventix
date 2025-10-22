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
    path('eventos/criar/', views_dashboard_empresa.criar_evento, name='criar_evento'),
    path('eventos/<int:evento_id>/', views_dashboard_empresa.detalhe_evento, name='detalhe_evento'),
    path('eventos/<int:evento_id>/editar/', views_dashboard_empresa.editar_evento, name='editar_evento'),
    path('eventos/<int:evento_id>/vagas/', views_dashboard_empresa.gerenciar_vagas_evento, name='gerenciar_vagas_evento'),
    path('eventos/<int:evento_id>/criar-setor/', views_dashboard_empresa.criar_setor, name='criar_setor'),
    path('eventos/<int:evento_id>/criar-vaga-generica/', views_dashboard_empresa.criar_vaga_generica, name='criar_vaga_generica'),
    path('setores/<int:setor_id>/criar-vaga/', views_dashboard_empresa.criar_vaga, name='criar_vaga'),
    path('vagas/<int:vaga_id>/editar/', views_dashboard_empresa.editar_vaga, name='editar_vaga'),
    path('vagas/<int:vaga_id>/desativar/', views_dashboard_empresa.desativar_vaga, name='desativar_vaga'),
    path('vagas/<int:vaga_id>/atrelar-setor/', views_dashboard_empresa.atrelar_vaga_setor, name='atrelar_vaga_setor'),
    path('vagas/<int:vaga_id>/desatrelar-setor/', views_dashboard_empresa.desatrelar_vaga_setor, name='desatrelar_vaga_setor'),
    path('candidaturas/', views_dashboard_empresa.candidaturas_empresa, name='candidaturas_empresa'),
    path('candidaturas/<int:candidatura_id>/', views_dashboard_empresa.detalhe_candidatura, name='detalhe_candidatura'),
    path('candidaturas/<int:candidatura_id>/aprovar/', views_dashboard_empresa.aprovar_candidatura, name='aprovar_candidatura'),
    path('candidaturas/<int:candidatura_id>/rejeitar/', views_dashboard_empresa.rejeitar_candidatura, name='rejeitar_candidatura'),
    path('freelancers/', views_dashboard_empresa.freelancers_empresa, name='freelancers_empresa'),
    path('freelancers/<int:freelancer_id>/', views_dashboard_empresa.detalhe_freelancer, name='detalhe_freelancer'),
    path('equipamentos/', views_dashboard_empresa.equipamentos_empresa, name='equipamentos_empresa'),
    
    # Notificações
    path('eventos/<int:evento_id>/notificar-freelancers/', NotificarFreelancersEventoView.as_view(), name='notificar_freelancers_evento'),
    path('notificar-vaga/<int:vaga_id>/', notificar_freelancers_vaga_especifica, name='notificar_freelancers_vaga'),
    path('financeiro/', views_dashboard_empresa.financeiro_empresa, name='financeiro_empresa'),
    path('usuarios/', views_dashboard_empresa.usuarios_empresa, name='usuarios_empresa'),
    
    # Sistema de Documentos
    path('documentos/', include('app_eventos.urls.urls_documentos_empresa')),
]
