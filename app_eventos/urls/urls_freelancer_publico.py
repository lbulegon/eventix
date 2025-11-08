from django.urls import path
from app_eventos import views_dashboard_freelancer_publico

app_name = 'freelancer_publico'

urlpatterns = [
    # Autenticação
    path('login/', views_dashboard_freelancer_publico.login_freelancer, name='login'),
    path('logout/', views_dashboard_freelancer_publico.logout_freelancer, name='logout'),
    path('app/', views_dashboard_freelancer_publico.freelancer_pwa, name='pwa'),
    
    # Dashboard
    path('dashboard/', views_dashboard_freelancer_publico.dashboard_freelancer, name='dashboard'),
    
    # Vagas
    path('vagas/', views_dashboard_freelancer_publico.vagas_disponiveis, name='vagas_disponiveis'),
    path('vagas/<int:vaga_id>/candidatar/', views_dashboard_freelancer_publico.candidatar_vaga, name='candidatar_vaga'),
    
    # Candidaturas
    path('candidaturas/', views_dashboard_freelancer_publico.minhas_candidaturas, name='minhas_candidaturas'),
    
    # Perfil
    path('perfil/', views_dashboard_freelancer_publico.perfil_freelancer, name='perfil'),
    
    # Páginas públicas (sem login)
    path('vaga/<int:vaga_id>/', views_dashboard_freelancer_publico.vaga_publica, name='vaga_publica'),
    path('evento/<int:evento_id>/', views_dashboard_freelancer_publico.evento_publico, name='evento_publico'),
]
