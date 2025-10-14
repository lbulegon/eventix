"""
URLs para sistema de documentos - API REST
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from app_eventos.views.views_api_documentos import (
    DocumentoFreelancerViewSet,
    VerificarDocumentosView,
    ConfiguracaoDocumentosViewSet,
    ReutilizacaoDocumentoViewSet
)

router = DefaultRouter()
router.register(r'documentos', DocumentoFreelancerViewSet, basename='documento')
router.register(r'configuracoes', ConfiguracaoDocumentosViewSet, basename='configuracao-documentos')
router.register(r'reutilizacoes', ReutilizacaoDocumentoViewSet, basename='reutilizacao')

app_name = 'documentos_api'

urlpatterns = [
    # API REST
    path('', include(router.urls)),
    
    # Endpoint de verificação
    path('verificar/', VerificarDocumentosView.as_view(), name='verificar-documentos'),
]

