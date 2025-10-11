# app_eventos/signals.py
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Candidatura, ContratoFreelance, User, GrupoUsuario, ComissaoEventix, Vaga, Freelance, FreelancerFuncao
from .services.notificacoes_push import NotificacaoPushService

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
def adicionar_usuario_ao_grupo_correto(sender, instance, created, **kwargs):
    """
    Quando um usuário é criado ou seu tipo_usuario é alterado,
    adiciona automaticamente ao grupo correto baseado no tipo.
    """
    # Busca o grupo apropriado baseado no tipo de usuário
    grupo = None
    
    if instance.tipo_usuario == 'freelancer':
        # Grupo global de freelancers (sem empresa específica)
        grupo = GrupoUsuario.objects.filter(
            nome='Freelancers Global',
            empresa_contratante=None,
            ativo=True
        ).first()
        
    elif instance.tipo_usuario == 'admin_sistema':
        # Grupo de administrador do sistema
        grupo = GrupoUsuario.objects.filter(
            nome='Administrador do Sistema',
            empresa_contratante=None,
            ativo=True
        ).first()
        
    elif instance.tipo_usuario in ['admin_empresa', 'operador_empresa']:
        # Grupos específicos da empresa
        if instance.empresa_contratante:
            if instance.tipo_usuario == 'admin_empresa':
                grupo = GrupoUsuario.objects.filter(
                    nome='Administrador da Empresa',
                    empresa_contratante=instance.empresa_contratante,
                    ativo=True
                ).first()
            elif instance.tipo_usuario == 'operador_empresa':
                grupo = GrupoUsuario.objects.filter(
                    nome='Operador da Empresa',
                    empresa_contratante=instance.empresa_contratante,
                    ativo=True
                ).first()
    
    # Adiciona o usuário ao grupo se encontrado
    if grupo:
        instance.adicionar_ao_grupo(grupo, ativo=True)


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
    
    # Se o tipo mudou, remove de todos os grupos e deixa o post_save adicionar ao correto
    if usuario_antigo.tipo_usuario != instance.tipo_usuario:
        # Remove de todos os grupos ativos
        grupos_ativos = instance.get_grupos_ativos()
        for usuario_grupo in grupos_ativos:
            instance.remover_do_grupo(usuario_grupo.grupo)
        
        # Se mudou a empresa contratante, também remove dos grupos da empresa antiga
        if (usuario_antigo.empresa_contratante != instance.empresa_contratante and 
            usuario_antigo.empresa_contratante):
            
            # Remove de grupos da empresa antiga
            grupos_empresa_antiga = GrupoUsuario.objects.filter(
                empresa_contratante=usuario_antigo.empresa_contratante,
                ativo=True
            )
            for grupo in grupos_empresa_antiga:
                instance.remover_do_grupo(grupo)


@receiver(post_save, sender=ContratoFreelance)
def calcular_comissao_eventix(sender, instance, created, **kwargs):
    """
    Quando um ContratoFreelance é criado, calcula automaticamente a comissão do Eventix.
    """
    if created and instance.status == 'ativo':
        try:
            # Verifica se já existe comissão para evitar duplicação
            if not ComissaoEventix.objects.filter(contrato_freelance=instance).exists():
                # Obtém o percentual de comissão do plano da empresa
                empresa = instance.vaga.empresa_contratante
                percentual_comissao = empresa.plano_contratado.percentual_comissao if empresa.plano_contratado else 6.00
                
                # Cria a comissão
                ComissaoEventix.objects.create(
                    contrato_freelance=instance,
                    empresa_contratante=empresa,
                    valor_vaga_freelancer=instance.vaga.remuneracao,
                    percentual_comissao=percentual_comissao,
                    status='calculada'
                )
        except Exception as e:
            # Log do erro (em produção, usar logging adequado)
            print(f"Erro ao calcular comissão: {e}")


@receiver(pre_save, sender=ContratoFreelance)
def atualizar_comissao_ao_alterar_status(sender, instance, **kwargs):
    """
    Atualiza o status da comissão quando o status do contrato muda.
    """
    if not instance.pk:
        return
    
    try:
        contrato_antigo = ContratoFreelance.objects.get(pk=instance.pk)
    except ContratoFreelance.DoesNotExist:
        return
    
    # Se o status mudou, atualiza a comissão correspondente
    if contrato_antigo.status != instance.status:
        try:
            comissao = ComissaoEventix.objects.get(contrato_freelance=instance)
            
            # Mapeia status do contrato para status da comissão
            if instance.status == 'finalizado':
                comissao.status = 'cobrada'
            elif instance.status == 'cancelado':
                comissao.status = 'cancelada'
            elif instance.status == 'ativo':
                comissao.status = 'calculada'
            
            comissao.save()
        except ComissaoEventix.DoesNotExist:
            pass  # Comissão não existe ainda


@receiver(post_save, sender=Vaga)
def notificar_freelancers_vaga_criada(sender, instance, created, **kwargs):
    """
    Quando uma vaga é criada, notifica todos os freelancers que têm a função cadastrada.
    """
    # Só notifica quando a vaga é criada (não em updates)
    if not created:
        return
    
    # Só notifica se a vaga está ativa
    if not instance.ativa:
        return
    
    # Só notifica se a vaga tem uma função associada
    if not instance.funcao:
        return
    
    try:
        # Buscar freelancers que têm essa função cadastrada
        freelancers_funcao = FreelancerFuncao.objects.filter(
            funcao=instance.funcao,
            ativo=True
        ).select_related('freelancer')
        
        # Filtrar apenas freelancers com:
        # 1. Cadastro completo
        # 2. Notificações ativas
        # 3. Device token configurado
        freelancers_notificar = []
        device_tokens = []
        
        for ff in freelancers_funcao:
            freelancer = ff.freelancer
            if (freelancer.cadastro_completo and 
                freelancer.notificacoes_ativas and 
                freelancer.device_token):
                freelancers_notificar.append(freelancer)
                device_tokens.append(freelancer.device_token)
        
        if not device_tokens:
            print(f"ℹ Nenhum freelancer com notificações ativas para a vaga: {instance.titulo}")
            return
        
        # Enviar notificações push
        servico_push = NotificacaoPushService()
        enviados = servico_push.enviar_notificacao_multipla(device_tokens, instance)
        
        print(f"✓ Notificações enviadas: {enviados}/{len(device_tokens)} freelancers para vaga: {instance.titulo}")
        
    except Exception as e:
        # Em produção, usar logging adequado
        print(f"✗ Erro ao notificar freelancers sobre vaga: {str(e)}")

