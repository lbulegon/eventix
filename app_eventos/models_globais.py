"""
MODELOS GLOBAIS DO SISTEMA EVENTIX
==================================

Estes modelos são compartilhados entre todas as empresas contratantes
e só podem ser gerenciados pelo administrador do sistema.

Categorias de Modelos Globais:
1. CATÁLOGOS GERAIS - Categorias, tipos, classificações
2. CONFIGURAÇÕES SISTEMA - Configurações globais
3. INTEGRAÇÕES - APIs, webhooks, integrações
4. TEMPLATES - Templates de documentos, emails
5. AUDITORIA - Logs, backups, versões
6. MARKETPLACE - Freelancers, fornecedores globais
"""

from django.db import models
from django.utils import timezone


class ModeloGlobal(models.Model):
    """
    Classe base para modelos globais do sistema
    """
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    criado_por = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_criados",
        verbose_name="Criado por",
        limit_choices_to={'tipo_usuario': 'admin_sistema'}
    )

    class Meta:
        abstract = True


# ============================================================================
# CATÁLOGOS GERAIS
# ============================================================================

class CategoriaGlobal(ModeloGlobal):
    """
    Categorias globais que servem como referência para todas as empresas
    """
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    icone = models.CharField(max_length=50, blank=True, null=True, verbose_name="Ícone")
    cor = models.CharField(max_length=7, blank=True, null=True, verbose_name="Cor (HEX)")
    ordem = models.PositiveIntegerField(default=0, verbose_name="Ordem de Exibição")

    class Meta:
        verbose_name = "Categoria Global"
        verbose_name_plural = "Categorias Globais"
        ordering = ['ordem', 'nome']

    def __str__(self):
        return self.nome


class TipoGlobal(ModeloGlobal):
    """
    Tipos globais que servem como referência para todas as empresas
    """
    categoria = models.ForeignKey(
        CategoriaGlobal,
        on_delete=models.CASCADE,
        related_name="tipos",
        verbose_name="Categoria"
    )
    nome = models.CharField(max_length=100, verbose_name="Nome")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    codigo = models.CharField(max_length=20, blank=True, null=True, verbose_name="Código")
    ordem = models.PositiveIntegerField(default=0, verbose_name="Ordem de Exibição")

    class Meta:
        verbose_name = "Tipo Global"
        verbose_name_plural = "Tipos Globais"
        unique_together = ['categoria', 'nome']
        ordering = ['categoria', 'ordem', 'nome']

    def __str__(self):
        return f"{self.nome} ({self.categoria.nome})"


class ClassificacaoGlobal(ModeloGlobal):
    """
    Classificações globais (níveis, status, prioridades, etc.)
    """
    tipo = models.CharField(max_length=50, verbose_name="Tipo de Classificação")
    nome = models.CharField(max_length=100, verbose_name="Nome")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    valor = models.IntegerField(default=0, verbose_name="Valor/Ordem")
    cor = models.CharField(max_length=7, blank=True, null=True, verbose_name="Cor (HEX)")

    class Meta:
        verbose_name = "Classificação Global"
        verbose_name_plural = "Classificações Globais"
        unique_together = ['tipo', 'nome']
        ordering = ['tipo', 'valor', 'nome']

    def __str__(self):
        return f"{self.nome} ({self.tipo})"


# ============================================================================
# CONFIGURAÇÕES SISTEMA
# ============================================================================

class ConfiguracaoSistema(ModeloGlobal):
    """
    Configurações globais do sistema
    """
    chave = models.CharField(max_length=100, unique=True, verbose_name="Chave")
    valor = models.TextField(verbose_name="Valor")
    tipo = models.CharField(
        max_length=20,
        choices=[
            ('string', 'Texto'),
            ('integer', 'Número Inteiro'),
            ('float', 'Número Decimal'),
            ('boolean', 'Verdadeiro/Falso'),
            ('json', 'JSON'),
        ],
        default='string',
        verbose_name="Tipo de Dado"
    )
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    categoria = models.CharField(max_length=50, verbose_name="Categoria")

    class Meta:
        verbose_name = "Configuração do Sistema"
        verbose_name_plural = "Configurações do Sistema"
        ordering = ['categoria', 'chave']

    def __str__(self):
        return f"{self.chave} = {self.valor}"


