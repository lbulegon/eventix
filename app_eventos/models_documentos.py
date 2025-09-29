"""
Modelos para gestão de documentos de freelancers por empresa
"""
from django.db import models
from django.contrib.auth import get_user_model
from .models import EmpresaContratante
from .models_freelancers import FreelancerGlobal

User = get_user_model()


class DocumentoFreelancerEmpresa(models.Model):
    """
    Documentos de freelancers armazenados por empresa
    Permite reutilização de documentos dentro do período de validade
    """
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="documentos_freelancers",
        verbose_name="Empresa Contratante"
    )
    freelancer = models.ForeignKey(
        FreelancerGlobal,
        on_delete=models.CASCADE,
        related_name="documentos_empresas",
        verbose_name="Freelancer"
    )
    
    # Tipo de documento
    TIPO_DOCUMENTO_CHOICES = [
        ('rg', 'RG'),
        ('cpf', 'CPF'),
        ('ctps', 'Carteira de Trabalho'),
        ('comprovante_residencia', 'Comprovante de Residência'),
        ('certificado_reservista', 'Certificado de Reservista'),
        ('comprovante_escolaridade', 'Comprovante de Escolaridade'),
        ('certificado_profissional', 'Certificado Profissional'),
        ('outros', 'Outros'),
    ]
    
    tipo_documento = models.CharField(
        max_length=30,
        choices=TIPO_DOCUMENTO_CHOICES,
        verbose_name="Tipo de Documento"
    )
    
    # Arquivo do documento
    arquivo = models.FileField(
        upload_to='documentos_freelancers_empresas/%Y/%m/%d/',
        verbose_name="Arquivo do Documento"
    )
    
    # Status do documento
    STATUS_DOCUMENTO_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado'),
        ('rejeitado', 'Rejeitado'),
        ('expirado', 'Expirado'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_DOCUMENTO_CHOICES,
        default='pendente',
        verbose_name="Status do Documento"
    )
    
    # Controle de validade
    data_upload = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data do Upload"
    )
    data_vencimento = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data de Vencimento",
        help_text="Data de vencimento do documento"
    )
    data_validacao = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data da Validação"
    )
    
    # Validação
    validado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documentos_validados_empresa",
        verbose_name="Validado por"
    )
    
    # Observações
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações"
    )
    
    # Controle de reutilização
    pode_reutilizar = models.BooleanField(
        default=True,
        verbose_name="Pode Reutilizar",
        help_text="Se este documento pode ser reutilizado em outras vagas"
    )
    total_reutilizacoes = models.PositiveIntegerField(
        default=0,
        verbose_name="Total de Reutilizações"
    )
    
    class Meta:
        verbose_name = "Documento do Freelancer por Empresa"
        verbose_name_plural = "Documentos dos Freelancers por Empresa"
        unique_together = ('empresa_contratante', 'freelancer', 'tipo_documento')
    
    def __str__(self):
        return f"{self.get_tipo_documento_display()} - {self.freelancer.usuario.username} - {self.empresa_contratante.nome_fantasia}"
    
    @property
    def esta_valido(self):
        """Verifica se o documento ainda está válido"""
        if not self.data_vencimento:
            return True
        
        from django.utils import timezone
        return timezone.now() <= self.data_vencimento
    
    @property
    def pode_ser_reutilizado(self):
        """Verifica se o documento pode ser reutilizado"""
        return (
            self.status == 'aprovado' and
            self.esta_valido and
            self.pode_reutilizar
        )
    
    def marcar_como_reutilizado(self):
        """Marca o documento como reutilizado"""
        self.total_reutilizacoes += 1
        self.save()


