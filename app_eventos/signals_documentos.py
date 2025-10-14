"""
Signals para sistema de documentos
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta

from .models_documentos import DocumentoFreelancerEmpresa
from .models_notificacoes import Notificacao


@receiver(post_save, sender=DocumentoFreelancerEmpresa)
def notificar_documento_enviado(sender, instance, created, **kwargs):
    """
    Notifica a empresa quando um freelancer envia um documento
    """
    if created:
        # Notificar empresa
        from .models import User
        usuarios_empresa = User.objects.filter(
            empresa_contratante=instance.empresa_contratante,
            tipo_usuario__in=['admin_empresa', 'operador_empresa']
        )
        
        for usuario in usuarios_empresa:
            Notificacao.objects.create(
                tipo='nova_candidatura',  # Usar tipo existente
                usuario=usuario,
                titulo='Novo Documento Enviado',
                mensagem=f'{instance.freelancer.usuario.get_full_name()} enviou {instance.get_tipo_documento_display()}',
                prioridade='media'
            )


@receiver(post_save, sender=DocumentoFreelancerEmpresa)
def notificar_documento_validado(sender, instance, created, update_fields, **kwargs):
    """
    Notifica o freelancer quando um documento é aprovado ou rejeitado
    """
    if not created and instance.status in ['aprovado', 'rejeitado']:
        # Verificar se o status mudou
        if update_fields and 'status' in update_fields:
            return  # Evitar duplicação
        
        # Notificar freelancer
        tipo_notif = 'candidatura_aprovada' if instance.status == 'aprovado' else 'candidatura_rejeitada'
        prioridade = 'media' if instance.status == 'aprovado' else 'alta'
        
        titulo = 'Documento Aprovado!' if instance.status == 'aprovado' else 'Documento Rejeitado'
        mensagem = f'Seu {instance.get_tipo_documento_display()} foi {instance.get_status_display().lower()} pela empresa {instance.empresa_contratante.nome_fantasia}'
        
        if instance.observacoes:
            mensagem += f'\n\nObservações: {instance.observacoes}'
        
        Notificacao.objects.create(
            tipo=tipo_notif,
            usuario=instance.freelancer.usuario,
            titulo=titulo,
            mensagem=mensagem,
            prioridade=prioridade
        )


def verificar_documentos_proximos_vencimento():
    """
    Verifica documentos que estão próximos ao vencimento (30, 15 e 7 dias)
    Chamado por comando de gerenciamento
    """
    from datetime import date
    
    # Datas de referência
    hoje = timezone.now().date()
    data_30_dias = hoje + timedelta(days=30)
    data_15_dias = hoje + timedelta(days=15)
    data_7_dias = hoje + timedelta(days=7)
    
    # Buscar documentos próximos ao vencimento
    documentos_30_dias = DocumentoFreelancerEmpresa.objects.filter(
        status='aprovado',
        data_vencimento__date=data_30_dias
    ).select_related('freelancer__usuario', 'empresa_contratante')
    
    documentos_15_dias = DocumentoFreelancerEmpresa.objects.filter(
        status='aprovado',
        data_vencimento__date=data_15_dias
    ).select_related('freelancer__usuario', 'empresa_contratante')
    
    documentos_7_dias = DocumentoFreelancerEmpresa.objects.filter(
        status='aprovado',
        data_vencimento__date=data_7_dias
    ).select_related('freelancer__usuario', 'empresa_contratante')
    
    # Notificar para cada grupo
    notificacoes_criadas = 0
    
    for documento in documentos_30_dias:
        # Verificar se já foi notificado
        if not Notificacao.objects.filter(
            usuario=documento.freelancer.usuario,
            mensagem__contains=str(documento.id)
        ).exists():
            Notificacao.objects.create(
                tipo='lembrete_candidatura',
                usuario=documento.freelancer.usuario,
                titulo='Documento vence em 30 dias',
                mensagem=f'Seu {documento.get_tipo_documento_display()} para {documento.empresa_contratante.nome_fantasia} vence em 30 dias. Doc ID: {documento.id}',
                prioridade='media'
            )
            notificacoes_criadas += 1
    
    for documento in documentos_15_dias:
        if not Notificacao.objects.filter(
            usuario=documento.freelancer.usuario,
            mensagem__contains=str(documento.id)
        ).exists():
            Notificacao.objects.create(
                tipo='lembrete_candidatura',
                usuario=documento.freelancer.usuario,
                titulo='⚠️ Documento vence em 15 dias',
                mensagem=f'Seu {documento.get_tipo_documento_display()} para {documento.empresa_contratante.nome_fantasia} vence em 15 dias. Doc ID: {documento.id}',
                prioridade='media'
            )
            notificacoes_criadas += 1
    
    for documento in documentos_7_dias:
        if not Notificacao.objects.filter(
            usuario=documento.freelancer.usuario,
            mensagem__contains=str(documento.id)
        ).exists():
            Notificacao.objects.create(
                tipo='lembrete_candidatura',
                usuario=documento.freelancer.usuario,
                titulo='🚨 URGENTE: Documento vence em 7 dias',
                mensagem=f'Seu {documento.get_tipo_documento_display()} para {documento.empresa_contratante.nome_fantasia} vence em 7 dias! Doc ID: {documento.id}',
                prioridade='alta'
            )
            notificacoes_criadas += 1
    
    return notificacoes_criadas


def marcar_documentos_expirados():
    """
    Marca documentos como expirados quando passam da data de vencimento
    Chamado por comando de gerenciamento
    """
    from datetime import date
    
    hoje = timezone.now()
    
    # Buscar documentos aprovados que passaram da data de vencimento
    documentos_expirados = DocumentoFreelancerEmpresa.objects.filter(
        status='aprovado',
        data_vencimento__lt=hoje
    )
    
    total = documentos_expirados.count()
    documentos_expirados.update(status='expirado')
    
    # Notificar freelancers
    for documento in documentos_expirados:
        Notificacao.objects.create(
            tipo='vaga_encerrada',  # Usar tipo existente
            usuario=documento.freelancer.usuario,
            titulo='Documento Expirado',
            mensagem=f'Seu {documento.get_tipo_documento_display()} para {documento.empresa_contratante.nome_fantasia} expirou. Por favor, envie um novo documento.',
            prioridade='alta'
        )
    
    return total