class ParametroSistema(ModeloGlobal):
    """
    Parâmetros do sistema que podem ser ajustados
    """
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome")
    valor_padrao = models.TextField(verbose_name="Valor Padrão")
    valor_atual = models.TextField(verbose_name="Valor Atual")
    tipo = models.CharField(
        max_length=20,
        choices=[
            ('string', 'Texto'),
            ('integer', 'Número Inteiro'),
            ('float', 'Número Decimal'),
            ('boolean', 'Verdadeiro/Falso'),
            ('json', 'JSON'),
        ],
        default='string',
        verbose_name="Tipo de Dado"
    )
    descricao = models.TextField(verbose_name="Descrição")
    categoria = models.CharField(max_length=50, verbose_name="Categoria")
    editavel = models.BooleanField(default=True, verbose_name="Editável")

    class Meta:
        verbose_name = "Parâmetro do Sistema"
        verbose_name_plural = "Parâmetros do Sistema"
        ordering = ['categoria', 'nome']

    def __str__(self):
        return f"{self.nome} = {self.valor_atual}"


# ============================================================================
# INTEGRAÇÕES
# ============================================================================

class IntegracaoGlobal(ModeloGlobal):
    """
    Integrações globais disponíveis para todas as empresas
    """
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome")
    descricao = models.TextField(verbose_name="Descrição")
    tipo = models.CharField(
        max_length=20,
        choices=[
            ('api', 'API REST'),
            ('webhook', 'Webhook'),
            ('sftp', 'SFTP'),
            ('email', 'Email'),
            ('sms', 'SMS'),
            ('payment', 'Pagamento'),
        ],
        verbose_name="Tipo de Integração"
    )
    url_base = models.URLField(blank=True, null=True, verbose_name="URL Base")
    documentacao = models.URLField(blank=True, null=True, verbose_name="Documentação")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        verbose_name = "Integração Global"
        verbose_name_plural = "Integrações Globais"
        ordering = ['nome']

    def __str__(self):
        return self.nome


class WebhookGlobal(ModeloGlobal):
    """
    Webhooks globais do sistema
    """
    integracao = models.ForeignKey(
        IntegracaoGlobal,
        on_delete=models.CASCADE,
        related_name="webhooks",
        verbose_name="Integração"
    )
    evento = models.CharField(max_length=100, verbose_name="Evento")
    url = models.URLField(verbose_name="URL do Webhook")
    metodo = models.CharField(
        max_length=10,
        choices=[
            ('POST', 'POST'),
            ('PUT', 'PUT'),
            ('PATCH', 'PATCH'),
        ],
        default='POST',
        verbose_name="Método HTTP"
    )
    headers = models.JSONField(default=dict, blank=True, verbose_name="Headers")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        verbose_name = "Webhook Global"
        verbose_name_plural = "Webhooks Globais"
        unique_together = ['integracao', 'evento']
        ordering = ['integracao', 'evento']

    def __str__(self):
        return f"{self.integracao.nome} - {self.evento}"


# ============================================================================
# TEMPLATES
# ============================================================================

class TemplateGlobal(ModeloGlobal):
    """
    Templates globais para documentos, emails, etc.
    """
    TIPO_TEMPLATE_CHOICES = [
        ('email', 'Email'),
        ('documento', 'Documento'),
        ('notificacao', 'Notificação'),
        ('relatorio', 'Relatório'),
        ('contrato', 'Contrato'),
    ]
    
    nome = models.CharField(max_length=100, verbose_name="Nome")
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_TEMPLATE_CHOICES,
        verbose_name="Tipo de Template"
    )
    assunto = models.CharField(max_length=200, blank=True, null=True, verbose_name="Assunto")
    conteudo = models.TextField(verbose_name="Conteúdo")
    variaveis = models.JSONField(default=list, blank=True, verbose_name="Variáveis Disponíveis")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        verbose_name = "Template Global"
        verbose_name_plural = "Templates Globais"
        unique_together = ['nome', 'tipo']
        ordering = ['tipo', 'nome']

    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"


# ============================================================================
# AUDITORIA
# ============================================================================

