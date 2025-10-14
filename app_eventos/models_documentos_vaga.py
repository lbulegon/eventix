"""
Modelos para documentos específicos por vaga e evento
"""
from django.db import models
from django.contrib.auth import get_user_model
from .models import EmpresaContratante, Evento
from .models_freelancers import VagaEmpresa
from .models_documentos import DocumentoFreelancerEmpresa

User = get_user_model()


class EventoDocumentacao(models.Model):
    """
    Documentos específicos exigidos para um evento
    Sobrescreve a configuração padrão da empresa para este evento
    """
    evento = models.OneToOneField(
        Evento,
        on_delete=models.CASCADE,
        related_name="documentacao",
        verbose_name="Evento"
    )
    
    # Documentos obrigatórios adicionais
    documentos_obrigatorios_adicionais = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Documentos Obrigatórios Adicionais",
        help_text="Lista de tipos de documentos obrigatórios além dos da empresa. Ex: ['certificado_profissional', 'atestado_saude']"
    )
    
    # Período de validade específico para este evento
    periodo_validade_especifico = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Período de Validade Específico (dias)",
        help_text="Se definido, sobrescreve o período padrão da empresa"
    )
    
    # Configurações
    exige_todos_documentos_atualizados = models.BooleanField(
        default=True,
        verbose_name="Exige Todos Documentos Atualizados",
        help_text="Se True, todos os documentos devem estar dentro do período de validade"
    )
    
    prazo_envio_documentos = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Prazo para Envio de Documentos",
        help_text="Data limite para freelancers enviarem documentação"
    )
    
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações",
        help_text="Observações sobre a documentação necessária"
    )
    
    class Meta:
        verbose_name = "Documentação do Evento"
        verbose_name_plural = "Documentações dos Eventos"
    
    def __str__(self):
        return f"Documentação - {self.evento.nome}"
    
    def get_documentos_obrigatorios_completos(self):
        """
        Retorna lista completa de documentos obrigatórios
        (empresa + evento)
        """
        from .models_documentos import ConfiguracaoDocumentosEmpresa
        
        # Documentos da empresa
        try:
            config_empresa = ConfiguracaoDocumentosEmpresa.objects.get(
                empresa_contratante=self.evento.empresa_contratante
            )
            docs_empresa = config_empresa.get_documentos_obrigatorios()
        except ConfiguracaoDocumentosEmpresa.DoesNotExist:
            docs_empresa = []
        
        # Documentos adicionais do evento
        docs_evento = self.documentos_obrigatorios_adicionais or []
        
        # Combinar sem duplicatas
        return list(set(docs_empresa + docs_evento))


class VagaDocumentacao(models.Model):
    """
    Documentos específicos exigidos para uma vaga
    Permite que cada vaga exija documentos diferentes
    """
    vaga = models.OneToOneField(
        VagaEmpresa,
        on_delete=models.CASCADE,
        related_name="documentacao",
        verbose_name="Vaga"
    )
    
    # Documentos obrigatórios para esta vaga
    documentos_obrigatorios = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Documentos Obrigatórios",
        help_text="Lista de tipos de documentos obrigatórios. Ex: ['rg', 'cpf', 'certificado_profissional']"
    )
    
    # Documentos opcionais mas recomendados
    documentos_opcionais = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Documentos Opcionais",
        help_text="Documentos opcionais que podem dar vantagem ao candidato"
    )
    
    # Configurações de validade
    periodo_validade_especifico = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Período de Validade Específico (dias)"
    )
    
    # Prazo
    prazo_envio_documentos = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Prazo para Envio de Documentos"
    )
    
    # Descrição
    descricao_requisitos = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descrição dos Requisitos",
        help_text="Explicação detalhada sobre os documentos necessários"
    )
    
    # Controle
    permite_candidatura_sem_documentos = models.BooleanField(
        default=False,
        verbose_name="Permite Candidatura Sem Documentos",
        help_text="Se True, permite candidatura mesmo sem todos os documentos (documentos podem ser enviados depois)"
    )
    
    class Meta:
        verbose_name = "Documentação da Vaga"
        verbose_name_plural = "Documentações das Vagas"
    
    def __str__(self):
        return f"Documentação - {self.vaga.titulo}"
    
    def get_documentos_obrigatorios_completos(self):
        """
        Retorna lista completa de documentos obrigatórios
        Ordem de prioridade: Vaga > Evento > Empresa
        """
        # Se a vaga define documentos específicos, usar apenas eles
        if self.documentos_obrigatorios:
            return self.documentos_obrigatorios
        
        # Senão, verificar se há documentação do evento
        if hasattr(self.vaga, 'evento') and hasattr(self.vaga.evento, 'documentacao'):
            return self.vaga.evento.documentacao.get_documentos_obrigatorios_completos()
        
        # Senão, usar documentos da empresa
        from .models_documentos import ConfiguracaoDocumentosEmpresa
        try:
            config = ConfiguracaoDocumentosEmpresa.objects.get(
                empresa_contratante=self.vaga.empresa_contratante
            )
            return config.get_documentos_obrigatorios()
        except ConfiguracaoDocumentosEmpresa.DoesNotExist:
            return []
    
    def verificar_documentos_freelancer(self, freelancer):
        """
        Verifica se o freelancer tem todos os documentos necessários
        Retorna (pode_candidatar, docs_faltantes, docs_invalidos)
        """
        docs_obrigatorios = self.get_documentos_obrigatorios_completos()
        
        # Buscar documentos do freelancer para esta empresa
        documentos = DocumentoFreelancerEmpresa.objects.filter(
            empresa_contratante=self.vaga.empresa_contratante,
            freelancer=freelancer
        )
        
        docs_faltantes = []
        docs_invalidos = []
        
        for doc_tipo in docs_obrigatorios:
            doc = documentos.filter(tipo_documento=doc_tipo).first()
            
            if not doc:
                docs_faltantes.append(doc_tipo)
            elif doc.status != 'aprovado':
                docs_faltantes.append(doc_tipo)
            elif not doc.esta_valido:
                docs_invalidos.append(doc_tipo)
        
        pode_candidatar = (
            len(docs_faltantes) == 0 and 
            len(docs_invalidos) == 0
        ) or self.permite_candidatura_sem_documentos
        
        return pode_candidatar, docs_faltantes, docs_invalidos


class TipoDocumentoCustomizado(models.Model):
    """
    Permite criar tipos de documentos personalizados para empresas
    Além dos tipos padrão do sistema
    """
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="tipos_documentos_customizados",
        verbose_name="Empresa Contratante"
    )
    
    # Identificação
    codigo = models.SlugField(
        max_length=50,
        verbose_name="Código",
        help_text="Código único para identificar o documento. Ex: 'alvara_trabalho_noturno'"
    )
    nome = models.CharField(
        max_length=100,
        verbose_name="Nome do Documento"
    )
    descricao = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descrição"
    )
    
    # Configurações
    obrigatorio_por_padrao = models.BooleanField(
        default=False,
        verbose_name="Obrigatório por Padrão",
        help_text="Se este documento é obrigatório para todas as vagas da empresa"
    )
    periodo_validade = models.PositiveIntegerField(
        default=365,
        verbose_name="Período de Validade (dias)"
    )
    
    # Status
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    
    class Meta:
        verbose_name = "Tipo de Documento Customizado"
        verbose_name_plural = "Tipos de Documentos Customizados"
        unique_together = ('empresa_contratante', 'codigo')
    
    def __str__(self):
        return f"{self.nome} - {self.empresa_contratante.nome_fantasia}"

