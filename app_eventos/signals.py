"""
Signals Django para notificações automáticas
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
import logging

from .models import Vaga
from .services.notificacao_vagas import NotificacaoVagasService

logger = logging.getLogger(__name__)


# Signal automático removido - agora usa botão manual
# @receiver(post_save, sender=Vaga)
# def notificar_freelancers_nova_vaga(sender, instance, created, **kwargs):
#     """
#     Signal que dispara quando uma nova vaga é criada
#     REMOVIDO: Agora usa botão manual no evento
#     """