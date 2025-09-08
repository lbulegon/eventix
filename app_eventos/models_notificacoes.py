# app_eventos/models_notificacoes.py
from django.db import models
from django.conf import settings
from django.utils import timezone


class Notificacao(models.Model):
    """
    Sistema de notificações para candidaturas e vagas
    """
    TIPO_CHOICES = [
        ('nova_candidatura', 'Nova Candidatura'),
        ('candidatura_aprovada', 'Candidatura Aprovada'),
        ('candidatura_rejeitada', 'Candidatura Rejeitada'),
        ('vaga_publicada', 'Vaga Publicada'),
        ('vaga_encerrada', 'Vaga Encerrada'),
        ('lembrete_candidatura', 'Lembrete de Candidatura'),
        ('evento_proximo', 'Evento Próximo'),
        ('contrato_criado', 'Contrato Criado'),
        ('avaliacao_solicitada', 'Avaliação Solicitada'),
    ]
    
    PRIORIDADE_CHOICES = [
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]
    
    # Destinatário
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notificacoes',
        verbose_name="Usuário"
    )
    
    # Tipo e conteúdo
    tipo = models.CharField(
        max_length=30,
        choices=TIPO_CHOICES,
        verbose_name="Tipo de Notificação"
    )
    titulo = models.CharField(max_length=200, verbose_name="Título")
    mensagem = models.TextField(verbose_name="Mensagem")
    prioridade = models.CharField(
        max_length=10,
        choices=PRIORIDADE_CHOICES,
        default='media',
        verbose_name="Prioridade"
    )
    
    # Relacionamentos opcionais
    candidatura = models.ForeignKey(
        'Candidatura',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notificacoes',
        verbose_name="Candidatura"
    )
    vaga = models.ForeignKey(
        'Vaga',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notificacoes',
        verbose_name="Vaga"
    )
    evento = models.ForeignKey(
        'Evento',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notificacoes_sistema',
        verbose_name="Evento"
    )
    
    # Status e controle
    lida = models.BooleanField(default=False, verbose_name="Lida")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_leitura = models.DateTimeField(null=True, blank=True, verbose_name="Data de Leitura")
    
    # Ações
    acao_url = models.URLField(blank=True, null=True, verbose_name="URL da Ação")
    acao_texto = models.CharField(max_length=100, blank=True, null=True, verbose_name="Texto da Ação")
    
    class Meta:
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"
        ordering = ['-data_criacao']
        indexes = [
            models.Index(fields=['usuario', 'lida']),
            models.Index(fields=['tipo', 'data_criacao']),
        ]
    
    def __str__(self):
        return f"{self.usuario.username} - {self.titulo}"
    
    def marcar_como_lida(self):
        """Marca a notificação como lida"""
        if not self.lida:
            self.lida = True
            self.data_leitura = timezone.now()
            self.save(update_fields=['lida', 'data_leitura'])
    
    @classmethod
    def criar_notificacao(cls, usuario, tipo, titulo, mensagem, **kwargs):
        """Método helper para criar notificações"""
        return cls.objects.create(
            usuario=usuario,
            tipo=tipo,
            titulo=titulo,
            mensagem=mensagem,
            **kwargs
        )


class ConfiguracaoNotificacao(models.Model):
    """
    Configurações de notificação por usuário
    """
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='configuracao_notificacao',
        verbose_name="Usuário"
    )
    
    # Configurações por tipo
    email_nova_candidatura = models.BooleanField(default=True, verbose_name="Email - Nova Candidatura")
    email_candidatura_aprovada = models.BooleanField(default=True, verbose_name="Email - Candidatura Aprovada")
    email_candidatura_rejeitada = models.BooleanField(default=True, verbose_name="Email - Candidatura Rejeitada")
    email_vaga_publicada = models.BooleanField(default=True, verbose_name="Email - Vaga Publicada")
    email_evento_proximo = models.BooleanField(default=True, verbose_name="Email - Evento Próximo")
    
    push_nova_candidatura = models.BooleanField(default=True, verbose_name="Push - Nova Candidatura")
    push_candidatura_aprovada = models.BooleanField(default=True, verbose_name="Push - Candidatura Aprovada")
    push_candidatura_rejeitada = models.BooleanField(default=True, verbose_name="Push - Candidatura Rejeitada")
    push_vaga_publicada = models.BooleanField(default=True, verbose_name="Push - Vaga Publicada")
    push_evento_proximo = models.BooleanField(default=True, verbose_name="Push - Evento Próximo")
    
    # Configurações gerais
    receber_emails = models.BooleanField(default=True, verbose_name="Receber Emails")
    receber_push = models.BooleanField(default=True, verbose_name="Receber Notificações Push")
    frequencia_digest = models.CharField(
        max_length=10,
        choices=[
            ('imediato', 'Imediato'),
            ('diario', 'Diário'),
            ('semanal', 'Semanal'),
        ],
        default='imediato',
        verbose_name="Frequência do Digest"
    )
    
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    
    class Meta:
        verbose_name = "Configuração de Notificação"
        verbose_name_plural = "Configurações de Notificação"
    
    def __str__(self):
        return f"Configurações de {self.usuario.username}"
