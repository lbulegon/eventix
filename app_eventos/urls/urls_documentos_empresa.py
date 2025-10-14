"""
URLs para dashboard de documentos da empresa
"""
from django.urls import path
from app_eventos.views.views_documentos_empresa import (
    dashboard_documentos_empresa,
    documentos_pendentes_empresa,
    validar_documento_empresa,
    configurar_documentos_empresa,
    documentos_freelancer_empresa,
    aprovar_documento_ajax,
    rejeitar_documento_ajax,
)

app_name = 'empresa_documentos'

urlpatterns = [
    # Dashboard principal
    path('', dashboard_documentos_empresa, name='dashboard'),
    
    # Validação
    path('pendentes/', documentos_pendentes_empresa, name='pendentes'),
    path('validar/<int:documento_id>/', validar_documento_empresa, name='validar'),
    
    # Configuração
    path('configurar/', configurar_documentos_empresa, name='configurar'),
    
    # Freelancer específico
    path('freelancer/<int:freelancer_id>/', documentos_freelancer_empresa, name='freelancer'),
    
    # AJAX
    path('ajax/aprovar/<int:documento_id>/', aprovar_documento_ajax, name='aprovar_ajax'),
    path('ajax/rejeitar/<int:documento_id>/', rejeitar_documento_ajax, name='rejeitar_ajax'),
]

