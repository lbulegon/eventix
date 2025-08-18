# app_eventos/signals.py
from django.db.models.signals import pre_save, post_save
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

@receiver(pre_save, sender=Candidatura)
def _candidatura_aprovada_cria_contrato(sender, instance: Candidatura, **kwargs):
    if not instance.pk:
        return
    try:
        antigo = Candidatura.objects.get(pk=instance.pk)
    except Candidatura.DoesNotExist:
        return
    # mudou de pendente/rejeitado para aprovado
    if antigo.status != "aprovado" and instance.status == "aprovado":
        ja_existe = ContratoFreelance.objects.filter(
            freelance=instance.freelance, vaga=instance.vaga, status="ativo"
        ).exists()
        if not ja_existe:
            ContratoFreelance.objects.create(
                freelance=instance.freelance, vaga=instance.vaga, status="ativo"
            )

