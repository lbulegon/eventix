# app_eventos/signals.py
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Candidatura, ContratoFreelance, User, GrupoUsuario

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


@receiver(post_save, sender=User)
def adicionar_freelancer_ao_grupo(sender, instance, created, **kwargs):
    """
    Quando um usuário é criado ou seu tipo_usuario é alterado para 'freelancer',
    adiciona automaticamente ao grupo global de freelancers.
    """
    # Só processa se o usuário é freelancer
    if instance.tipo_usuario == 'freelancer':
        # Busca o grupo global de freelancers (sem empresa específica)
        grupo_freelancers = GrupoUsuario.objects.filter(
            nome='Freelancers Global',
            empresa_contratante=None,
            ativo=True
        ).first()
        
        if grupo_freelancers:
            # Adiciona o usuário ao grupo (ou reativa se já existir)
            instance.adicionar_ao_grupo(grupo_freelancers, ativo=True)


@receiver(pre_save, sender=User)
def verificar_mudanca_tipo_usuario(sender, instance, **kwargs):
    """
    Verifica se o tipo_usuario foi alterado e ajusta os grupos automaticamente.
    """
    if not instance.pk:
        return
    
    try:
        usuario_antigo = User.objects.get(pk=instance.pk)
    except User.DoesNotExist:
        return
    
    # Se mudou de freelancer para outro tipo, remove do grupo global de freelancers
    if (usuario_antigo.tipo_usuario == 'freelancer' and 
        instance.tipo_usuario != 'freelancer'):
        
        # Remove do grupo global de freelancers
        grupo_freelancers = GrupoUsuario.objects.filter(
            nome='Freelancers Global',
            empresa_contratante=None,
            ativo=True
        ).first()
        
        if grupo_freelancers:
            instance.remover_do_grupo(grupo_freelancers)
    
    # Se mudou para freelancer, adiciona ao grupo global
    elif (usuario_antigo.tipo_usuario != 'freelancer' and 
          instance.tipo_usuario == 'freelancer'):
        
        # Busca o grupo global de freelancers
        grupo_freelancers = GrupoUsuario.objects.filter(
            nome='Freelancers Global',
            empresa_contratante=None,
            ativo=True
        ).first()
        
        if grupo_freelancers:
            instance.adicionar_ao_grupo(grupo_freelancers, ativo=True)

