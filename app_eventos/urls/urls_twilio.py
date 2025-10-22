"""
URLs para Sistema Twilio (WhatsApp + SMS)
"""
from django.urls import path
from app_eventos.views.views_twilio import (
    VerifyStartView,
    VerifyCheckView,
    BroadcastView,
    TwilioStatusWebhook,
    NotificarFreelancersVagaView
)

app_name = 'twilio'

urlpatterns = [
    # Verificação de telefone (OTP)
    path('verify/start/', VerifyStartView.as_view(), name='verify_start'),
    path('verify/check/', VerifyCheckView.as_view(), name='verify_check'),
    
    # Broadcast (envio em massa)
    path('broadcast/', BroadcastView.as_view(), name='broadcast'),
    
    # Notificações específicas
    path('notificar-vaga/', NotificarFreelancersVagaView.as_view(), name='notificar_vaga'),
    
    # Webhook do Twilio
    path('status/', TwilioStatusWebhook.as_view(), name='twilio_status_webhook'),
]

