# app_eventos/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Candidatura, ContratoFreelance

@receiver(post_save, sender=Candidatura)
def criar_contrato_ao_aprovar(sender, instance, created, **kwargs):
    """
    Quando a candidatura for aprovada, cria automaticamente um ContratoFreelance.
    """
    # Só cria contrato se status = aprovado
    if instance.status == "aprovado":
        # Verifica se já existe contrato para evitar duplicação
        contrato, criado = ContratoFreelance.objects.get_or_create(
            freelance=instance.freelance,
            vaga=instance.vaga,
            defaults={"status": "ativo"},
        )
        # Se já existia mas estava cancelado/finalizado, pode reativar (opcional)
        if not criado and contrato.status != "ativo":
            contrato.status = "ativo"
            contrato.save()
