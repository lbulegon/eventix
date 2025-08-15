from django.urls import path
from app_eventos.views.views_freelance import UploadDocumentosFreelanceView

urlpatterns = [
    path(
        'freelance/upload-documentos/',
        UploadDocumentosFreelanceView.as_view(),
        name='upload-documentos-freelance'
    ),
]