class LogSistema(ModeloGlobal):
    """
    Logs globais do sistema
    """
    NIVEL_CHOICES = [
        ('DEBUG', 'Debug'),
        ('INFO', 'Informação'),
        ('WARNING', 'Aviso'),
        ('ERROR', 'Erro'),
        ('CRITICAL', 'Crítico'),
    ]
    
    nivel = models.CharField(
        max_length=10,
        choices=NIVEL_CHOICES,
        verbose_name="Nível"
    )
    mensagem = models.TextField(verbose_name="Mensagem")
    modulo = models.CharField(max_length=100, verbose_name="Módulo")
    funcao = models.CharField(max_length=100, blank=True, null=True, verbose_name="Função")
    linha = models.PositiveIntegerField(blank=True, null=True, verbose_name="Linha")
    dados_extras = models.JSONField(default=dict, blank=True, verbose_name="Dados Extras")

    class Meta:
        verbose_name = "Log do Sistema"
        verbose_name_plural = "Logs do Sistema"
        ordering = ['-data_criacao']

    def __str__(self):
        return f"[{self.nivel}] {self.mensagem[:50]}..."


class BackupGlobal(ModeloGlobal):
    """
    Backups globais do sistema
    """
    nome = models.CharField(max_length=200, verbose_name="Nome do Backup")
    tipo = models.CharField(
        max_length=20,
        choices=[
            ('completo', 'Completo'),
            ('incremental', 'Incremental'),
            ('diferencial', 'Diferencial'),
        ],
        verbose_name="Tipo de Backup"
    )
    tamanho = models.BigIntegerField(verbose_name="Tamanho (bytes)")
    localizacao = models.CharField(max_length=500, verbose_name="Localização")
    status = models.CharField(
        max_length=20,
        choices=[
            ('em_andamento', 'Em Andamento'),
            ('concluido', 'Concluído'),
            ('falhou', 'Falhou'),
        ],
        default='em_andamento',
        verbose_name="Status"
    )
    data_inicio = models.DateTimeField(verbose_name="Data de Início")
    data_fim = models.DateTimeField(blank=True, null=True, verbose_name="Data de Fim")

    class Meta:
        verbose_name = "Backup Global"
        verbose_name_plural = "Backups Globais"
        ordering = ['-data_inicio']

    def __str__(self):
        return f"{self.nome} - {self.get_status_display()}"


# ============================================================================
# MARKETPLACE
# ============================================================================

class CategoriaFreelancerGlobal(ModeloGlobal):
    """
    Categorias globais de freelancers
    """
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    icone = models.CharField(max_length=50, blank=True, null=True, verbose_name="Ícone")
    cor = models.CharField(max_length=7, blank=True, null=True, verbose_name="Cor (HEX)")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        verbose_name = "Categoria de Freelancer Global"
        verbose_name_plural = "Categorias de Freelancer Globais"
        ordering = ['nome']

    def __str__(self):
        return self.nome


class HabilidadeGlobal(ModeloGlobal):
    """
    Habilidades globais disponíveis para freelancers
    """
    categoria = models.ForeignKey(
        CategoriaFreelancerGlobal,
        on_delete=models.CASCADE,
        related_name="habilidades",
        verbose_name="Categoria"
    )
    nome = models.CharField(max_length=100, verbose_name="Nome")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    nivel_minimo = models.CharField(
        max_length=20,
        choices=[
            ('iniciante', 'Iniciante'),
            ('intermediario', 'Intermediário'),
            ('avancado', 'Avançado'),
            ('especialista', 'Especialista'),
        ],
        default='iniciante',
        verbose_name="Nível Mínimo"
    )
    ativo = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        verbose_name = "Habilidade Global"
        verbose_name_plural = "Habilidades Globais"
        unique_together = ['categoria', 'nome']
        ordering = ['categoria', 'nome']

    def __str__(self):
        return f"{self.nome} ({self.categoria.nome})"


class FornecedorGlobal(ModeloGlobal):
    """
    Fornecedores globais do marketplace
    """
    nome = models.CharField(max_length=200, verbose_name="Nome")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    website = models.URLField(blank=True, null=True, verbose_name="Website")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    endereco = models.TextField(blank=True, null=True, verbose_name="Endereço")
    categoria = models.CharField(max_length=100, verbose_name="Categoria")
    avaliacao_media = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        verbose_name="Avaliação Média"
    )
    total_avaliacoes = models.PositiveIntegerField(default=0, verbose_name="Total de Avaliações")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        verbose_name = "Fornecedor Global"
        verbose_name_plural = "Fornecedores Globais"
        ordering = ['nome']

    def __str__(self):
        return self.nome