class ConfiguracaoDocumentosEmpresa(models.Model):
    """
    Configuração de documentos por empresa
    Define quais documentos são obrigatórios e seus períodos de validade
    """
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="configuracoes_documentos",
        verbose_name="Empresa Contratante"
    )
    
    # Configurações gerais
    aceita_documentos_externos = models.BooleanField(
        default=True,
        verbose_name="Aceita Documentos Externos",
        help_text="Se aceita documentos de outras empresas"
    )
    periodo_validade_padrao = models.PositiveIntegerField(
        default=365,
        verbose_name="Período de Validade Padrão (dias)",
        help_text="Período padrão de validade dos documentos em dias"
    )
    
    # Documentos obrigatórios
    rg_obrigatorio = models.BooleanField(default=True, verbose_name="RG Obrigatório")
    cpf_obrigatorio = models.BooleanField(default=True, verbose_name="CPF Obrigatório")
    ctps_obrigatorio = models.BooleanField(default=True, verbose_name="CTPS Obrigatório")
    comprovante_residencia_obrigatorio = models.BooleanField(default=True, verbose_name="Comprovante de Residência Obrigatório")
    certificado_reservista_obrigatorio = models.BooleanField(default=False, verbose_name="Certificado de Reservista Obrigatório")
    comprovante_escolaridade_obrigatorio = models.BooleanField(default=False, verbose_name="Comprovante de Escolaridade Obrigatório")
    certificado_profissional_obrigatorio = models.BooleanField(default=False, verbose_name="Certificado Profissional Obrigatório")
    
    # Períodos de validade específicos
    periodo_validade_rg = models.PositiveIntegerField(default=365, verbose_name="Validade RG (dias)")
    periodo_validade_cpf = models.PositiveIntegerField(default=365, verbose_name="Validade CPF (dias)")
    periodo_validade_ctps = models.PositiveIntegerField(default=365, verbose_name="Validade CTPS (dias)")
    periodo_validade_residencia = models.PositiveIntegerField(default=90, verbose_name="Validade Residência (dias)")
    periodo_validade_reservista = models.PositiveIntegerField(default=365, verbose_name="Validade Reservista (dias)")
    periodo_validade_escolaridade = models.PositiveIntegerField(default=365, verbose_name="Validade Escolaridade (dias)")
    periodo_validade_profissional = models.PositiveIntegerField(default=365, verbose_name="Validade Profissional (dias)")
    
    class Meta:
        verbose_name = "Configuração de Documentos da Empresa"
        verbose_name_plural = "Configurações de Documentos das Empresas"
    
    def __str__(self):
        return f"Configuração de Documentos - {self.empresa_contratante.nome_fantasia}"
    
    def get_documentos_obrigatorios(self):
        """Retorna lista dos documentos obrigatórios"""
        obrigatorios = []
        if self.rg_obrigatorio:
            obrigatorios.append('rg')
        if self.cpf_obrigatorio:
            obrigatorios.append('cpf')
        if self.ctps_obrigatorio:
            obrigatorios.append('ctps')
        if self.comprovante_residencia_obrigatorio:
            obrigatorios.append('comprovante_residencia')
        if self.certificado_reservista_obrigatorio:
            obrigatorios.append('certificado_reservista')
        if self.comprovante_escolaridade_obrigatorio:
            obrigatorios.append('comprovante_escolaridade')
        if self.certificado_profissional_obrigatorio:
            obrigatorios.append('certificado_profissional')
        return obrigatorios
    
    def get_periodo_validade(self, tipo_documento):
        """Retorna o período de validade para um tipo de documento"""
        periodos = {
            'rg': self.periodo_validade_rg,
            'cpf': self.periodo_validade_cpf,
            'ctps': self.periodo_validade_ctps,
            'comprovante_residencia': self.periodo_validade_residencia,
            'certificado_reservista': self.periodo_validade_reservista,
            'comprovante_escolaridade': self.periodo_validade_escolaridade,
            'certificado_profissional': self.periodo_validade_profissional,
        }
        return periodos.get(tipo_documento, self.periodo_validade_padrao)


class ReutilizacaoDocumento(models.Model):
    """
    Controle de reutilização de documentos
    """
    documento_original = models.ForeignKey(
        DocumentoFreelancerEmpresa,
        on_delete=models.CASCADE,
        related_name="reutilizacoes",
        verbose_name="Documento Original"
    )
    vaga_utilizada = models.ForeignKey(
        'app_eventos.VagaEmpresa',
        on_delete=models.CASCADE,
        related_name="documentos_reutilizados",
        verbose_name="Vaga Utilizada"
    )
    candidatura = models.ForeignKey(
        'app_eventos.CandidaturaEmpresa',
        on_delete=models.CASCADE,
        related_name="documentos_reutilizados",
        verbose_name="Candidatura"
    )
    
    # Controle
    data_reutilizacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data da Reutilização"
    )
    status_na_reutilizacao = models.CharField(
        max_length=20,
        choices=[
            ('aprovado', 'Aprovado'),
            ('rejeitado', 'Rejeitado'),
            ('pendente', 'Pendente'),
        ],
        default='aprovado',
        verbose_name="Status na Reutilização"
    )
    
    class Meta:
        verbose_name = "Reutilização de Documento"
        verbose_name_plural = "Reutilizações de Documentos"
        unique_together = ('documento_original', 'candidatura')
    
    def __str__(self):
        return f"Reutilização - {self.documento_original.get_tipo_documento_display()} - {self.vaga_utilizada.titulo}"
