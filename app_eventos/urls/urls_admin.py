from django.urls import path
from app_eventos.views.views_web import (
    web_dashboard, web_empresa_dashboard, web_freelancer_dashboard, web_admin_dashboard,
    web_eventos_list, web_evento_detail, web_equipamentos_list, web_equipamento_detail,
    web_vagas_list, web_vaga_detail, web_candidaturas_list, web_financeiro_dashboard
)

urlpatterns = [
    # Dashboard principal
    path('', web_dashboard, name='admin_dashboard'),
    
    # Dashboards por tipo de usuário
    path('empresa/', web_empresa_dashboard, name='admin_empresa_dashboard'),
    path('freelancer/', web_freelancer_dashboard, name='admin_freelancer_dashboard'),
    path('admin-sistema/', web_admin_dashboard, name='admin_admin_dashboard'),
    
    # Eventos
    path('eventos/', web_eventos_list, name='admin_eventos_list'),
    path('eventos/<int:evento_id>/', web_evento_detail, name='admin_evento_detail'),
    
    # Equipamentos
    path('equipamentos/', web_equipamentos_list, name='admin_equipamentos_list'),
    path('equipamentos/<int:equipamento_id>/', web_equipamento_detail, name='admin_equipamento_detail'),
    
    # Vagas
    path('vagas/', web_vagas_list, name='admin_vagas_list'),
    path('vagas/<int:vaga_id>/', web_vaga_detail, name='admin_vaga_detail'),
    
    # Candidaturas
    path('candidaturas/', web_candidaturas_list, name='admin_candidaturas_list'),
    
    # Financeiro
    path('financeiro/', web_financeiro_dashboard, name='admin_financeiro_dashboard'),
]
