"""
URLs para modelos globais do sistema
"""
from django.urls import path
from . import views_globais

app_name = 'globais'

urlpatterns = [
    # Dashboard Global
    path('dashboard/', views_globais.dashboard_global, name='dashboard_global'),
    
    # Catálogos Gerais
    path('categorias/', views_globais.CategoriaGlobalListView.as_view(), name='categorias_list'),
    path('categorias/<int:pk>/', views_globais.CategoriaGlobalDetailView.as_view(), name='categoria_detail'),
    
    path('tipos/', views_globais.TipoGlobalListView.as_view(), name='tipos_list'),
    
    path('classificacoes/', views_globais.ClassificacaoGlobalListView.as_view(), name='classificacoes_list'),
    
    # Configurações Sistema
    path('configuracoes/', views_globais.ConfiguracaoSistemaListView.as_view(), name='configuracoes_list'),
    path('parametros/', views_globais.ParametroSistemaListView.as_view(), name='parametros_list'),
    
    # Integrações
    path('integracoes/', views_globais.IntegracaoGlobalListView.as_view(), name='integracoes_list'),
    path('integracoes/<int:pk>/', views_globais.IntegracaoGlobalDetailView.as_view(), name='integracao_detail'),
    
    # Templates
    path('templates/', views_globais.TemplateGlobalListView.as_view(), name='templates_list'),
    path('templates/<int:pk>/', views_globais.TemplateGlobalDetailView.as_view(), name='template_detail'),
    
    # Marketplace
    path('categorias-freelancer/', views_globais.CategoriaFreelancerGlobalListView.as_view(), name='categorias_freelancer_list'),
    path('habilidades/', views_globais.HabilidadeGlobalListView.as_view(), name='habilidades_list'),
    path('fornecedores/', views_globais.FornecedorGlobalListView.as_view(), name='fornecedores_list'),
    path('fornecedores/<int:pk>/', views_globais.FornecedorGlobalDetailView.as_view(), name='fornecedor_detail'),
]
