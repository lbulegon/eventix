"""
Modelos específicos para gestão de freelancers
"""
from django.db import models
from django.contrib.auth import get_user_model
from .models import EmpresaContratante

User = get_user_model()


class FreelancerGlobal(models.Model):
    """
    Freelancers do marketplace global - sem vínculo permanente com empresas
    """
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="freelancer_global",
        verbose_name="Usuário"
    )
    
    # Dados públicos do marketplace
    perfil_publico = models.BooleanField(
        default=True,
        verbose_name="Perfil Público",
        help_text="Se o perfil é visível no marketplace"
    )
    disponivel_para_vagas = models.BooleanField(
        default=True,
        verbose_name="Disponível para Vagas",
        help_text="Se está disponível para receber vagas"
    )
    
    # Avaliação global
    avaliacao_global = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        verbose_name="Avaliação Global",
        help_text="Avaliação média de todas as empresas"
    )
    total_avaliacoes = models.PositiveIntegerField(
        default=0,
        verbose_name="Total de Avaliações"
    )
    total_eventos = models.PositiveIntegerField(
        default=0,
        verbose_name="Total de Eventos"
    )
    
    # Controle de qualidade
    nivel_confiabilidade = models.CharField(
        max_length=20,
        choices=[
            ('alta', 'Alta'),
            ('media', 'Média'),
            ('baixa', 'Baixa'),
        ],
        default='media',
        verbose_name="Nível de Confiabilidade"
    )
    verificado = models.BooleanField(
        default=False,
        verbose_name="Verificado",
        help_text="Se o perfil foi verificado pelo sistema"
    )
    
    # Dados de contato público
    telefone_publico = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Telefone Público"
    )
    email_publico = models.EmailField(
        blank=True,
        null=True,
        verbose_name="Email Público"
    )
    website_pessoal = models.URLField(
        blank=True,
        null=True,
        verbose_name="Website Pessoal"
    )
    
    class Meta:
        verbose_name = "Freelancer Global"
        verbose_name_plural = "Freelancers Globais"
    
    def __str__(self):
        return f"{self.usuario.username} (Global)"


class VagaEmpresa(models.Model):
    """
    Vagas específicas de cada empresa
    """
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="vagas_empresa",
        verbose_name="Empresa Contratante"
    )
    
    # Configuração da vaga
    titulo = models.CharField(max_length=200, verbose_name="Título da Vaga")
    descricao = models.TextField(verbose_name="Descrição")
    
    # Exigência de vínculo empregatício
    exige_vinculo_empregaticio = models.BooleanField(
        default=False,
        verbose_name="Exige Vínculo Empregatício",
        help_text="Se esta vaga exige contrato temporário de trabalho"
    )
    
    # Tipo de vínculo (quando exigido)
    TIPO_VINCULO_CHOICES = [
        ('temporario', 'Contrato Temporário'),
        ('intermitente', 'Contrato Intermitente'),
        ('terceirizado', 'Terceirizado'),
    ]
    
    tipo_vinculo = models.CharField(
        max_length=20,
        choices=TIPO_VINCULO_CHOICES,
        blank=True,
        null=True,
        verbose_name="Tipo de Vínculo",
        help_text="Tipo de vínculo empregatício exigido"
    )
    
    # Requisitos
    experiencia_minima = models.CharField(
        max_length=20,
        choices=[
            ('iniciante', 'Iniciante'),
            ('intermediario', 'Intermediário'),
            ('avancado', 'Avançado'),
            ('especialista', 'Especialista'),
        ],
        default='iniciante',
        verbose_name="Experiência Mínima"
    )
    
    # Remuneração
    remuneracao = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valor da Remuneração"
    )
    tipo_remuneracao = models.CharField(
        max_length=20,
        choices=[
            ('por_hora', 'Por Hora'),
            ('por_dia', 'Por Dia'),
            ('por_evento', 'Por Evento'),
            ('fixo', 'Valor Fixo'),
        ],
        default='por_evento',
        verbose_name="Tipo de Remuneração"
    )
    
    # Controle
    quantidade_vagas = models.PositiveIntegerField(verbose_name="Quantidade de Vagas")
    quantidade_preenchida = models.PositiveIntegerField(
        default=0,
        verbose_name="Vagas Preenchidas"
    )
    
    # Datas
    data_inicio = models.DateTimeField(verbose_name="Data de Início")
    data_fim = models.DateTimeField(verbose_name="Data de Fim")
    data_limite_candidatura = models.DateTimeField(
        verbose_name="Data Limite para Candidatura"
    )
    
    # Status
    ativa = models.BooleanField(default=True, verbose_name="Ativa")
    publicada = models.BooleanField(default=False, verbose_name="Publicada")
    
    class Meta:
        verbose_name = "Vaga da Empresa"
        verbose_name_plural = "Vagas da Empresa"
    
    def __str__(self):
        return f"{self.titulo} - {self.empresa_contratante.nome_fantasia}"
    
    @property
    def vagas_disponiveis(self):
        return self.quantidade_vagas - self.quantidade_preenchida
    
    @property
    def exige_documentacao(self):
        """Se esta vaga exige documentação para vínculo empregatício"""
        return self.exige_vinculo_empregaticio


