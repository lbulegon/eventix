"""
URLs para dashboard de documentos do freelancer
"""
from django.urls import path
from app_eventos.views.views_documentos_freelancer import (
    dashboard_documentos_freelancer,
    upload_documento_freelancer,
    documentos_empresa_freelancer,
    excluir_documento_freelancer,
)

app_name = 'freelancer_documentos'

urlpatterns = [
    # Dashboard principal
    path('', dashboard_documentos_freelancer, name='dashboard'),
    
    # Documentos por empresa
    path('empresa/<int:empresa_id>/', documentos_empresa_freelancer, name='documentos_empresa'),
    path('empresa/<int:empresa_id>/upload/', upload_documento_freelancer, name='upload'),
    
    # Ações
    path('excluir/<int:documento_id>/', excluir_documento_freelancer, name='excluir'),
]

