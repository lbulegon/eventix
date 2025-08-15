from django.urls import path
from app_eventos.views.views_freelance import CadastroBasicoFreelanceView, UploadDocumentosFreelanceView

urlpatterns = [
    path('freelance/cadastro-basico/', CadastroBasicoFreelanceView.as_view(), name='cadastro-basico-freelance'),
    path('freelance/upload-documentos/', UploadDocumentosFreelanceView.as_view(), name='upload-documentos-freelance'),
]