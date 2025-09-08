# app_eventos/signals_notificacoes.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

from .models import Candidatura, Vaga, Evento, ContratoFreelance
from .models_notificacoes import Notificacao, ConfiguracaoNotificacao


@receiver(post_save, sender=Candidatura)
def notificar_nova_candidatura(sender, instance, created, **kwargs):
    """
    Notifica empresa sobre nova candidatura
    """
    if created:
        # Buscar usuários da empresa que podem receber notificações
        empresa_contratante = instance.vaga.setor.evento.empresa_contratante
        usuarios_empresa = empresa_contratante.usuarios.filter(
            is_active=True,
            tipo_usuario__in=['admin_empresa', 'operador_empresa']
        )
        
        for usuario in usuarios_empresa:
            # Verificar configurações de notificação
            config, _ = ConfiguracaoNotificacao.objects.get_or_create(usuario=usuario)
            
            if config.email_nova_candidatura:
                # Criar notificação
                Notificacao.criar_notificacao(
                    usuario=usuario,
                    tipo='nova_candidatura',
                    titulo='Nova Candidatura Recebida',
                    mensagem=f'Você recebeu uma nova candidatura para a vaga "{instance.vaga.titulo}" de {instance.freelance.nome_completo}.',
                    candidatura=instance,
                    vaga=instance.vaga,
                    prioridade='media'
                )
                
                # Enviar email
                try:
                    send_mail(
                        subject=f'Nova Candidatura - {instance.vaga.titulo}',
                        message=f'Você recebeu uma nova candidatura para a vaga "{instance.vaga.titulo}" de {instance.freelance.nome_completo}.',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[usuario.email],
                        fail_silently=True
                    )
                except Exception as e:
                    print(f"Erro ao enviar email: {e}")


@receiver(pre_save, sender=Candidatura)
def notificar_mudanca_status_candidatura(sender, instance, **kwargs):
    """
    Notifica freelancer sobre mudança de status da candidatura
    """
    if instance.pk:  # Só para atualizações, não criações
        try:
            candidatura_anterior = Candidatura.objects.get(pk=instance.pk)
            
            # Verificar se o status mudou
            if candidatura_anterior.status != instance.status:
                config, _ = ConfiguracaoNotificacao.objects.get_or_create(
                    usuario=instance.freelance.usuario
                )
                
                if instance.status == 'aprovado':
                    if config.email_candidatura_aprovada:
                        Notificacao.criar_notificacao(
                            usuario=instance.freelance.usuario,
                            tipo='candidatura_aprovada',
                            titulo='Candidatura Aprovada!',
                            mensagem=f'Parabéns! Sua candidatura para a vaga "{instance.vaga.titulo}" foi aprovada.',
                            candidatura=instance,
                            vaga=instance.vaga,
                            prioridade='alta'
                        )
                        
                        # Enviar email
                        try:
                            send_mail(
                                subject=f'Candidatura Aprovada - {instance.vaga.titulo}',
                                message=f'Parabéns! Sua candidatura para a vaga "{instance.vaga.titulo}" foi aprovada.',
                                from_email=settings.DEFAULT_FROM_EMAIL,
                                recipient_list=[instance.freelance.usuario.email],
                                fail_silently=True
                            )
                        except Exception as e:
                            print(f"Erro ao enviar email: {e}")
                
                elif instance.status == 'rejeitado':
                    if config.email_candidatura_rejeitada:
                        Notificacao.criar_notificacao(
                            usuario=instance.freelance.usuario,
                            tipo='candidatura_rejeitada',
                            titulo='Candidatura Não Aprovada',
                            mensagem=f'Sua candidatura para a vaga "{instance.vaga.titulo}" não foi aprovada desta vez.',
                            candidatura=instance,
                            vaga=instance.vaga,
                            prioridade='media'
                        )
                        
                        # Enviar email
                        try:
                            send_mail(
                                subject=f'Candidatura Não Aprovada - {instance.vaga.titulo}',
                                message=f'Sua candidatura para a vaga "{instance.vaga.titulo}" não foi aprovada desta vez.',
                                from_email=settings.DEFAULT_FROM_EMAIL,
                                recipient_list=[instance.freelance.usuario.email],
                                fail_silently=True
                            )
                        except Exception as e:
                            print(f"Erro ao enviar email: {e}")
        
        except Candidatura.DoesNotExist:
            pass


@receiver(post_save, sender=Vaga)
def notificar_vaga_publicada(sender, instance, created, **kwargs):
    """
    Notifica freelancers sobre nova vaga publicada
    """
    if not created and instance.publicada:
        # Buscar freelancers que podem se interessar pela vaga
        freelancers_interessados = instance._get_freelancers_interessados()
        
        for freelancer in freelancers_interessados:
            config, _ = ConfiguracaoNotificacao.objects.get_or_create(
                usuario=freelancer.usuario
            )
            
            if config.email_vaga_publicada:
                Notificacao.criar_notificacao(
                    usuario=freelancer.usuario,
                    tipo='vaga_publicada',
                    titulo='Nova Vaga Disponível',
                    mensagem=f'Uma nova vaga foi publicada: "{instance.titulo}" em {instance.setor.evento.nome}.',
                    vaga=instance,
                    evento=instance.setor.evento,
                    prioridade='media'
                )


@receiver(post_save, sender=ContratoFreelance)
def notificar_contrato_criado(sender, instance, created, **kwargs):
    """
    Notifica freelancer sobre contrato criado
    """
    if created:
        config, _ = ConfiguracaoNotificacao.objects.get_or_create(
            usuario=instance.freelance.usuario
        )
        
        Notificacao.criar_notificacao(
            usuario=instance.freelance.usuario,
            tipo='contrato_criado',
            titulo='Contrato Criado',
            mensagem=f'Seu contrato para a vaga "{instance.vaga.titulo}" foi criado com sucesso.',
            vaga=instance.vaga,
            prioridade='alta'
        )


# Método auxiliar para o modelo Vaga
def _get_freelancers_interessados(self):
    """
    Retorna freelancers que podem se interessar por esta vaga
    """
    from .models import Freelance
    
    # Buscar freelancers por localização e função
    freelancers = Freelance.objects.filter(
        usuario__is_active=True,
        cadastro_completo=True
    )
    
    # Filtrar por localização se disponível
    if self.setor.evento.local and self.setor.evento.local.cidade:
        freelancers = freelancers.filter(
            cidade__icontains=self.setor.evento.local.cidade
        )
    
    # Filtrar por função se disponível
    if self.funcao:
        # TODO: Implementar matching de habilidades
        pass
    
    return freelancers[:50]  # Limitar a 50 freelancers


# Adicionar método ao modelo Vaga
Vaga._get_freelancers_interessados = _get_freelancers_interessados
