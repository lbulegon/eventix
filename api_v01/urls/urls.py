# api_v01/urls.py
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from ..views.views import (
    login_unico, registro_freelancer, registro_empresa,
    perfil_usuario, logout, verificar_tipo_usuario, registro_unico, listar_empresas,
    # Views financeiras
    categorias_financeiras, despesas_evento, criar_despesa, atualizar_despesa,
    receitas_evento, criar_receita, atualizar_receita, fluxo_caixa_evento, fluxo_caixa_empresa,
    # Views fornecedores
    listar_fornecedores, detalhes_fornecedor, criar_fornecedor, atualizar_fornecedor, fornecedor_despesas
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
    
    # Sistema Financeiro
    path('categorias-financeiras/', categorias_financeiras, name='categorias_financeiras'),
    path('eventos/<int:evento_id>/despesas/', despesas_evento, name='despesas_evento'),
    path('despesas/', criar_despesa, name='criar_despesa'),
    path('despesas/<int:despesa_id>/', atualizar_despesa, name='atualizar_despesa'),
    path('eventos/<int:evento_id>/receitas/', receitas_evento, name='receitas_evento'),
    path('receitas/', criar_receita, name='criar_receita'),
    path('receitas/<int:receita_id>/', atualizar_receita, name='atualizar_receita'),
    path('eventos/<int:evento_id>/fluxo-caixa/', fluxo_caixa_evento, name='fluxo_caixa_evento'),
    path('fluxo-caixa-empresa/', fluxo_caixa_empresa, name='fluxo_caixa_empresa'),
    
    # Sistema de Fornecedores
    path('fornecedores/', listar_fornecedores, name='listar_fornecedores'),
    path('fornecedores/<int:fornecedor_id>/', detalhes_fornecedor, name='detalhes_fornecedor'),
    path('fornecedores/criar/', criar_fornecedor, name='criar_fornecedor'),
    path('fornecedores/<int:fornecedor_id>/atualizar/', atualizar_fornecedor, name='atualizar_fornecedor'),
    path('fornecedores/<int:fornecedor_id>/despesas/', fornecedor_despesas, name='fornecedor_despesas'),
    
    # Sistema de Documentos (API)
    path('', include('app_eventos.urls.urls_documentos')),
]
