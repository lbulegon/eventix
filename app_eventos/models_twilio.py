"""
Modelos para Sistema de Notificações via Twilio (WhatsApp + SMS)
"""
from django.db import models
from django.conf import settings


class UserContact(models.Model):
    """
    Contatos de usuários para WhatsApp/SMS
    """
    CHANNEL_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('sms', 'SMS'),
    ]
    
    # Multi-tenant
    empresa_contratante = models.ForeignKey(
        'EmpresaContratante',
        on_delete=models.CASCADE,
        related_name='user_contacts',
        verbose_name="Empresa Contratante"
    )
    
    # Usuário (pode ser null para leads/não cadastrados)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='contacts',
        verbose_name="Usuário"
    )
    
    # Freelancer (opcional, para vincular diretamente)
    freelancer = models.ForeignKey(
        'Freelance',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='contacts_twilio',
        verbose_name="Freelancer"
    )
    
    # Canal e endereço
    channel_type = models.CharField(
        max_length=20,
        choices=CHANNEL_CHOICES,
        default='whatsapp',
        verbose_name="Tipo de Canal"
    )
    address = models.CharField(
        max_length=20,
        verbose_name="Número (Formato E.164)",
        help_text="Exemplo: +5511999999999"
    )
    
    # Consentimento e verificação
    consent = models.BooleanField(
        default=False,
        verbose_name="Consentimento para Receber Mensagens"
    )
    consent_timestamp = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data do Consentimento"
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name="Número Verificado"
    )
    last_verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Última Verificação"
    )
    
    # Controle
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Contato de Usuário"
        verbose_name_plural = "Contatos de Usuários"
        unique_together = ['empresa_contratante', 'address', 'channel_type']
        ordering = ['-created_at']
    
    def __str__(self):
        if self.user:
            return f"{self.user.username} - {self.address} ({self.channel_type})"
        return f"{self.address} ({self.channel_type})"


class OtpLog(models.Model):
    """
    Log de códigos OTP enviados (verificação)
    """
    PURPOSE_CHOICES = [
        ('signup', 'Cadastro'),
        ('login', 'Login'),
        ('password_reset', 'Recuperação de Senha'),
        ('phone_verification', 'Verificação de Telefone'),
    ]
    
    STATUS_CHOICES = [
        ('sent', 'Enviado'),
        ('verified', 'Verificado'),
        ('expired', 'Expirado'),
        ('failed', 'Falhou'),
    ]
    
    # Multi-tenant
    empresa_contratante = models.ForeignKey(
        'EmpresaContratante',
        on_delete=models.CASCADE,
        related_name='otp_logs',
        verbose_name="Empresa Contratante"
    )
    
    # Endereço e canal
    address = models.CharField(
        max_length=20,
        verbose_name="Número (Formato E.164)"
    )
    channel_type = models.CharField(
        max_length=20,
        choices=UserContact.CHANNEL_CHOICES,
        default='whatsapp',
        verbose_name="Canal Usado"
    )
    
    # Propósito e status
    purpose = models.CharField(
        max_length=30,
        choices=PURPOSE_CHOICES,
        default='signup',
        verbose_name="Propósito"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='sent',
        verbose_name="Status"
    )
    
    # Twilio
    provider_sid = models.CharField(
        max_length=100,
        verbose_name="Twilio SID/Verify SID",
        help_text="ID do serviço Twilio"
    )
    
    # Timestamps
    sent_timestamp = models.DateTimeField(auto_now_add=True)
    verified_timestamp = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    meta = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Metadados",
        help_text="Informações adicionais em JSON"
    )
    
    class Meta:
        verbose_name = "Log de OTP"
        verbose_name_plural = "Logs de OTP"
        ordering = ['-sent_timestamp']
        indexes = [
            models.Index(fields=['address', 'status']),
            models.Index(fields=['provider_sid']),
        ]
    
    def __str__(self):
        return f"{self.address} - {self.purpose} ({self.status})"


class BroadcastLog(models.Model):
    """
    Log de campanhas de broadcast (envio em massa)
    """
    CHANNEL_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('sms', 'SMS'),
        ('both', 'Ambos (com fallback)'),
    ]
    
    # Multi-tenant
    empresa_contratante = models.ForeignKey(
        'EmpresaContratante',
        on_delete=models.CASCADE,
        related_name='broadcast_logs',
        verbose_name="Empresa Contratante"
    )
    
    # Informações da campanha
    campaign_name = models.CharField(
        max_length=200,
        verbose_name="Nome da Campanha"
    )
    body_template = models.TextField(
        verbose_name="Corpo da Mensagem"
    )
    channel_preferred = models.CharField(
        max_length=20,
        choices=CHANNEL_CHOICES,
        default='whatsapp',
        verbose_name="Canal Preferencial"
    )
    
    # Relacionamento com evento (opcional)
    evento = models.ForeignKey(
        'Evento',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='broadcasts',
        verbose_name="Evento Relacionado"
    )
    
    # Estatísticas
    total_targets = models.PositiveIntegerField(
        default=0,
        verbose_name="Total de Destinatários"
    )
    sent = models.PositiveIntegerField(
        default=0,
        verbose_name="Enviados"
    )
    delivered = models.PositiveIntegerField(
        default=0,
        verbose_name="Entregues"
    )
    failed = models.PositiveIntegerField(
        default=0,
        verbose_name="Falhados"
    )
    
    # Controle
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='broadcasts_created',
        verbose_name="Criado Por"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    meta = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Metadados"
    )
    
    class Meta:
        verbose_name = "Log de Broadcast"
        verbose_name_plural = "Logs de Broadcast"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.campaign_name} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"
    
    @property
    def success_rate(self):
        """Taxa de sucesso do broadcast"""
        if self.total_targets == 0:
            return 0
        return (self.delivered / self.total_targets) * 100


class BroadcastMessage(models.Model):
    """
    Mensagens individuais de um broadcast
    """
    STATUS_CHOICES = [
        ('queued', 'Na Fila'),
        ('sent', 'Enviado'),
        ('delivered', 'Entregue'),
        ('read', 'Lido'),
        ('failed', 'Falhou'),
        ('undelivered', 'Não Entregue'),
    ]
    
    broadcast = models.ForeignKey(
        BroadcastLog,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name="Broadcast"
    )
    
    # Destinatário
    contact = models.ForeignKey(
        UserContact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='broadcast_messages',
        verbose_name="Contato"
    )
    to_address = models.CharField(
        max_length=20,
        verbose_name="Número Destinatário"
    )
    
    # Canal usado
    channel_used = models.CharField(
        max_length=20,
        choices=UserContact.CHANNEL_CHOICES,
        verbose_name="Canal Utilizado"
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='queued',
        verbose_name="Status"
    )
    
    # Twilio
    message_sid = models.CharField(
        max_length=100,
        verbose_name="Twilio Message SID",
        unique=True
    )
    error_code = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name="Código de Erro"
    )
    error_message = models.TextField(
        null=True,
        blank=True,
        verbose_name="Mensagem de Erro"
    )
    
    # Timestamps
    sent_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Mensagem de Broadcast"
        verbose_name_plural = "Mensagens de Broadcast"
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"{self.to_address} - {self.status}"