class CandidaturaEmpresa(models.Model):
    """
    Candidaturas para vagas da empresa
    """
    vaga = models.ForeignKey(
        VagaEmpresa,
        on_delete=models.CASCADE,
        related_name="candidaturas",
        verbose_name="Vaga"
    )
    
    # Freelancer (sempre do marketplace global)
    freelancer = models.ForeignKey(
        FreelancerGlobal,
        on_delete=models.CASCADE,
        related_name="candidaturas",
        verbose_name="Freelancer"
    )
    
    # Dados da candidatura
    carta_apresentacao = models.TextField(
        blank=True,
        null=True,
        verbose_name="Carta de Apresentação"
    )
    experiencia_relacionada = models.TextField(
        blank=True,
        null=True,
        verbose_name="Experiência Relacionada"
    )
    
    # Status
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovada', 'Aprovada'),
        ('rejeitada', 'Rejeitada'),
        ('cancelada', 'Cancelada'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pendente',
        verbose_name="Status"
    )
    
    # Controle
    data_candidatura = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data da Candidatura"
    )
    data_avaliacao = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data da Avaliação"
    )
    observacoes_empresa = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações da Empresa"
    )
    
    class Meta:
        verbose_name = "Candidatura da Empresa"
        verbose_name_plural = "Candidaturas da Empresa"
        unique_together = ('vaga', 'freelancer')
    
    def __str__(self):
        return f"{self.freelancer.usuario.username} - {self.vaga.titulo}"
    
    @property
    def exige_documentacao(self):
        """Se esta candidatura exige documentação"""
        return self.vaga.exige_vinculo_empregaticio


class DocumentoFreelancer(models.Model):
    """
    Documentos obrigatórios para freelancers em vagas com vínculo empregatício
    """
    candidatura = models.ForeignKey(
        CandidaturaEmpresa,
        on_delete=models.CASCADE,
        related_name="documentos",
        verbose_name="Candidatura"
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
        upload_to='documentos_freelancers/%Y/%m/%d/',
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
    
    # Observações
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações"
    )
    
    # Controle
    data_upload = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data do Upload"
    )
    data_validacao = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data da Validação"
    )
    validado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documentos_validados",
        verbose_name="Validado por"
    )
    
    class Meta:
        verbose_name = "Documento do Freelancer"
        verbose_name_plural = "Documentos dos Freelancers"
        unique_together = ('candidatura', 'tipo_documento')
    
    def __str__(self):
        return f"{self.get_tipo_documento_display()} - {self.candidatura.freelancer.usuario.username}"


class ContratacaoEmpresa(models.Model):
    """
    Contratação efetiva de freelancer para vaga
    """
    candidatura = models.OneToOneField(
        CandidaturaEmpresa,
        on_delete=models.CASCADE,
        related_name="contratacao",
        verbose_name="Candidatura"
    )
    
    # Dados da contratação
    data_contratacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data da Contratação"
    )
    
    # Status da contratação
    STATUS_CONTRATACAO_CHOICES = [
        ('ativa', 'Ativa'),
        ('concluida', 'Concluída'),
        ('cancelada', 'Cancelada'),
        ('suspensa', 'Suspensa'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CONTRATACAO_CHOICES,
        default='ativa',
        verbose_name="Status da Contratação"
    )
    
    # Vínculo empregatício
    tem_vinculo_empregaticio = models.BooleanField(
        default=False,
        verbose_name="Tem Vínculo Empregatício",
        help_text="Se foi criado vínculo empregatício"
    )
    
    # Dados do contrato (quando aplicável)
    numero_contrato = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Número do Contrato"
    )
    data_inicio_contrato = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Início do Contrato"
    )
    data_fim_contrato = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Fim do Contrato"
    )
    
    # Remuneração efetiva
    remuneracao_efetiva = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Remuneração Efetiva"
    )
    
    # Controle
    contratado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contratacoes_realizadas",
        verbose_name="Contratado por"
    )
    
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações"
    )
    
    class Meta:
        verbose_name = "Contratação da Empresa"
        verbose_name_plural = "Contratações da Empresa"
    
    def __str__(self):
        return f"Contratação - {self.candidatura.freelancer.usuario.username} - {self.candidatura.vaga.titulo}"
    
    @property
    def documentos_obrigatorios_aprovados(self):
        """Verifica se todos os documentos obrigatórios foram aprovados"""
        if not self.candidatura.exige_documentacao:
            return True
        
        documentos = self.candidatura.documentos.all()
        if not documentos.exists():
            return False
        
        return all(doc.status == 'aprovado' for doc in documentos)
    
    @property
    def pode_iniciar_trabalho(self):
        """Verifica se pode iniciar o trabalho"""
        if not self.tem_vinculo_empregaticio:
            return True
        
        return self.documentos_obrigatorios_aprovados
