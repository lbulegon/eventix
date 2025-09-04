from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models import Q, F

class User(AbstractUser):
    """
    Usuário do sistema com controle multi-empresas
    """
    TIPO_USUARIO_CHOICES = [
        ('admin_empresa', 'Administrador da Empresa'),
        ('operador_empresa', 'Operador da Empresa'),
        ('freelancer', 'Freelancer'),
        ('admin_sistema', 'Administrador do Sistema'),
    ]
    
    tipo_usuario = models.CharField(max_length=20, choices=TIPO_USUARIO_CHOICES, default='freelancer')
    empresa_contratante = models.ForeignKey(
        'EmpresaContratante',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="usuarios",
        verbose_name="Empresa Contratante"
    )
    ativo = models.BooleanField(default=True, db_index=True)
    data_ultimo_acesso = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"

    def __str__(self):
        if self.empresa_contratante:
            return f"{self.username} - {self.empresa_contratante.nome}"
        return self.username

    @property
    def is_freelancer(self):
        """Verifica se o usuário é freelancer"""
        return self.tipo_usuario == 'freelancer'

    @property
    def is_empresa_user(self):
        """Verifica se o usuário é da empresa (admin ou operador)"""
        return self.tipo_usuario in ['admin_empresa', 'operador_empresa']

    @property
    def is_admin_sistema(self):
        """Verifica se o usuário é administrador do sistema"""
        return self.tipo_usuario == 'admin_sistema'

    @property
    def empresa_owner(self):
        """
        Retorna a empresa proprietária do usuário.
        Para freelancers, sempre retorna a Eventix.
        Para usuários de empresa, retorna sua empresa contratante.
        """
        if self.is_freelancer:
            # Sempre retorna a Eventix para freelancers
            return EmpresaContratante.objects.filter(nome_fantasia__icontains='Eventix').first()
        elif self.is_empresa_user:
            return self.empresa_contratante
        return None

    @property
    def pode_gerenciar_empresa(self):
        """Verifica se o usuário pode gerenciar a empresa"""
        return self.tipo_usuario in ['admin_empresa', 'admin_sistema']

    @property
    def pode_operar_sistema(self):
        """Verifica se o usuário pode operar o sistema"""
        return self.tipo_usuario in ['admin_empresa', 'operador_empresa', 'admin_sistema']

    def get_dashboard_url(self):
        """Retorna a URL do dashboard baseada no tipo de usuário"""
        if self.is_admin_sistema:
            return '/admin/'
        elif self.is_empresa_user:
            return '/empresa/dashboard/'
        elif self.is_freelancer:
            return '/freelancer/dashboard/'
        return '/'

    def get_user_type_display_name(self):
        """Retorna o nome amigável do tipo de usuário"""
        type_names = {
            'admin_empresa': 'Administrador da Empresa',
            'operador_empresa': 'Operador da Empresa', 
            'freelancer': 'Freelancer',
            'admin_sistema': 'Administrador do Sistema'
        }
        return type_names.get(self.tipo_usuario, self.tipo_usuario)


class EmpresaContratante(models.Model):
    """
    Empresa que contratou o sistema Eventix
    """
    nome = models.CharField(max_length=255, verbose_name="Nome da Empresa")
    cnpj = models.CharField(max_length=18, verbose_name="CNPJ")
    razao_social = models.CharField(max_length=255, verbose_name="Razão Social")
    nome_fantasia = models.CharField(max_length=255, verbose_name="Nome Fantasia")
    
    # Contato
    telefone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(verbose_name="E-mail")
    website = models.URLField(blank=True, null=True)
    
    # Endereço
    cep = models.CharField(max_length=9, blank=True, null=True)
    logradouro = models.CharField(max_length=255, blank=True, null=True)
    numero = models.CharField(max_length=10, blank=True, null=True)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    uf = models.CharField(max_length=2, blank=True, null=True)
    
    # Contrato
    data_contratacao = models.DateField(auto_now_add=True, verbose_name="Data de Contratação")
    data_vencimento = models.DateField(verbose_name="Data de Vencimento", db_index=True)
    plano_contratado = models.CharField(max_length=50, verbose_name="Plano Contratado")
    valor_mensal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Mensal")
    
    # Status
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Empresa Contratante"
        verbose_name_plural = "Empresas Contratantes"

    def __str__(self):
        return f"{self.nome_fantasia} ({self.cnpj})"

    @property
    def usuarios_ativos(self):
        """Retorna usuários ativos da empresa"""
        return self.usuarios.filter(ativo=True)

    @property
    def eventos_ativos(self):
        """Retorna eventos ativos da empresa"""
        return self.eventos.filter(ativo=True)


class TipoEmpresa(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Tipo de Empresa"
        verbose_name_plural = "Tipos de Empresas"

    def __str__(self):
        return self.nome


class Empresa(models.Model):
    """
    Empresas parceiras (locais, fornecedores, etc.)
    """
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="empresas_parceiras",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    nome = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=18, blank=True, null=True)
    tipo_empresa = models.ForeignKey(
        TipoEmpresa,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="empresas"
    )
    telefone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
        constraints = [
            models.UniqueConstraint(fields=['empresa_contratante', 'cnpj'], name='uniq_empresa_cnpj_por_tenant')
        ]

    def __str__(self):
        empresa = self.empresa_contratante.nome_fantasia if self.empresa_contratante else "—"
        return f"{self.nome} - {empresa}"


class LocalEvento(models.Model):
    nome                 = models.CharField(max_length=200)
    endereco             = models.CharField(max_length=255)
    capacidade           = models.IntegerField()
    descricao            = models.TextField(blank=True, null=True, verbose_name="Descrição")
    empresa_contratante  = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="locais_eventos",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    empresa_proprietaria = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name="locais",
        verbose_name="Empresa Proprietária"
    )
    ativo = models.BooleanField(default=True)

    def __str__(self):
        empresa = self.empresa_contratante.nome_fantasia if self.empresa_contratante else "—"
        return f"{self.nome} - {empresa}"


class Evento(models.Model):
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="eventos",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    nome = models.CharField(max_length=200)
    data_inicio = models.DateField()
    data_fim = models.DateField()
    descricao = models.TextField(blank=True, null=True)
    local = models.ForeignKey(LocalEvento, on_delete=models.CASCADE, related_name="eventos")
    empresa_produtora = models.ForeignKey(
        Empresa,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="eventos_produzidos"
    )
    empresa_contratante_mao_obra = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name="eventos_contratados",
        verbose_name="Empresa Contratante de Mão de Obra"
    )
    ativo         = models.BooleanField(default=True)
    data_criacao  = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        constraints = [
            models.CheckConstraint(check=Q(data_fim__gte=F('data_inicio')), name='evento_fim_gte_inicio')
        ]

    def __str__(self):
        empresa = self.empresa_contratante.nome_fantasia if self.empresa_contratante else "—"
        return f"{self.nome} - {empresa}"
    
    # Métodos para fluxo de caixa
    @property
    def total_despesas(self):
        """Retorna o total de despesas do evento"""
        return self.despesas.aggregate(
            total=models.Sum('valor')
        )['total'] or 0
    
    @property
    def total_receitas(self):
        """Retorna o total de receitas do evento"""
        return self.receitas.aggregate(
            total=models.Sum('valor')
        )['total'] or 0
    
    @property
    def saldo_financeiro(self):
        """Retorna o saldo financeiro (receitas - despesas)"""
        return self.total_receitas - self.total_despesas
    
    @property
    def despesas_pagas(self):
        """Retorna o total de despesas pagas"""
        return self.despesas.filter(status='pago').aggregate(
            total=models.Sum('valor')
        )['total'] or 0
    
    @property
    def receitas_recebidas(self):
        """Retorna o total de receitas recebidas"""
        return self.receitas.filter(status='recebido').aggregate(
            total=models.Sum('valor')
        )['total'] or 0
    
    @property
    def saldo_realizado(self):
        """Retorna o saldo realizado (receitas recebidas - despesas pagas)"""
        return self.receitas_recebidas - self.despesas_pagas
    
    @property
    def despesas_pendentes(self):
        """Retorna o total de despesas pendentes"""
        return self.despesas.filter(status='pendente').aggregate(
            total=models.Sum('valor')
        )['total'] or 0
    
    @property
    def receitas_pendentes(self):
        """Retorna o total de receitas pendentes"""
        return self.receitas.filter(status='pendente').aggregate(
            total=models.Sum('valor')
        )['total'] or 0
    
    @property
    def despesas_atrasadas(self):
        """Retorna despesas atrasadas"""
        return self.despesas.filter(
            status='pendente',
            data_vencimento__lt=timezone.now().date()
        )
    
    @property
    def receitas_atrasadas(self):
        """Retorna receitas atrasadas"""
        return self.receitas.filter(
            status='pendente',
            data_vencimento__lt=timezone.now().date()
        )


class EventoFreelancerInfo(models.Model):
    """
    Informações específicas do freelancer dentro de um Evento
    """
    evento = models.OneToOneField(
        "Evento",
        on_delete=models.CASCADE,
        related_name="freelancer_info"
    )

    horario_inicio  = models.TimeField(help_text="Horário de chegada")
    horario_fim     = models.TimeField(help_text="Horário de saída")

    cache           = models.DecimalField(max_digits=8, decimal_places=2, help_text="Valor do cachê")
    prazo_pagamento = models.CharField(
        max_length=100,
        default="até 7 dias após o evento",
        help_text="Prazo de pagamento"
    )

    beneficios = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Ex.: Lanche incluso, transporte"
    )

    funcao = models.CharField(
        max_length=100,
        help_text="Função do freelancer, ex.: Garçom, Bar, Caixa"
    )

    observacoes = models.TextField(blank=True, null=True, help_text="Observações adicionais")

    def __str__(self):
        return f"Info Freelancer - {self.evento.nome}"


class CategoriaFinanceira(models.Model):
    """
    Categorias para classificar despesas e receitas
    """
    TIPO_CHOICES = [
        ('despesa', 'Despesa'),
        ('receita', 'Receita'),
        ('ambos', 'Ambos'),
    ]
    
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="categorias_financeiras",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    nome      = models.CharField(max_length=100, verbose_name="Nome da Categoria")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    tipo      = models.CharField(max_length=10, choices=TIPO_CHOICES, default='ambos', verbose_name="Tipo")
    cor       = models.CharField(max_length=7, default="#007bff", help_text="Cor em formato hexadecimal (#RRGGBB)")
    ativo     = models.BooleanField(default=True, verbose_name="Ativo")
    
    class Meta:
        verbose_name = "Categoria Financeira"
        verbose_name_plural = "Categorias Financeiras"
        constraints = [
            models.UniqueConstraint(fields=['empresa_contratante', 'nome'], name='uniq_categoria_financeira_por_tenant')
        ]
    
    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"


class Fornecedor(models.Model):
    """
    Fornecedores de serviços e produtos para eventos
    """
    TIPO_FORNECEDOR_CHOICES = [
        ('equipamentos', 'Equipamentos'),
        ('alimentacao', 'Alimentação'),
        ('decoracao', 'Decoração'),
        ('seguranca', 'Segurança'),
        ('transporte', 'Transporte'),
        ('marketing', 'Marketing'),
        ('infraestrutura', 'Infraestrutura'),
        ('outros', 'Outros'),
    ]
    
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="fornecedores",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    nome_fantasia = models.CharField(max_length=200, verbose_name="Nome Fantasia")
    razao_social = models.CharField(max_length=200, verbose_name="Razão Social")
    cnpj = models.CharField(max_length=18, unique=True, verbose_name="CNPJ")
    tipo_fornecedor = models.CharField(max_length=20, choices=TIPO_FORNECEDOR_CHOICES, verbose_name="Tipo de Fornecedor")
    
    # Contato
    telefone        = models.CharField(max_length=20, verbose_name="Telefone")
    email           = models.EmailField(verbose_name="E-mail")
    website         = models.URLField(blank=True, null=True, verbose_name="Website")
    
    # Endereço
    cep             = models.CharField(max_length=9, blank=True, null=True, verbose_name="CEP")
    logradouro      = models.CharField(max_length=255, blank=True, null=True, verbose_name="Logradouro")
    numero          = models.CharField(max_length=10, blank=True, null=True, verbose_name="Número")
    complemento     = models.CharField(max_length=100, blank=True, null=True, verbose_name="Complemento")
    bairro          = models.CharField(max_length=100, blank=True, null=True, verbose_name="Bairro")
    cidade          = models.CharField(max_length=100, blank=True, null=True, verbose_name="Cidade")
    uf              = models.CharField(max_length=2, blank=True, null=True, verbose_name="UF")
    
    # Informações financeiras
    banco           = models.CharField(max_length=100, blank=True, null=True, verbose_name="Banco")
    agencia         = models.CharField(max_length=10, blank=True, null=True, verbose_name="Agência")
    conta           = models.CharField(max_length=20, blank=True, null=True, verbose_name="Conta")
    pix             = models.CharField(max_length=100, blank=True, null=True, verbose_name="Chave PIX")
    
    # Observações e status
    observacoes      = models.TextField(blank=True, null=True, verbose_name="Observações")
    ativo            = models.BooleanField(default=True, verbose_name="Ativo")
    data_cadastro    = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    
    class Meta:
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"
        ordering = ['nome_fantasia']
        constraints = [
            models.UniqueConstraint(fields=['empresa_contratante', 'cnpj'], name='uniq_fornecedor_por_tenant')
        ]
    
    def __str__(self):
        return f"{self.nome_fantasia} - {self.get_tipo_fornecedor_display()}"
    
    @property
    def endereco_completo(self):
        """Retorna o endereço completo formatado"""
        partes = []
        if self.logradouro:
            partes.append(self.logradouro)
        if self.numero:
            partes.append(self.numero)
        if self.complemento:
            partes.append(self.complemento)
        if self.bairro:
            partes.append(self.bairro)
        if self.cidade:
            partes.append(self.cidade)
        if self.uf:
            partes.append(self.uf)
        if self.cep:
            partes.append(f"CEP: {self.cep}")
        
        return ", ".join(partes) if partes else "Endereço não informado"
    
    @property
    def total_despesas(self):
        """Retorna o total de despesas com este fornecedor"""
        return self.despesas.aggregate(
            total=models.Sum('valor')
        )['total'] or 0
    
    @property
    def despesas_pagas(self):
        """Retorna o total de despesas pagas com este fornecedor"""
        return self.despesas.filter(status='pago').aggregate(
            total=models.Sum('valor')
        )['total'] or 0
    
    @property
    def despesas_pendentes(self):
        """Retorna o total de despesas pendentes com este fornecedor"""
        return self.despesas.filter(status='pendente').aggregate(
            total=models.Sum('valor')
        )['total'] or 0


class DespesaEvento(models.Model):
    """
    Despesas associadas a um evento
    """
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('pago', 'Pago'),
        ('cancelado', 'Cancelado'),
    ]
    
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name="despesas",
        verbose_name="Evento"
    )
    categoria = models.ForeignKey(
        CategoriaFinanceira,
        on_delete=models.PROTECT,
        related_name="despesas",
        verbose_name="Categoria"
    )
    descricao        = models.CharField(max_length=255, verbose_name="Descrição")
    valor            = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    data_vencimento  = models.DateField(verbose_name="Data de Vencimento")
    data_pagamento   = models.DateField(blank=True, null=True, verbose_name="Data de Pagamento")
    fornecedor       = models.ForeignKey(
        Fornecedor,
        on_delete=models.SET_NULL,
        related_name="despesas",
        verbose_name="Fornecedor",
        null=True,
        blank=True
    )
    numero_documento = models.CharField(max_length=50, blank=True, null=True, verbose_name="Número do Documento")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pendente', verbose_name="Status")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    
    class Meta:
        verbose_name = "Despesa do Evento"
        verbose_name_plural = "Despesas do Evento"
        ordering = ['-data_vencimento']
        constraints = [
            models.CheckConstraint(check=Q(status='pago', data_pagamento__isnull=False) | ~Q(status='pago'), name='despesa_pago_tem_data'),
            models.CheckConstraint(check=Q(valor__gte=0), name='despesa_valor_nao_negativo')
        ]
    
    def __str__(self):
        return f"{self.descricao} - R$ {self.valor} ({self.evento.nome})"
    
    @property
    def atrasada(self):
        """Verifica se a despesa está atrasada"""
        if self.status == 'pendente' and self.data_vencimento < timezone.now().date():
            return True
        return False
    
    @property
    def dias_atraso(self):
        """Retorna o número de dias de atraso"""
        if self.atrasada:
            return (timezone.now().date() - self.data_vencimento).days
        return 0


class ReceitaEvento(models.Model):
    """
    Receitas associadas a um evento
    """
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('recebido', 'Recebido'),
        ('cancelado', 'Cancelado'),
    ]
    
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name="receitas",
        verbose_name="Evento"
    )
    categoria = models.ForeignKey(
        CategoriaFinanceira,
        on_delete=models.PROTECT,
        related_name="receitas",
        verbose_name="Categoria"
    )
    descricao = models.CharField(max_length=255, verbose_name="Descrição")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    data_vencimento = models.DateField(verbose_name="Data de Vencimento")
    data_recebimento = models.DateField(blank=True, null=True, verbose_name="Data de Recebimento")
    cliente = models.CharField(max_length=200, blank=True, null=True, verbose_name="Cliente")
    numero_documento = models.CharField(max_length=50, blank=True, null=True, verbose_name="Número do Documento")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pendente', verbose_name="Status")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    
    class Meta:
        verbose_name = "Receita do Evento"
        verbose_name_plural = "Receitas do Evento"
        ordering = ['-data_vencimento']
        constraints = [
            models.CheckConstraint(check=Q(status='recebido', data_recebimento__isnull=False) | ~Q(status='recebido'), name='receita_recebido_tem_data'),
            models.CheckConstraint(check=Q(valor__gte=0), name='receita_valor_nao_negativo')
        ]
    
    def __str__(self):
        return f"{self.descricao} - R$ {self.valor} ({self.evento.nome})"
    
    @property
    def atrasada(self):
        """Verifica se a receita está atrasada"""
        if self.status == 'pendente' and self.data_vencimento < timezone.now().date():
            return True
        return False
    
    @property
    def dias_atraso(self):
        """Retorna o número de dias de atraso"""
        if self.atrasada:
            return (timezone.now().date() - self.data_vencimento).days
        return 0


class SetorEvento(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name="setores")
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    capacidade = models.PositiveIntegerField(blank=True, null=True, verbose_name="Capacidade de Pessoas")
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nome} - {self.evento.nome}"


class CategoriaEquipamento(models.Model):
    """
    Categorias de equipamentos (ex: Áudio, Iluminação, Segurança, etc.)
    """
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="categorias_equipamentos",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Categoria de Equipamento"
        verbose_name_plural = "Categorias de Equipamentos"
        constraints = [
            models.UniqueConstraint(fields=['empresa_contratante', 'nome'], name='uniq_categoria_equipamento_por_tenant')
        ]
    
    def __str__(self):
        empresa = self.empresa_contratante.nome_fantasia if self.empresa_contratante else "—"
        return f"{self.nome} - {empresa}"


class Equipamento(models.Model):
    """
    Equipamentos que podem ser utilizados nos setores dos eventos
    """
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="equipamentos",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    empresa_proprietaria = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name="equipamentos",
        verbose_name="Empresa Proprietária"
    )
    codigo_patrimonial = models.CharField(max_length=200, verbose_name="Código Patrimonial", blank=True, null=True, db_index=True)
    nome = models.CharField(max_length=200, verbose_name="Nome do Equipamento", default="Equipamento")
    categoria = models.ForeignKey(CategoriaEquipamento, on_delete=models.CASCADE, related_name="equipamentos")
    descricao = models.TextField(blank=True, null=True)
    especificacoes_tecnicas = models.TextField(blank=True, null=True)
    marca = models.CharField(max_length=100, blank=True, null=True)
    modelo = models.CharField(max_length=100, blank=True, null=True)
    numero_serie = models.CharField(max_length=100, blank=True, null=True)
    data_aquisicao = models.DateField(blank=True, null=True)
    valor_aquisicao = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    estado_conservacao = models.CharField(max_length=20, choices=[
        ('excelente', 'Excelente'),
        ('bom', 'Bom'),
        ('regular', 'Regular'),
        ('ruim', 'Ruim'),
        ('inutilizavel', 'Inutilizável'),
    ], default='bom')
    foto = models.ImageField(upload_to='equipamentos/fotos/', blank=True, null=True)
    manual_instrucoes = models.FileField(upload_to='equipamentos/manuais/', blank=True, null=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Equipamento"
        verbose_name_plural = "Equipamentos"
    
    def __str__(self):
        codigo = self.codigo_patrimonial or "Sem código"
        empresa = self.empresa_contratante.nome_fantasia if self.empresa_contratante else "—"
        return f"{self.nome} ({codigo}) - {empresa}"


class EquipamentoSetor(models.Model):
    """
    Relacionamento entre equipamentos e setores de eventos
    """
    setor = models.ForeignKey(SetorEvento, on_delete=models.CASCADE, related_name="equipamentos_setor")
    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE, related_name="setores_utilizacao")
    quantidade_necessaria = models.PositiveIntegerField(default=1)
    quantidade_disponivel = models.PositiveIntegerField(default=0)
    observacoes = models.TextField(blank=True, null=True)
    data_inicio_uso = models.DateTimeField(blank=True, null=True)
    data_fim_uso = models.DateTimeField(blank=True, null=True)
    responsavel_equipamento = models.ForeignKey(
        'Freelance',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="equipamentos_responsavel"
    )
    status = models.CharField(max_length=20, choices=[
        ('disponivel', 'Disponível'),
        ('em_uso', 'Em Uso'),
        ('manutencao', 'Em Manutenção'),
        ('indisponivel', 'Indisponível'),
    ], default='disponivel', db_index=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    def clean(self):
        """Validação personalizada para garantir que equipamento e setor sejam da mesma empresa"""
        from django.core.exceptions import ValidationError
        
        if self.equipamento and self.setor:
            # Verifica se o equipamento pertence à mesma empresa contratante do evento do setor
            empresa_equipamento = self.equipamento.empresa_contratante
            empresa_evento = self.setor.evento.empresa_contratante
            
            if empresa_equipamento != empresa_evento:
                codigo = self.equipamento.codigo_patrimonial or "Sem código"
                raise ValidationError({
                    'equipamento': f'O equipamento "{codigo}" pertence à empresa "{empresa_equipamento.nome_fantasia}", mas o setor pertence ao evento da empresa "{empresa_evento.nome_fantasia}". Só é possível associar equipamentos da mesma empresa.'
                })
    
    def save(self, *args, **kwargs):
        """Executa validação antes de salvar"""
        self.clean()
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Equipamento do Setor"
        verbose_name_plural = "Equipamentos do Setor"
        constraints = [
            models.UniqueConstraint(fields=['setor', 'equipamento'], name='uniq_equipamento_por_setor')
        ]
    
    def __str__(self):
        codigo = self.equipamento.codigo_patrimonial or "Sem código"
        return f"{codigo} - {self.setor.nome} ({self.quantidade_necessaria})"
    
    @property
    def quantidade_faltante(self):
        """Retorna a quantidade que ainda falta para completar o necessário"""
        return max(0, self.quantidade_necessaria - self.quantidade_disponivel)
    
    @property
    def percentual_cobertura(self):
        """Retorna o percentual de cobertura do equipamento no setor"""
        if self.quantidade_necessaria == 0:
            return 100
        return min(100, (self.quantidade_disponivel / self.quantidade_necessaria) * 100)


class ManutencaoEquipamento(models.Model):
    """
    Registro de manutenções realizadas nos equipamentos
    """
    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE, related_name="manutencoes")
    tipo_manutencao = models.CharField(max_length=20, choices=[
        ('preventiva', 'Preventiva'),
        ('corretiva', 'Corretiva'),
        ('calibracao', 'Calibração'),
    ])
    descricao = models.TextField()
    data_inicio = models.DateField()
    data_fim = models.DateField(blank=True, null=True)
    custo = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fornecedor = models.CharField(max_length=200, blank=True, null=True)
    responsavel = models.ForeignKey(
        'Freelance',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="manutencoes_realizadas"
    )
    status = models.CharField(max_length=20, choices=[
        ('agendada', 'Agendada'),
        ('em_andamento', 'Em Andamento'),
        ('concluida', 'Concluída'),
        ('cancelada', 'Cancelada'),
    ], default='agendada', db_index=True)
    observacoes = models.TextField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Manutenção de Equipamento"
        verbose_name_plural = "Manutenções de Equipamentos"
    
    def __str__(self):
        codigo = self.equipamento.codigo_patrimonial or "Sem código"
        return f"{codigo} - {self.tipo_manutencao} ({self.status})"


class TipoFuncao(models.Model):
    nome = models.CharField(max_length=80, unique=True)
    descricao = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tipo de Função"
        verbose_name_plural = "Tipos de Função"

    def __str__(self):
        return self.nome


class Funcao(models.Model):
    tipo_funcao = models.ForeignKey(TipoFuncao, on_delete=models.CASCADE, related_name="funcoes")
    nome = models.CharField(max_length=80)
    descricao = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nome} ({self.tipo_funcao.nome})"


class Vaga(models.Model):
    setor = models.ForeignKey(SetorEvento, on_delete=models.CASCADE, related_name="vagas")
    titulo = models.CharField(max_length=100)
    funcao = models.ForeignKey(Funcao, on_delete=models.CASCADE, related_name="vagas", verbose_name="Função", null=True, blank=True)
    quantidade = models.PositiveIntegerField()
    remuneracao = models.DecimalField(max_digits=10, decimal_places=2)
    descricao = models.TextField(blank=True, null=True)
    ativa = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.titulo} ({self.setor.evento.nome})"


class Freelance(models.Model):
    VINCULO_CHOICES = [
        ('intermitente', 'Intermitente'),
        ('freelancer', 'Freelancer'),
    ]
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('O', 'Outro'),
    ]
    ESTADO_CIVIL_CHOICES = [
        ('solteiro', 'Solteiro(a)'),
        ('casado', 'Casado(a)'),
        ('divorciado', 'Divorciado(a)'),
        ('viuvo', 'Viúvo(a)'),
    ]
    TIPO_CONTA_CHOICES = [
        ('corrente', 'Conta Corrente'),
        ('poupanca', 'Poupança'),
        ('pix', 'PIX'),
    ]
    RESULTADO_EXAME_CHOICES = [
        ('apto', 'Apto'),
        ('inapto', 'Inapto'),
    ]

    # Relacionamento com usuário
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Dados pessoais
    nome_completo = models.CharField(max_length=255)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    documento = models.CharField(max_length=50, blank=True, null=True)
    habilidades = models.TextField(blank=True, null=True)

    cpf = models.CharField(max_length=14, unique=True, blank=True, null=True)
    rg = models.CharField(max_length=20, blank=True, null=True)
    orgao_expedidor = models.CharField(max_length=20, blank=True, null=True)
    uf_rg = models.CharField(max_length=2, blank=True, null=True)
    data_nascimento = models.DateField(blank=True, null=True)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, blank=True, null=True)
    estado_civil = models.CharField(max_length=20, choices=ESTADO_CIVIL_CHOICES, blank=True, null=True)
    nacionalidade = models.CharField(max_length=50, default='Brasileira', blank=True, null=True)
    naturalidade = models.CharField(max_length=100, blank=True, null=True)
    nome_mae = models.CharField(max_length=255, blank=True, null=True)
    nome_pai = models.CharField(max_length=255, blank=True, null=True)
    foto = models.ImageField(upload_to='freelancers/fotos/', blank=True, null=True)

    # Endereço
    cep = models.CharField(max_length=9, blank=True, null=True)
    logradouro = models.CharField(max_length=255, blank=True, null=True)
    numero = models.CharField(max_length=10, blank=True, null=True)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    uf = models.CharField(max_length=2, blank=True, null=True)

    # Documentos extras
    pis_pasep = models.CharField(max_length=20, blank=True, null=True)
    carteira_trabalho_numero = models.CharField(max_length=20, blank=True, null=True)
    carteira_trabalho_serie = models.CharField(max_length=10, blank=True, null=True)
    titulo_eleitor = models.CharField(max_length=20, blank=True, null=True)
    cnh_numero = models.CharField(max_length=20, blank=True, null=True)
    cnh_categoria = models.CharField(max_length=5, blank=True, null=True)
    certificado_reservista = models.CharField(max_length=20, blank=True, null=True)

    # Dados Bancários
    banco = models.CharField(max_length=100, blank=True, null=True)
    agencia = models.CharField(max_length=10, blank=True, null=True)
    conta = models.CharField(max_length=20, blank=True, null=True)
    tipo_conta = models.CharField(max_length=20, choices=TIPO_CONTA_CHOICES, blank=True, null=True)
    chave_pix = models.CharField(max_length=100, blank=True, null=True)

    # Arquivos obrigatórios
    arquivo_exame_medico = models.FileField(upload_to='freelancers/documentos/exame_medico/', blank=True, null=True)
    arquivo_comprovante_residencia = models.FileField(upload_to='freelancers/documentos/comprovante_residencia/', blank=True, null=True)
    arquivo_identidade_frente = models.ImageField(upload_to='freelancers/documentos/identidade/', blank=True, null=True)
    arquivo_identidade_verso = models.ImageField(upload_to='freelancers/documentos/identidade/', blank=True, null=True)

    # Observações
    observacoes = models.TextField(blank=True, null=True)
    observacoes_medicas = models.TextField(blank=True, null=True)

    atualizado_em = models.DateTimeField(auto_now=True)
    cadastro_completo = models.BooleanField(default=False)
    
    def verificar_cadastro_completo(self):
        """
        Verifica se o cadastro tem todos os documentos obrigatórios e marca como completo.
        """
        if (
            self.arquivo_exame_medico and
            self.arquivo_comprovante_residencia and
            self.arquivo_identidade_frente and
            self.arquivo_identidade_verso
        ):
            self.cadastro_completo = True
            self.save()
        else:
            self.cadastro_completo = False
            self.save()

    def __str__(self):
        return self.nome_completo


class Candidatura(models.Model):
    """
    Pré-cadastro de um freelance para uma vaga.
    """
    freelance = models.ForeignKey(
        Freelance,
        on_delete=models.CASCADE,
        related_name='candidaturas_pendentes'
    )
    vaga = models.ForeignKey(
        'Vaga',
        on_delete=models.CASCADE,
        related_name='candidaturas'
    )
    data_candidatura = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado'),
        ('rejeitado', 'Rejeitado'),
    ], default='pendente')

    def __str__(self):
        return f"{self.freelance} → {self.vaga} ({self.status})"


class ContratoFreelance(models.Model):
    """
    Registro de um freelance já aprovado para uma vaga.
    """
    freelance = models.ForeignKey(
        Freelance,
        on_delete=models.CASCADE,
        related_name='contratacoes'
    )
    vaga = models.ForeignKey(
        'Vaga',
        on_delete=models.CASCADE,
        related_name='freelances_contratados'
    )
    data_contratacao = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('ativo', 'Ativo'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
    ], default='ativo')

    def __str__(self):
        return f"{self.freelance} contratado para {self.vaga} ({self.status})"


# ========== MODELOS DE COMUNICAÇÃO E MENSAGENS ==========

class CanalComunicacao(models.Model):
    """
    Canais de comunicação disponíveis no sistema
    """
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="canais_comunicacao",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=[
        ('email', 'E-mail'),
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
        ('push', 'Push Notification'),
        ('interno', 'Sistema Interno'),
    ])
    ativo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Canal de Comunicação"
        verbose_name_plural = "Canais de Comunicação"
        constraints = [
            models.UniqueConstraint(fields=['empresa_contratante', 'nome'], name='uniq_canal_comunicacao_por_tenant')
        ]
    
    def __str__(self):
        empresa = self.empresa_contratante.nome_fantasia if self.empresa_contratante else "—"
        return f"{self.nome} - {empresa}"


class Mensagem(models.Model):
    """
    Mensagens enviadas através dos canais de comunicação
    """
    PRIORIDADE_CHOICES = [
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]
    
    STATUS_CHOICES = [
        ('rascunho', 'Rascunho'),
        ('enviada', 'Enviada'),
        ('entregue', 'Entregue'),
        ('lida', 'Lida'),
        ('falha', 'Falha no Envio'),
    ]
    
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="mensagens",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    remetente = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="mensagens_enviadas"
    )
    destinatarios = models.ManyToManyField(
        User,
        related_name="mensagens_recebidas"
    )
    canal = models.ForeignKey(
        CanalComunicacao,
        on_delete=models.CASCADE,
        related_name="mensagens"
    )
    assunto = models.CharField(max_length=200)
    conteudo = models.TextField()
    prioridade = models.CharField(max_length=20, choices=PRIORIDADE_CHOICES, default='media')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='rascunho')
    data_envio = models.DateTimeField(null=True, blank=True)
    data_leitura = models.DateTimeField(null=True, blank=True)
    anexos = models.FileField(upload_to='mensagens/anexos/', blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Mensagem"
        verbose_name_plural = "Mensagens"
        ordering = ['-criado_em']
    
    def __str__(self):
        return f"{self.assunto} - {self.remetente.username}"


# ========== MODELOS DE CHECKLISTS E TAREFAS ==========

class ChecklistEvento(models.Model):
    """
    Checklists para organização de eventos
    """
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="checklists_eventos",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name="checklists"
    )
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)
    responsavel = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="checklists_responsavel"
    )
    data_limite = models.DateTimeField(null=True, blank=True)
    concluido = models.BooleanField(default=False)
    data_conclusao = models.DateTimeField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Checklist de Evento"
        verbose_name_plural = "Checklists de Eventos"
    
    def __str__(self):
        return f"{self.titulo} - {self.evento.nome}"


class ItemChecklist(models.Model):
    """
    Itens individuais de um checklist
    """
    checklist = models.ForeignKey(
        ChecklistEvento,
        on_delete=models.CASCADE,
        related_name="itens"
    )
    descricao = models.CharField(max_length=500)
    ordem = models.PositiveIntegerField(default=0)
    responsavel = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="itens_checklist_responsavel",
        null=True,
        blank=True
    )
    concluido = models.BooleanField(default=False)
    data_conclusao = models.DateTimeField(null=True, blank=True)
    observacoes = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Item do Checklist"
        verbose_name_plural = "Itens do Checklist"
        ordering = ['ordem']
    
    def __str__(self):
        return f"{self.descricao} - {self.checklist.titulo}"


class Tarefa(models.Model):
    """
    Tarefas gerais do sistema
    """
    PRIORIDADE_CHOICES = [
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]
    
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('em_andamento', 'Em Andamento'),
        ('concluida', 'Concluída'),
        ('cancelada', 'Cancelada'),
    ]
    
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="tarefas",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    responsavel = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="tarefas_responsavel"
    )
    criado_por = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="tarefas_criadas"
    )
    prioridade = models.CharField(max_length=20, choices=PRIORIDADE_CHOICES, default='media')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_limite = models.DateTimeField(null=True, blank=True)
    data_conclusao = models.DateTimeField(null=True, blank=True)
    evento_relacionado = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name="tarefas",
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = "Tarefa"
        verbose_name_plural = "Tarefas"
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"{self.titulo} - {self.responsavel.username}"


# ========== MODELOS DE TEMPLATES E DOCUMENTOS ==========

class TemplateDocumento(models.Model):
    """
    Templates de documentos reutilizáveis
    """
    TIPO_DOCUMENTO_CHOICES = [
        ('contrato', 'Contrato'),
        ('termo_compromisso', 'Termo de Compromisso'),
        ('checklist', 'Checklist'),
        ('relatorio', 'Relatório'),
        ('email', 'E-mail'),
        ('sms', 'SMS'),
        ('outro', 'Outro'),
    ]
    
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="templates_documentos",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    nome = models.CharField(max_length=200)
    tipo_documento = models.CharField(max_length=20, choices=TIPO_DOCUMENTO_CHOICES)
    descricao = models.TextField(blank=True, null=True)
    conteudo = models.TextField()
    variaveis = models.JSONField(default=dict, help_text="Variáveis disponíveis no template")
    ativo = models.BooleanField(default=True)
    criado_por = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="templates_criados"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Template de Documento"
        verbose_name_plural = "Templates de Documentos"
        constraints = [
            models.UniqueConstraint(fields=['empresa_contratante', 'nome'], name='uniq_template_documento_por_tenant')
        ]
    
    def __str__(self):
        empresa = self.empresa_contratante.nome_fantasia if self.empresa_contratante else "—"
        return f"{self.nome} - {empresa}"


class DocumentoGerado(models.Model):
    """
    Documentos gerados a partir de templates
    """
    template = models.ForeignKey(
        TemplateDocumento,
        on_delete=models.CASCADE,
        related_name="documentos_gerados"
    )
    titulo = models.CharField(max_length=200)
    conteudo = models.TextField()
    arquivo = models.FileField(upload_to='documentos/gerados/', blank=True, null=True)
    variaveis_utilizadas = models.JSONField(default=dict)
    gerado_por = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="documentos_gerados"
    )
    evento_relacionado = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name="documentos",
        null=True,
        blank=True
    )
    data_geracao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Documento Gerado"
        verbose_name_plural = "Documentos Gerados"
    
    def __str__(self):
        return f"{self.titulo} - {self.template.nome}"


# ========== MODELOS DE INTEGRAÇÕES E APIs ==========

class IntegracaoAPI(models.Model):
    """
    Configurações de integrações com APIs externas
    """
    TIPO_INTEGRACAO_CHOICES = [
        ('pagamento', 'Pagamento'),
        ('email', 'E-mail'),
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
        ('calendario', 'Calendário'),
        ('outro', 'Outro'),
    ]
    
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="integracoes_api",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    nome = models.CharField(max_length=200)
    tipo_integracao = models.CharField(max_length=20, choices=TIPO_INTEGRACAO_CHOICES)
    url_base = models.URLField()
    api_key = models.CharField(max_length=500, blank=True, null=True)
    api_secret = models.CharField(max_length=500, blank=True, null=True)
    configuracoes = models.JSONField(default=dict)
    ativo = models.BooleanField(default=True)
    ultima_sincronizacao = models.DateTimeField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Integração de API"
        verbose_name_plural = "Integrações de API"
        constraints = [
            models.UniqueConstraint(fields=['empresa_contratante', 'nome'], name='uniq_integracao_api_por_tenant')
        ]
    
    def __str__(self):
        empresa = self.empresa_contratante.nome_fantasia if self.empresa_contratante else "—"
        return f"{self.nome} - {empresa}"


class LogIntegracao(models.Model):
    """
    Logs de integrações com APIs externas
    """
    STATUS_CHOICES = [
        ('sucesso', 'Sucesso'),
        ('erro', 'Erro'),
        ('pendente', 'Pendente'),
    ]
    
    integracao = models.ForeignKey(
        IntegracaoAPI,
        on_delete=models.CASCADE,
        related_name="logs"
    )
    acao = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    dados_enviados = models.JSONField(default=dict)
    resposta_recebida = models.JSONField(default=dict)
    erro = models.TextField(blank=True, null=True)
    tempo_resposta = models.FloatField(null=True, blank=True)
    data_hora = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Log de Integração"
        verbose_name_plural = "Logs de Integração"
        ordering = ['-data_hora']
    
    def __str__(self):
        return f"{self.integracao.nome} - {self.acao} - {self.status}"


# ========== MODELOS DE BACKUP E VERSIONAMENTO ==========

class BackupSistema(models.Model):
    """
    Registro de backups do sistema
    """
    TIPO_BACKUP_CHOICES = [
        ('completo', 'Completo'),
        ('incremental', 'Incremental'),
        ('diferencial', 'Diferencial'),
    ]
    
    STATUS_CHOICES = [
        ('em_andamento', 'Em Andamento'),
        ('concluido', 'Concluído'),
        ('falha', 'Falha'),
    ]
    
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="backups",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    tipo_backup = models.CharField(max_length=20, choices=TIPO_BACKUP_CHOICES)
    arquivo_backup = models.FileField(upload_to='backups/')
    tamanho_arquivo = models.BigIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='em_andamento')
    data_inicio = models.DateTimeField(auto_now_add=True)
    data_conclusao = models.DateTimeField(null=True, blank=True)
    observacoes = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Backup do Sistema"
        verbose_name_plural = "Backups do Sistema"
        ordering = ['-data_inicio']
    
    def __str__(self):
        empresa = self.empresa_contratante.nome_fantasia if self.empresa_contratante else "—"
        return f"Backup {self.tipo_backup} - {empresa} - {self.data_inicio}"


class VersaoSistema(models.Model):
    """
    Controle de versões do sistema
    """
    numero_versao = models.CharField(max_length=20, unique=True)
    nome_versao = models.CharField(max_length=100)
    data_lancamento = models.DateField()
    descricao = models.TextField()
    mudancas = models.JSONField(default=list)
    ativo = models.BooleanField(default=True)
    obrigatorio = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Versão do Sistema"
        verbose_name_plural = "Versões do Sistema"
        ordering = ['-data_lancamento']
    
    def __str__(self):
        return f"{self.numero_versao} - {self.nome_versao}"


# ========== MODELOS DE ESTOQUE E INSUMOS ==========

class CategoriaInsumo(models.Model):
    """
    Categorias de insumos (ex: Alimentação, Bebidas, Material de Limpeza, etc.)
    """
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="categorias_insumos",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Categoria de Insumo"
        verbose_name_plural = "Categorias de Insumos"
        constraints = [
            models.UniqueConstraint(fields=['empresa_contratante', 'nome'], name='uniq_categoria_insumo_por_tenant')
        ]
    
    def __str__(self):
        empresa = self.empresa_contratante.nome_fantasia if self.empresa_contratante else "—"
        return f"{self.nome} - {empresa}"


class Insumo(models.Model):
    """
    Insumos que podem ser utilizados nos setores dos eventos
    """
    UNIDADE_CHOICES = [
        ('unidade', 'Unidade'),
        ('kg', 'Quilograma'),
        ('l', 'Litro'),
        ('m', 'Metro'),
        ('m2', 'Metro Quadrado'),
        ('m3', 'Metro Cúbico'),
        ('caixa', 'Caixa'),
        ('pacote', 'Pacote'),
        ('fardo', 'Fardo'),
        ('outro', 'Outro'),
    ]
    
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="insumos",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    empresa_fornecedora = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name="insumos_fornecidos",
        verbose_name="Empresa Fornecedora"
    )
    codigo = models.CharField(max_length=50, verbose_name="Código do Insumo", blank=True, null=True, db_index=True)
    categoria = models.ForeignKey(CategoriaInsumo, on_delete=models.CASCADE, related_name="insumos")
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)
    especificacoes = models.TextField(blank=True, null=True)
    unidade_medida = models.CharField(max_length=20, choices=UNIDADE_CHOICES, default='unidade')
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    estoque_minimo = models.PositiveIntegerField(default=0, verbose_name="Estoque Mínimo")
    estoque_atual = models.PositiveIntegerField(default=0, verbose_name="Estoque Atual")
    local_armazenamento = models.CharField(max_length=200, blank=True, null=True)
    data_validade = models.DateField(blank=True, null=True)
    foto = models.ImageField(upload_to='insumos/fotos/', blank=True, null=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Insumo"
        verbose_name_plural = "Insumos"
    
    def __str__(self):
        codigo = self.codigo or "Sem código"
        empresa = self.empresa_contratante.nome_fantasia if self.empresa_contratante else "—"
        return f"{codigo} - {self.nome} ({empresa})"
    
    @property
    def estoque_disponivel(self):
        """Retorna o estoque disponível (atual - mínimo)"""
        return max(0, self.estoque_atual - self.estoque_minimo)
    
    @property
    def precisa_reposicao(self):
        """Verifica se precisa de reposição"""
        return self.estoque_atual <= self.estoque_minimo
    
    def alocar_para_evento(self, evento, quantidade, responsavel=None):
        """
        Aloca uma quantidade do estoque geral para um evento específico.
        Cria ou atualiza o InsumoEvento correspondente.
        """
        if quantidade > self.estoque_disponivel:
            return False, "Estoque insuficiente"
        
        insumo_evento, created = InsumoEvento.objects.get_or_create(
            evento=evento,
            insumo=self,
            defaults={
                'quantidade_alocada_evento': quantidade,
                'responsavel_alocacao': responsavel
            }
        )
        
        if not created:
            insumo_evento.quantidade_alocada_evento += quantidade
            insumo_evento.responsavel_alocacao = responsavel
        
        insumo_evento.save()
        return True, insumo_evento
    
    def get_quantidade_alocada_eventos(self):
        """Retorna a quantidade total alocada para todos os eventos"""
        return sum(
            ie.quantidade_alocada_evento 
            for ie in self.eventos_utilizacao.all()
        )
    
    def get_quantidade_utilizada_eventos(self):
        """Retorna a quantidade total utilizada em todos os eventos"""
        return sum(
            ie.quantidade_utilizada_evento 
            for ie in self.eventos_utilizacao.all()
        )
    
    @property
    def estoque_real_disponivel(self):
        """Retorna o estoque realmente disponível (considerando alocações para eventos)"""
        return max(0, self.estoque_disponivel - self.get_quantidade_alocada_eventos())


class InsumoEvento(models.Model):
    """
    Alocação de insumos para um evento específico.
    Gerencia o estoque do evento como um todo antes da distribuição pelos setores.
    """
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name="insumos_evento")
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE, related_name="eventos_utilizacao")
    quantidade_total_necessaria = models.PositiveIntegerField(default=0, verbose_name="Quantidade Total Necessária")
    quantidade_alocada_evento = models.PositiveIntegerField(default=0, verbose_name="Quantidade Alocada para o Evento")
    quantidade_distribuida_setores = models.PositiveIntegerField(default=0, verbose_name="Quantidade Distribuída pelos Setores")
    quantidade_utilizada_evento = models.PositiveIntegerField(default=0, verbose_name="Quantidade Utilizada no Evento")
    data_alocacao = models.DateTimeField(auto_now_add=True)
    responsavel_alocacao = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="insumos_alocados"
    )
    observacoes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=[
        ('pendente', 'Pendente'),
        ('alocado', 'Alocado'),
        ('em_distribuicao', 'Em Distribuição'),
        ('distribuido', 'Distribuído'),
        ('em_uso', 'Em Uso'),
        ('finalizado', 'Finalizado'),
        ('insuficiente', 'Insufficiente'),
    ], default='pendente')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Insumo do Evento"
        verbose_name_plural = "Insumos do Evento"
        constraints = [
            models.UniqueConstraint(fields=['evento', 'insumo'], name='uniq_insumo_por_evento')
        ]
    
    def __str__(self):
        codigo = self.insumo.codigo or "Sem código"
        return f"{codigo} - {self.evento.nome} ({self.quantidade_total_necessaria})"
    
    @property
    def quantidade_disponivel_distribuicao(self):
        """Retorna a quantidade disponível para distribuição pelos setores"""
        return max(0, self.quantidade_alocada_evento - self.quantidade_distribuida_setores)
    
    @property
    def quantidade_nao_utilizada(self):
        """Retorna a quantidade que não foi utilizada no evento"""
        return max(0, self.quantidade_distribuida_setores - self.quantidade_utilizada_evento)
    
    @property
    def percentual_utilizacao(self):
        """Retorna o percentual de utilização do insumo no evento"""
        if self.quantidade_distribuida_setores == 0:
            return 0
        return (self.quantidade_utilizada_evento / self.quantidade_distribuida_setores) * 100
    
    def calcular_quantidade_total_necessaria(self):
        """Calcula a quantidade total necessária baseada na soma dos setores"""
        total = sum(
            insumo_setor.quantidade_necessaria 
            for insumo_setor in self.insumo.setores_utilizacao.filter(setor__evento=self.evento)
        )
        self.quantidade_total_necessaria = total
        self.save()
        return total


class InsumoSetor(models.Model):
    """
    Relacionamento entre insumos e setores de eventos.
    Agora consome do estoque alocado para o evento (InsumoEvento).
    """
    setor = models.ForeignKey(SetorEvento, on_delete=models.CASCADE, related_name="insumos_setor")
    insumo_evento = models.ForeignKey(InsumoEvento, on_delete=models.CASCADE, related_name="setores_distribuicao")
    quantidade_necessaria = models.PositiveIntegerField(default=1)
    quantidade_alocada = models.PositiveIntegerField(default=0)
    quantidade_transportada = models.PositiveIntegerField(default=0)
    quantidade_utilizada = models.PositiveIntegerField(default=0, verbose_name="Quantidade Utilizada no Setor")
    observacoes = models.TextField(blank=True, null=True)
    data_necessidade = models.DateTimeField(blank=True, null=True)
    responsavel_insumo = models.ForeignKey(
        'Freelance',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="insumos_responsavel"
    )
    status = models.CharField(max_length=20, choices=[
        ('pendente', 'Pendente'),
        ('alocado', 'Alocado'),
        ('em_transporte', 'Em Transporte'),
        ('entregue', 'Entregue'),
        ('em_uso', 'Em Uso'),
        ('finalizado', 'Finalizado'),
        ('insuficiente', 'Insufficiente'),
    ], default='pendente')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Insumo do Setor"
        verbose_name_plural = "Insumos do Setor"
        constraints = [
            models.UniqueConstraint(fields=['setor', 'insumo_evento'], name='uniq_insumo_evento_por_setor')
        ]
    
    def __str__(self):
        codigo = self.insumo_evento.insumo.codigo or "Sem código"
        return f"{codigo} - {self.setor.nome} ({self.quantidade_necessaria})"
    
    @property
    def quantidade_faltante(self):
        """Retorna a quantidade que ainda falta para completar o necessário"""
        return max(0, self.quantidade_necessaria - self.quantidade_alocada)
    
    @property
    def quantidade_nao_utilizada(self):
        """Retorna a quantidade que não foi utilizada no setor"""
        return max(0, self.quantidade_alocada - self.quantidade_utilizada)
    
    def alocar_quantidade(self, quantidade):
        """Aloca uma quantidade do estoque do evento para este setor"""
        if quantidade <= self.insumo_evento.quantidade_disponivel_distribuicao:
            self.quantidade_alocada += quantidade
            self.insumo_evento.quantidade_distribuida_setores += quantidade
            self.insumo_evento.save()
            self.save()
            return True
        return False
    
    def registrar_utilizacao(self, quantidade):
        """Registra a utilização de uma quantidade no setor"""
        if quantidade <= self.quantidade_alocada:
            self.quantidade_utilizada += quantidade
            self.insumo_evento.quantidade_utilizada_evento += quantidade
            self.insumo_evento.save()
            self.save()
            return True
        return False
    
    @property
    def quantidade_transporte_pendente(self):
        """Retorna a quantidade que ainda precisa ser transportada"""
        return max(0, self.quantidade_alocada - self.quantidade_transportada)
    
    @property
    def percentual_cobertura(self):
        """Retorna o percentual de cobertura do insumo no setor"""
        if self.quantidade_necessaria == 0:
            return 100
        return min(100, (self.quantidade_alocada / self.quantidade_necessaria) * 100)


# ========== MODELOS DE PLANEJAMENTO DE TRANSPORTE ==========

class TipoVeiculo(models.Model):
    """
    Tipos de veículos disponíveis para transporte
    """
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="tipos_veiculos",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    capacidade_carga = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Capacidade de Carga (kg)")
    capacidade_volume = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Capacidade de Volume (m³)")
    ativo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Tipo de Veículo"
        verbose_name_plural = "Tipos de Veículos"
        constraints = [
            models.UniqueConstraint(fields=['empresa_contratante', 'nome'], name='uniq_tipo_veiculo_por_tenant')
        ]
    
    def __str__(self):
        empresa = self.empresa_contratante.nome_fantasia if self.empresa_contratante else "—"
        return f"{self.nome} - {empresa}"


class Veiculo(models.Model):
    """
    Veículos disponíveis para transporte
    """
    STATUS_CHOICES = [
        ('disponivel', 'Disponível'),
        ('em_uso', 'Em Uso'),
        ('manutencao', 'Em Manutenção'),
        ('indisponivel', 'Indisponível'),
    ]
    
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="veiculos",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    empresa_proprietaria = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name="veiculos",
        verbose_name="Empresa Proprietária"
    )
    tipo_veiculo = models.ForeignKey(TipoVeiculo, on_delete=models.CASCADE, related_name="veiculos")
    placa = models.CharField(max_length=10, unique=True)
    modelo = models.CharField(max_length=100)
    ano = models.PositiveIntegerField()
    cor = models.CharField(max_length=50)
    motorista_responsavel = models.ForeignKey(
        'Freelance',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="veiculos_responsavel"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='disponivel')
    observacoes = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Veículo"
        verbose_name_plural = "Veículos"
    
    def __str__(self):
        empresa = self.empresa_contratante.nome_fantasia if self.empresa_contratante else "—"
        return f"{self.placa} - {self.modelo} ({empresa})"


class RotaTransporte(models.Model):
    """
    Rotas de transporte para eventos
    """
    STATUS_CHOICES = [
        ('planejada', 'Planejada'),
        ('em_andamento', 'Em Andamento'),
        ('concluida', 'Concluída'),
        ('cancelada', 'Cancelada'),
    ]
    
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="rotas_transporte",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name="rotas_transporte")
    nome_rota = models.CharField(max_length=200)
    origem = models.CharField(max_length=200)
    destino = models.CharField(max_length=200)
    veiculo = models.ForeignKey(Veiculo, on_delete=models.CASCADE, related_name="rotas")
    motorista = models.ForeignKey(
        'Freelance',
        on_delete=models.CASCADE,
        related_name="rotas_motorista"
    )
    data_saida = models.DateTimeField()
    data_chegada_prevista = models.DateTimeField()
    data_chegada_real = models.DateTimeField(null=True, blank=True)
    distancia_km = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    custo_combustivel = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    custo_pedagio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planejada')
    observacoes = models.TextField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Rota de Transporte"
        verbose_name_plural = "Rotas de Transporte"
    
    def __str__(self):
        return f"{self.nome_rota} - {self.evento.nome} ({self.status})"
    
    @property
    def custo_total(self):
        """Calcula o custo total da rota"""
        combustivel = self.custo_combustivel or 0
        pedagio = self.custo_pedagio or 0
        return combustivel + pedagio


class ItemTransporte(models.Model):
    """
    Itens transportados em uma rota
    """
    TIPO_ITEM_CHOICES = [
        ('equipamento', 'Equipamento'),
        ('insumo', 'Insumo'),
        ('outro', 'Outro'),
    ]
    
    rota = models.ForeignKey(RotaTransporte, on_delete=models.CASCADE, related_name="itens_transporte")
    tipo_item = models.CharField(max_length=20, choices=TIPO_ITEM_CHOICES)
    equipamento = models.ForeignKey(
        Equipamento,
        on_delete=models.CASCADE,
        related_name="transportes",
        null=True,
        blank=True
    )
    insumo = models.ForeignKey(
        Insumo,
        on_delete=models.CASCADE,
        related_name="transportes",
        null=True,
        blank=True
    )
    quantidade = models.PositiveIntegerField(default=1)
    peso_unitario = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    volume_unitario = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    setor_destino = models.ForeignKey(SetorEvento, on_delete=models.CASCADE, related_name="itens_recebidos")
    observacoes = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Item de Transporte"
        verbose_name_plural = "Itens de Transporte"
    
    def __str__(self):
        if self.equipamento:
            return f"{self.equipamento.codigo_patrimonial} - {self.setor_destino.nome}"
        elif self.insumo:
            return f"{self.insumo.nome} - {self.setor_destino.nome}"
        return f"Item - {self.setor_destino.nome}"
    
    @property
    def peso_total(self):
        """Calcula o peso total do item"""
        if self.peso_unitario:
            return self.peso_unitario * self.quantidade
        return 0
    
    @property
    def volume_total(self):
        """Calcula o volume total do item"""
        if self.volume_unitario:
            return self.volume_unitario * self.quantidade
        return 0


# ========== MODELOS MELHORADOS DE CONTROLE DE EQUIPAMENTOS ==========

class StatusEquipamento(models.Model):
    """
    Status detalhados para equipamentos
    """
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="status_equipamentos",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    cor = models.CharField(max_length=7, default="#000000", help_text="Cor em hexadecimal")
    ativo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Status de Equipamento"
        verbose_name_plural = "Status de Equipamentos"
        constraints = [
            models.UniqueConstraint(fields=['empresa_contratante', 'nome'], name='uniq_status_equipamento_por_tenant')
        ]
    
    def __str__(self):
        empresa = self.empresa_contratante.nome_fantasia if self.empresa_contratante else "—"
        return f"{self.nome} - {empresa}"


class ControleEquipamento(models.Model):
    """
    Controle detalhado de equipamentos
    """
    TIPO_CONTROLE_CHOICES = [
        ('estoque', 'Controle de Estoque'),
        ('manutencao', 'Manutenção'),
        ('compra', 'Compra Necessária'),
        ('aluguel', 'Aluguel'),
        ('emprestimo', 'Empréstimo'),
        ('outro', 'Outro'),
    ]
    
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="controles_equipamentos",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE, related_name="controles")
    tipo_controle = models.CharField(max_length=20, choices=TIPO_CONTROLE_CHOICES)
    status_equipamento = models.ForeignKey(
        StatusEquipamento,
        on_delete=models.CASCADE,
        related_name="controles"
    )
    quantidade_atual = models.PositiveIntegerField(default=0)
    quantidade_necessaria = models.PositiveIntegerField(default=0)
    quantidade_em_manutencao = models.PositiveIntegerField(default=0)
    quantidade_para_comprar = models.PositiveIntegerField(default=0)
    quantidade_alugada = models.PositiveIntegerField(default=0)
    data_ultima_verificacao = models.DateTimeField(auto_now_add=True)
    proxima_verificacao = models.DateTimeField(blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)
    responsavel = models.ForeignKey(
        'Freelance',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="controles_equipamentos_responsavel"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Controle de Equipamento"
        verbose_name_plural = "Controles de Equipamentos"
        constraints = [
            models.UniqueConstraint(fields=['equipamento', 'tipo_controle'], name='uniq_controle_por_equipamento')
        ]
    
    def __str__(self):
        return f"{self.equipamento.codigo_patrimonial} - {self.tipo_controle} ({self.status_equipamento.nome})"
    
    @property
    def quantidade_disponivel(self):
        """Calcula quantidade disponível"""
        return max(0, self.quantidade_atual - self.quantidade_em_manutencao)
    
    @property
    def quantidade_faltante(self):
        """Calcula quantidade faltante"""
        return max(0, self.quantidade_necessaria - self.quantidade_disponivel)
    
    @property
    def percentual_cobertura(self):
        """Calcula percentual de cobertura"""
        if self.quantidade_necessaria == 0:
            return 100
        return min(100, (self.quantidade_disponivel / self.quantidade_necessaria) * 100)


class PedidoCompraEquipamento(models.Model):
    """
    Pedidos de compra de equipamentos
    """
    STATUS_CHOICES = [
        ('rascunho', 'Rascunho'),
        ('enviado', 'Enviado'),
        ('aprovado', 'Aprovado'),
        ('em_producao', 'Em Produção'),
        ('pronto_envio', 'Pronto para Envio'),
        ('enviado', 'Enviado'),
        ('recebido', 'Recebido'),
        ('cancelado', 'Cancelado'),
    ]
    
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="pedidos_compra_equipamentos",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    numero_pedido = models.CharField(max_length=50, unique=True)
    fornecedor = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="pedidos_fornecidos")
    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE, related_name="pedidos_compra")
    quantidade = models.PositiveIntegerField()
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    valor_total = models.DecimalField(max_digits=12, decimal_places=2)
    data_pedido = models.DateField(auto_now_add=True)
    data_entrega_prevista = models.DateField()
    data_entrega_real = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='rascunho')
    observacoes = models.TextField(blank=True, null=True)
    solicitante = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="pedidos_compra_solicitados"
    )
    aprovador = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pedidos_compra_aprovados"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Pedido de Compra de Equipamento"
        verbose_name_plural = "Pedidos de Compra de Equipamentos"
    
    def __str__(self):
        return f"Pedido {self.numero_pedido} - {self.equipamento.codigo_patrimonial}"
    
    def save(self, *args, **kwargs):
        """Calcula valor total automaticamente"""
        if self.quantidade and self.valor_unitario:
            self.valor_total = self.quantidade * self.valor_unitario
        super().save(*args, **kwargs)


class AluguelEquipamento(models.Model):
    """
    Controle de aluguel de equipamentos
    """
    STATUS_CHOICES = [
        ('solicitado', 'Solicitado'),
        ('aprovado', 'Aprovado'),
        ('em_uso', 'Em Uso'),
        ('devolvido', 'Devolvido'),
        ('cancelado', 'Cancelado'),
    ]
    
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="alugueis_equipamentos",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE, related_name="alugueis")
    fornecedor_aluguel = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="equipamentos_alugados")
    quantidade = models.PositiveIntegerField()
    valor_diario = models.DecimalField(max_digits=10, decimal_places=2)
    data_inicio = models.DateField()
    data_fim = models.DateField()
    data_devolucao = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='solicitado')
    valor_total = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)
    solicitante = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="alugueis_solicitados"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Aluguel de Equipamento"
        verbose_name_plural = "Aluguéis de Equipamentos"
    
    def __str__(self):
        return f"Aluguel {self.equipamento.codigo_patrimonial} - {self.fornecedor_aluguel.nome}"
    
    @property
    def dias_aluguel(self):
        """Calcula quantidade de dias do aluguel"""
        from datetime import date
        if self.data_fim and self.data_inicio:
            return (self.data_fim - self.data_inicio).days
        return 0
    
    @property
    def valor_calculado(self):
        """Calcula valor total do aluguel"""
        if self.valor_diario and self.dias_aluguel:
            return self.valor_diario * self.dias_aluguel * self.quantidade
        return 0


# ========== MODELOS DE RELATÓRIOS DE ESTOQUE E TRANSPORTE ==========

class RelatorioEstoque(models.Model):
    """
    Relatórios de estoque e controle de materiais
    """
    TIPO_RELATORIO_CHOICES = [
        ('estoque_geral', 'Estoque Geral'),
        ('estoque_baixo', 'Estoque Baixo'),
        ('validade', 'Controle de Validade'),
        ('transporte', 'Relatório de Transporte'),
        ('equipamentos', 'Status de Equipamentos'),
        ('compras', 'Pedidos de Compra'),
        ('alugueis', 'Aluguéis'),
    ]
    
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="relatorios_estoque",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name="relatorios_estoque",
        null=True,
        blank=True
    )
    tipo_relatorio = models.CharField(max_length=20, choices=TIPO_RELATORIO_CHOICES)
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)
    dados_relatorio = models.JSONField(default=dict)
    arquivo = models.FileField(upload_to='relatorios/estoque/', blank=True, null=True)
    gerado_por = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="relatorios_estoque_gerados"
    )
    data_geracao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Relatório de Estoque"
        verbose_name_plural = "Relatórios de Estoque"
    
    def __str__(self):
        empresa = self.empresa_contratante.nome_fantasia if self.empresa_contratante else "—"
        return f"{self.titulo} - {empresa}"


class DashboardEstoque(models.Model):
    """
    Dashboard com métricas de estoque e transporte
    """
    empresa_contratante = models.OneToOneField(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="dashboard_estoque"
    )
    total_equipamentos = models.PositiveIntegerField(default=0)
    equipamentos_disponiveis = models.PositiveIntegerField(default=0)
    equipamentos_manutencao = models.PositiveIntegerField(default=0)
    equipamentos_alugados = models.PositiveIntegerField(default=0)
    total_insumos = models.PositiveIntegerField(default=0)
    insumos_estoque_baixo = models.PositiveIntegerField(default=0)
    insumos_vencendo = models.PositiveIntegerField(default=0)
    rotas_transporte_ativas = models.PositiveIntegerField(default=0)
    veiculos_disponiveis = models.PositiveIntegerField(default=0)
    pedidos_compra_pendentes = models.PositiveIntegerField(default=0)
    alugueis_ativos = models.PositiveIntegerField(default=0)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Dashboard de Estoque"
        verbose_name_plural = "Dashboards de Estoque"
    
    def __str__(self):
        empresa = self.empresa_contratante.nome_fantasia if self.empresa_contratante else "—"
        return f"Dashboard - {empresa}"
    
    @property
    def percentual_equipamentos_disponiveis(self):
        """Calcula percentual de equipamentos disponíveis"""
        if self.total_equipamentos == 0:
            return 0
        return (self.equipamentos_disponiveis / self.total_equipamentos) * 100
    
    @property
    def percentual_insumos_criticos(self):
        """Calcula percentual de insumos em situação crítica"""
        if self.total_insumos == 0:
            return 0
        return ((self.insumos_estoque_baixo + self.insumos_vencendo) / self.total_insumos) * 100


# =============================================================================
# ANALYTICS E BUSINESS INTELLIGENCE
# =============================================================================

class MetricaEvento(models.Model):
    """
    Métricas e KPIs para análise de performance de eventos
    """
    TIPO_METRICA_CHOICES = [
        ('financeiro', 'Financeiro'),
        ('operacional', 'Operacional'),
        ('qualidade', 'Qualidade'),
        ('satisfacao', 'Satisfação'),
        ('produtividade', 'Produtividade'),
        ('outro', 'Outro'),
    ]
    
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="metricas_eventos",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name="metricas",
        verbose_name="Evento"
    )
    nome = models.CharField(max_length=200, verbose_name="Nome da Métrica")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    tipo = models.CharField(max_length=20, choices=TIPO_METRICA_CHOICES, verbose_name="Tipo")
    valor_objetivo = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Valor Objetivo")
    valor_real = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Valor Real")
    unidade_medida = models.CharField(max_length=50, verbose_name="Unidade de Medida")
    data_medicao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Medição")
    responsavel = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="metricas_responsavel",
        verbose_name="Responsável"
    )
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    class Meta:
        verbose_name = "Métrica de Evento"
        verbose_name_plural = "Métricas de Eventos"
        ordering = ['-data_medicao']
    
    def __str__(self):
        return f"{self.nome} - {self.evento.nome}"
    
    @property
    def percentual_atingimento(self):
        """Calcula percentual de atingimento da meta"""
        if not self.valor_objetivo or self.valor_objetivo == 0:
            return None
        return (self.valor_real / self.valor_objetivo) * 100 if self.valor_real else 0


class RelatorioAnalytics(models.Model):
    """
    Relatórios automatizados de analytics
    """
    TIPO_RELATORIO_CHOICES = [
        ('financeiro', 'Financeiro'),
        ('operacional', 'Operacional'),
        ('qualidade', 'Qualidade'),
        ('comparativo', 'Comparativo'),
        ('tendencia', 'Tendência'),
        ('customizado', 'Customizado'),
    ]
    
    PERIODICIDADE_CHOICES = [
        ('diario', 'Diário'),
        ('semanal', 'Semanal'),
        ('mensal', 'Mensal'),
        ('trimestral', 'Trimestral'),
        ('anual', 'Anual'),
        ('sob_demanda', 'Sob Demanda'),
    ]
    
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="relatorios_analytics",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    nome = models.CharField(max_length=200, verbose_name="Nome do Relatório")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    tipo = models.CharField(max_length=20, choices=TIPO_RELATORIO_CHOICES, verbose_name="Tipo")
    periodicidade = models.CharField(max_length=20, choices=PERIODICIDADE_CHOICES, verbose_name="Periodicidade")
    template_relatorio = models.TextField(verbose_name="Template do Relatório")
    parametros = models.JSONField(default=dict, blank=True, verbose_name="Parâmetros")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    ultima_execucao = models.DateTimeField(null=True, blank=True, verbose_name="Última Execução")
    proxima_execucao = models.DateTimeField(null=True, blank=True, verbose_name="Próxima Execução")
    
    class Meta:
        verbose_name = "Relatório de Analytics"
        verbose_name_plural = "Relatórios de Analytics"
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"


class DashboardPersonalizado(models.Model):
    """
    Dashboards customizáveis para diferentes usuários
    """
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="dashboards_personalizados",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    nome = models.CharField(max_length=200, verbose_name="Nome do Dashboard")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="dashboards_personalizados",
        verbose_name="Usuário"
    )
    layout_config = models.JSONField(default=dict, verbose_name="Configuração do Layout")
    widgets_config = models.JSONField(default=list, verbose_name="Configuração dos Widgets")
    filtros_padrao = models.JSONField(default=dict, blank=True, verbose_name="Filtros Padrão")
    publico = models.BooleanField(default=False, verbose_name="Público")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    
    class Meta:
        verbose_name = "Dashboard Personalizado"
        verbose_name_plural = "Dashboards Personalizados"
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} - {self.usuario.username}"


class ComparativoEventos(models.Model):
    """
    Comparação entre eventos para análise de performance
    """
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="comparativos_eventos",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    nome = models.CharField(max_length=200, verbose_name="Nome da Comparação")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    eventos = models.ManyToManyField(
        Evento,
        related_name="comparativos",
        verbose_name="Eventos"
    )
    metricas_comparadas = models.JSONField(default=list, verbose_name="Métricas Comparadas")
    criterios_comparacao = models.JSONField(default=dict, verbose_name="Critérios de Comparação")
    resultado_comparacao = models.JSONField(default=dict, blank=True, verbose_name="Resultado da Comparação")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    responsavel = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comparativos_responsavel",
        verbose_name="Responsável"
    )
    
    class Meta:
        verbose_name = "Comparativo de Eventos"
        verbose_name_plural = "Comparativos de Eventos"
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"{self.nome} ({self.eventos.count()} eventos)"


# =============================================================================
# GESTÃO DE QUALIDADE E SATISFAÇÃO
# =============================================================================

class AvaliacaoEvento(models.Model):
    """
    Avaliações de eventos por clientes e participantes
    """
    TIPO_AVALIADOR_CHOICES = [
        ('cliente', 'Cliente'),
        ('participante', 'Participante'),
        ('fornecedor', 'Fornecedor'),
        ('freelancer', 'Freelancer'),
        ('interno', 'Interno'),
    ]
    
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="avaliacoes_eventos",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name="avaliacoes",
        verbose_name="Evento"
    )
    tipo_avaliador = models.CharField(max_length=20, choices=TIPO_AVALIADOR_CHOICES, verbose_name="Tipo de Avaliador")
    nome_avaliador = models.CharField(max_length=200, verbose_name="Nome do Avaliador")
    email_avaliador = models.EmailField(blank=True, null=True, verbose_name="Email do Avaliador")
    nota_geral = models.PositiveIntegerField(verbose_name="Nota Geral (1-10)")
    comentarios = models.TextField(blank=True, null=True, verbose_name="Comentários")
    aspectos_positivos = models.TextField(blank=True, null=True, verbose_name="Aspectos Positivos")
    aspectos_melhorar = models.TextField(blank=True, null=True, verbose_name="Aspectos a Melhorar")
    recomendaria = models.BooleanField(default=True, verbose_name="Recomendaria")
    data_avaliacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Avaliação")
    anonima = models.BooleanField(default=False, verbose_name="Avaliação Anônima")
    
    class Meta:
        verbose_name = "Avaliação de Evento"
        verbose_name_plural = "Avaliações de Eventos"
        ordering = ['-data_avaliacao']
    
    def __str__(self):
        return f"Avaliação {self.evento.nome} - {self.nome_avaliador} ({self.nota_geral}/10)"


class IndicadorQualidade(models.Model):
    """
    Indicadores de qualidade para eventos
    """
    TIPO_INDICADOR_CHOICES = [
        ('quantitativo', 'Quantitativo'),
        ('qualitativo', 'Qualitativo'),
        ('misto', 'Misto'),
    ]
    
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="indicadores_qualidade",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    nome = models.CharField(max_length=200, verbose_name="Nome do Indicador")
    descricao = models.TextField(verbose_name="Descrição")
    tipo = models.CharField(max_length=20, choices=TIPO_INDICADOR_CHOICES, verbose_name="Tipo")
    formula_calculo = models.TextField(verbose_name="Fórmula de Cálculo")
    meta_objetivo = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Meta Objetivo")
    unidade_medida = models.CharField(max_length=50, verbose_name="Unidade de Medida")
    frequencia_medicao = models.CharField(max_length=50, verbose_name="Frequência de Medição")
    responsavel = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="indicadores_qualidade_responsavel",
        verbose_name="Responsável"
    )
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    
    class Meta:
        verbose_name = "Indicador de Qualidade"
        verbose_name_plural = "Indicadores de Qualidade"
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"


class PesquisaSatisfacao(models.Model):
    """
    Pesquisas de satisfação pós-evento
    """
    STATUS_CHOICES = [
        ('rascunho', 'Rascunho'),
        ('ativa', 'Ativa'),
        ('finalizada', 'Finalizada'),
        ('cancelada', 'Cancelada'),
    ]
    
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="pesquisas_satisfacao",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name="pesquisas_satisfacao",
        verbose_name="Evento"
    )
    titulo = models.CharField(max_length=200, verbose_name="Título da Pesquisa")
    descricao = models.TextField(verbose_name="Descrição")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='rascunho', verbose_name="Status")
    data_inicio = models.DateTimeField(verbose_name="Data de Início")
    data_fim = models.DateTimeField(verbose_name="Data de Fim")
    link_pesquisa = models.URLField(blank=True, null=True, verbose_name="Link da Pesquisa")
    total_respostas = models.PositiveIntegerField(default=0, verbose_name="Total de Respostas")
    meta_respostas = models.PositiveIntegerField(null=True, blank=True, verbose_name="Meta de Respostas")
    responsavel = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="pesquisas_satisfacao_responsavel",
        verbose_name="Responsável"
    )
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    
    class Meta:
        verbose_name = "Pesquisa de Satisfação"
        verbose_name_plural = "Pesquisas de Satisfação"
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"{self.titulo} - {self.evento.nome}"


class FeedbackFreelancer(models.Model):
    """
    Sistema de feedback e avaliação de freelancers
    """
    TIPO_FEEDBACK_CHOICES = [
        ('positivo', 'Positivo'),
        ('negativo', 'Negativo'),
        ('neutro', 'Neutro'),
        ('sugestao', 'Sugestão'),
    ]
    
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="feedbacks_freelancers",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    freelancer = models.ForeignKey(
        Freelance,
        on_delete=models.CASCADE,
        related_name="feedbacks",
        verbose_name="Freelancer"
    )
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name="feedbacks_freelancers",
        verbose_name="Evento"
    )
    tipo = models.CharField(max_length=20, choices=TIPO_FEEDBACK_CHOICES, verbose_name="Tipo")
    nota_desempenho = models.PositiveIntegerField(verbose_name="Nota de Desempenho (1-10)")
    comentarios = models.TextField(verbose_name="Comentários")
    aspectos_destacar = models.TextField(blank=True, null=True, verbose_name="Aspectos a Destacar")
    areas_melhorar = models.TextField(blank=True, null=True, verbose_name="Áreas a Melhorar")
    recomendaria = models.BooleanField(default=True, verbose_name="Recomendaria")
    avaliador = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="feedbacks_dados",
        verbose_name="Avaliador"
    )
    data_avaliacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Avaliação")
    
    class Meta:
        verbose_name = "Feedback de Freelancer"
        verbose_name_plural = "Feedbacks de Freelancers"
        ordering = ['-data_avaliacao']
    
    def __str__(self):
        return f"Feedback {self.freelancer.nome} - {self.evento.nome} ({self.nota_desempenho}/10)"


# =============================================================================
# AUTOMAÇÃO E WORKFLOWS
# =============================================================================

class WorkflowEvento(models.Model):
    """
    Fluxos de trabalho automatizados para eventos
    """
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
        ('pausado', 'Pausado'),
    ]
    
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="workflows_eventos",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    nome = models.CharField(max_length=200, verbose_name="Nome do Workflow")
    descricao = models.TextField(verbose_name="Descrição")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ativo', verbose_name="Status")
    trigger_evento = models.CharField(max_length=100, verbose_name="Evento Disparador")
    acoes_automaticas = models.JSONField(default=list, verbose_name="Ações Automáticas")
    condicoes_execucao = models.JSONField(default=dict, verbose_name="Condições de Execução")
    responsavel = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="workflows_responsavel",
        verbose_name="Responsável"
    )
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    ultima_execucao = models.DateTimeField(null=True, blank=True, verbose_name="Última Execução")
    
    class Meta:
        verbose_name = "Workflow de Evento"
        verbose_name_plural = "Workflows de Eventos"
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} ({self.get_status_display()})"


class RegraNegocio(models.Model):
    """
    Regras de negócio configuráveis para automação
    """
    TIPO_REGRA_CHOICES = [
        ('validacao', 'Validação'),
        ('calculo', 'Cálculo'),
        ('notificacao', 'Notificação'),
        ('aprovacao', 'Aprovação'),
        ('integracao', 'Integração'),
    ]
    
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="regras_negocio",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    nome = models.CharField(max_length=200, verbose_name="Nome da Regra")
    descricao = models.TextField(verbose_name="Descrição")
    tipo = models.CharField(max_length=20, choices=TIPO_REGRA_CHOICES, verbose_name="Tipo")
    condicao = models.TextField(verbose_name="Condição")
    acao = models.TextField(verbose_name="Ação")
    prioridade = models.PositiveIntegerField(default=1, verbose_name="Prioridade")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    criado_por = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="regras_negocio_criadas",
        verbose_name="Criado por"
    )
    
    class Meta:
        verbose_name = "Regra de Negócio"
        verbose_name_plural = "Regras de Negócio"
        ordering = ['prioridade', 'nome']
    
    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"


class NotificacaoAutomatica(models.Model):
    """
    Sistema de notificações automáticas
    """
    TIPO_NOTIFICACAO_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
        ('sistema', 'Sistema'),
        ('whatsapp', 'WhatsApp'),
    ]
    
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('enviada', 'Enviada'),
        ('falhou', 'Falhou'),
        ('cancelada', 'Cancelada'),
    ]
    
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="notificacoes_automaticas",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    titulo = models.CharField(max_length=200, verbose_name="Título")
    mensagem = models.TextField(verbose_name="Mensagem")
    tipo = models.CharField(max_length=20, choices=TIPO_NOTIFICACAO_CHOICES, verbose_name="Tipo")
    destinatarios = models.JSONField(default=list, verbose_name="Destinatários")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente', verbose_name="Status")
    data_agendamento = models.DateTimeField(verbose_name="Data de Agendamento")
    data_envio = models.DateTimeField(null=True, blank=True, verbose_name="Data de Envio")
    tentativas_envio = models.PositiveIntegerField(default=0, verbose_name="Tentativas de Envio")
    erro_envio = models.TextField(blank=True, null=True, verbose_name="Erro no Envio")
    evento_relacionado = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name="notificacoes",
        verbose_name="Evento Relacionado",
        null=True,
        blank=True
    )
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    
    class Meta:
        verbose_name = "Notificação Automática"
        verbose_name_plural = "Notificações Automáticas"
        ordering = ['-data_agendamento']
    
    def __str__(self):
        return f"{self.titulo} - {self.get_status_display()}"


class IntegracaoERP(models.Model):
    """
    Integrações com sistemas ERP externos
    """
    TIPO_SISTEMA_CHOICES = [
        ('sap', 'SAP'),
        ('oracle', 'Oracle'),
        ('microsoft_dynamics', 'Microsoft Dynamics'),
        ('totvs', 'TOTVS'),
        ('senior', 'Senior'),
        ('outro', 'Outro'),
    ]
    
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
        ('erro', 'Erro'),
        ('manutencao', 'Manutenção'),
    ]
    
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="integracoes_erp",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    nome = models.CharField(max_length=200, verbose_name="Nome da Integração")
    tipo_sistema = models.CharField(max_length=30, choices=TIPO_SISTEMA_CHOICES, verbose_name="Tipo de Sistema")
    url_api = models.URLField(verbose_name="URL da API")
    credenciais = models.JSONField(verbose_name="Credenciais")
    configuracoes = models.JSONField(default=dict, verbose_name="Configurações")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ativo', verbose_name="Status")
    ultima_sincronizacao = models.DateTimeField(null=True, blank=True, verbose_name="Última Sincronização")
    frequencia_sincronizacao = models.CharField(max_length=50, verbose_name="Frequência de Sincronização")
    responsavel = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="integracoes_erp_responsavel",
        verbose_name="Responsável"
    )
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    
    class Meta:
        verbose_name = "Integração ERP"
        verbose_name_plural = "Integrações ERP"
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} ({self.get_tipo_sistema_display()})"


# =============================================================================
# MOBILIDADE E FIELD MANAGEMENT
# =============================================================================

class ChecklistMobile(models.Model):
    """
    Checklists específicos para uso em dispositivos móveis no campo
    """
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('em_andamento', 'Em Andamento'),
        ('concluido', 'Concluído'),
        ('cancelado', 'Cancelado'),
    ]
    
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="checklists_mobile",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name="checklists_mobile",
        verbose_name="Evento"
    )
    setor = models.ForeignKey(
        SetorEvento,
        on_delete=models.CASCADE,
        related_name="checklists_mobile",
        verbose_name="Setor",
        null=True,
        blank=True
    )
    titulo = models.CharField(max_length=200, verbose_name="Título")
    descricao = models.TextField(verbose_name="Descrição")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente', verbose_name="Status")
    responsavel = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="checklists_mobile_responsavel",
        verbose_name="Responsável"
    )
    data_limite = models.DateTimeField(verbose_name="Data Limite")
    data_inicio = models.DateTimeField(null=True, blank=True, verbose_name="Data de Início")
    data_conclusao = models.DateTimeField(null=True, blank=True, verbose_name="Data de Conclusão")
    localizacao_inicio = models.JSONField(null=True, blank=True, verbose_name="Localização de Início")
    localizacao_fim = models.JSONField(null=True, blank=True, verbose_name="Localização de Fim")
    fotos_evidencia = models.JSONField(default=list, verbose_name="Fotos de Evidência")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    
    class Meta:
        verbose_name = "Checklist Mobile"
        verbose_name_plural = "Checklists Mobile"
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"{self.titulo} - {self.evento.nome}"


class ItemChecklistMobile(models.Model):
    """
    Itens individuais de um checklist mobile
    """
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('concluido', 'Concluído'),
        ('problema', 'Problema'),
        ('nao_aplicavel', 'Não Aplicável'),
    ]
    
    checklist = models.ForeignKey(
        ChecklistMobile,
        on_delete=models.CASCADE,
        related_name="itens",
        verbose_name="Checklist"
    )
    descricao = models.CharField(max_length=500, verbose_name="Descrição")
    instrucoes = models.TextField(blank=True, null=True, verbose_name="Instruções")
    ordem = models.PositiveIntegerField(default=0, verbose_name="Ordem")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente', verbose_name="Status")
    obrigatorio = models.BooleanField(default=True, verbose_name="Obrigatório")
    permite_foto = models.BooleanField(default=False, verbose_name="Permite Foto")
    permite_comentario = models.BooleanField(default=True, verbose_name="Permite Comentário")
    comentario = models.TextField(blank=True, null=True, verbose_name="Comentário")
    fotos = models.JSONField(default=list, verbose_name="Fotos")
    data_conclusao = models.DateTimeField(null=True, blank=True, verbose_name="Data de Conclusão")
    localizacao = models.JSONField(null=True, blank=True, verbose_name="Localização")
    
    class Meta:
        verbose_name = "Item Checklist Mobile"
        verbose_name_plural = "Itens Checklist Mobile"
        ordering = ['ordem']
    
    def __str__(self):
        return f"{self.descricao} - {self.checklist.titulo}"


class GeolocalizacaoEquipamento(models.Model):
    """
    Rastreamento GPS de equipamentos
    """
    equipamento = models.ForeignKey(
        Equipamento,
        on_delete=models.CASCADE,
        related_name="geolocalizacoes",
        verbose_name="Equipamento"
    )
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name="geolocalizacoes_equipamentos",
        verbose_name="Evento"
    )
    latitude = models.DecimalField(max_digits=10, decimal_places=8, verbose_name="Latitude")
    longitude = models.DecimalField(max_digits=11, decimal_places=8, verbose_name="Longitude")
    altitude = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Altitude")
    precisao = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Precisão (metros)")
    endereco = models.CharField(max_length=500, blank=True, null=True, verbose_name="Endereço")
    responsavel = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="geolocalizacoes_equipamentos",
        verbose_name="Responsável"
    )
    data_rastreamento = models.DateTimeField(auto_now_add=True, verbose_name="Data de Rastreamento")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    class Meta:
        verbose_name = "Geolocalização de Equipamento"
        verbose_name_plural = "Geolocalizações de Equipamentos"
        ordering = ['-data_rastreamento']
    
    def __str__(self):
        return f"{self.equipamento.nome} - {self.data_rastreamento.strftime('%d/%m/%Y %H:%M')}"


class QRCodeEquipamento(models.Model):
    """
    Controle de equipamentos via QR Code
    """
    equipamento = models.OneToOneField(
        Equipamento,
        on_delete=models.CASCADE,
        related_name="qr_code",
        verbose_name="Equipamento"
    )
    codigo_qr = models.CharField(max_length=100, unique=True, verbose_name="Código QR")
    url_qr = models.URLField(verbose_name="URL do QR Code")
    data_geracao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Geração")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    total_scans = models.PositiveIntegerField(default=0, verbose_name="Total de Scans")
    ultimo_scan = models.DateTimeField(null=True, blank=True, verbose_name="Último Scan")
    
    class Meta:
        verbose_name = "QR Code de Equipamento"
        verbose_name_plural = "QR Codes de Equipamentos"
    
    def __str__(self):
        return f"QR Code - {self.equipamento.nome}"


class ScanQRCode(models.Model):
    """
    Registro de scans de QR Codes
    """
    TIPO_SCAN_CHOICES = [
        ('checkin', 'Check-in'),
        ('checkout', 'Check-out'),
        ('manutencao', 'Manutenção'),
        ('inventario', 'Inventário'),
        ('outro', 'Outro'),
    ]
    
    qr_code = models.ForeignKey(
        QRCodeEquipamento,
        on_delete=models.CASCADE,
        related_name="scans",
        verbose_name="QR Code"
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="scans_qr_code",
        verbose_name="Usuário"
    )
    tipo_scan = models.CharField(max_length=20, choices=TIPO_SCAN_CHOICES, verbose_name="Tipo de Scan")
    localizacao = models.JSONField(null=True, blank=True, verbose_name="Localização")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    data_scan = models.DateTimeField(auto_now_add=True, verbose_name="Data do Scan")
    
    class Meta:
        verbose_name = "Scan QR Code"
        verbose_name_plural = "Scans QR Code"
        ordering = ['-data_scan']
    
    def __str__(self):
        return f"Scan {self.qr_code.equipamento.nome} - {self.usuario.username}"


class AppFieldWorker(models.Model):
    """
    Configurações específicas para trabalhadores de campo
    """
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="config_field_worker",
        verbose_name="Usuário"
    )
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="field_workers",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    funcoes_habilitadas = models.JSONField(default=list, verbose_name="Funções Habilitadas")
    setores_acesso = models.ManyToManyField(
        SetorEvento,
        related_name="field_workers_acesso",
        verbose_name="Setores com Acesso",
        blank=True
    )
    permissoes_especiais = models.JSONField(default=dict, verbose_name="Permissões Especiais")
    configuracao_offline = models.JSONField(default=dict, verbose_name="Configuração Offline")
    ultima_sincronizacao = models.DateTimeField(null=True, blank=True, verbose_name="Última Sincronização")
    versao_app = models.CharField(max_length=20, blank=True, null=True, verbose_name="Versão do App")
    dispositivo_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="ID do Dispositivo")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    
    class Meta:
        verbose_name = "Field Worker"
        verbose_name_plural = "Field Workers"
    
    def __str__(self):
        return f"Field Worker - {self.usuario.username}"


# =============================================================================
# GESTÃO DE RISCOS E COMPLIANCE
# =============================================================================

class RiscoEvento(models.Model):
    """
    Identificação e controle de riscos em eventos
    """
    TIPO_RISCO_CHOICES = [
        ('operacional', 'Operacional'),
        ('financeiro', 'Financeiro'),
        ('seguranca', 'Segurança'),
        ('ambiental', 'Ambiental'),
        ('legal', 'Legal'),
        ('reputacional', 'Reputacional'),
        ('tecnologico', 'Tecnológico'),
        ('outro', 'Outro'),
    ]
    
    NIVEL_RISCO_CHOICES = [
        ('baixo', 'Baixo'),
        ('medio', 'Médio'),
        ('alto', 'Alto'),
        ('critico', 'Crítico'),
    ]
    
    STATUS_CHOICES = [
        ('identificado', 'Identificado'),
        ('avaliado', 'Avaliado'),
        ('mitigado', 'Mitigado'),
        ('monitorado', 'Monitorado'),
        ('resolvido', 'Resolvido'),
        ('cancelado', 'Cancelado'),
    ]
    
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="riscos_eventos",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name="riscos",
        verbose_name="Evento"
    )
    titulo = models.CharField(max_length=200, verbose_name="Título do Risco")
    descricao = models.TextField(verbose_name="Descrição")
    tipo = models.CharField(max_length=20, choices=TIPO_RISCO_CHOICES, verbose_name="Tipo")
    nivel = models.CharField(max_length=20, choices=NIVEL_RISCO_CHOICES, verbose_name="Nível")
    probabilidade = models.PositiveIntegerField(verbose_name="Probabilidade (1-5)")
    impacto = models.PositiveIntegerField(verbose_name="Impacto (1-5)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='identificado', verbose_name="Status")
    responsavel = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="riscos_responsavel",
        verbose_name="Responsável"
    )
    acoes_mitigacao = models.TextField(verbose_name="Ações de Mitigação")
    plano_contingencia = models.TextField(blank=True, null=True, verbose_name="Plano de Contingência")
    data_identificacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Identificação")
    data_avaliacao = models.DateTimeField(null=True, blank=True, verbose_name="Data de Avaliação")
    data_resolucao = models.DateTimeField(null=True, blank=True, verbose_name="Data de Resolução")
    
    class Meta:
        verbose_name = "Risco de Evento"
        verbose_name_plural = "Riscos de Eventos"
        ordering = ['-data_identificacao']
    
    def __str__(self):
        return f"{self.titulo} - {self.evento.nome} ({self.get_nivel_display()})"
    
    @property
    def score_risco(self):
        """Calcula o score de risco (probabilidade x impacto)"""
        return self.probabilidade * self.impacto


class PlanoContingencia(models.Model):
    """
    Planos de contingência para eventos
    """
    STATUS_CHOICES = [
        ('rascunho', 'Rascunho'),
        ('aprovado', 'Aprovado'),
        ('ativo', 'Ativo'),
        ('executado', 'Executado'),
        ('cancelado', 'Cancelado'),
    ]
    
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="planos_contingencia",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name="planos_contingencia",
        verbose_name="Evento"
    )
    titulo = models.CharField(max_length=200, verbose_name="Título do Plano")
    descricao = models.TextField(verbose_name="Descrição")
    cenario = models.TextField(verbose_name="Cenário")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='rascunho', verbose_name="Status")
    acoes_emergencia = models.JSONField(default=list, verbose_name="Ações de Emergência")
    responsaveis = models.JSONField(default=list, verbose_name="Responsáveis")
    contatos_emergencia = models.JSONField(default=list, verbose_name="Contatos de Emergência")
    recursos_necessarios = models.JSONField(default=list, verbose_name="Recursos Necessários")
    tempo_resposta = models.CharField(max_length=100, verbose_name="Tempo de Resposta")
    custo_estimado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Custo Estimado")
    aprovado_por = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="planos_contingencia_aprovados",
        verbose_name="Aprovado por",
        null=True,
        blank=True
    )
    data_aprovacao = models.DateTimeField(null=True, blank=True, verbose_name="Data de Aprovação")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    
    class Meta:
        verbose_name = "Plano de Contingência"
        verbose_name_plural = "Planos de Contingência"
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"{self.titulo} - {self.evento.nome}"


class ComplianceEvento(models.Model):
    """
    Controle de conformidade legal e regulatória
    """
    TIPO_COMPLIANCE_CHOICES = [
        ('licenca', 'Licença'),
        ('alvara', 'Alvará'),
        ('certificado', 'Certificado'),
        ('seguro', 'Seguro'),
        ('contrato', 'Contrato'),
        ('outro', 'Outro'),
    ]
    
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('em_analise', 'Em Análise'),
        ('aprovado', 'Aprovado'),
        ('rejeitado', 'Rejeitado'),
        ('vencido', 'Vencido'),
        ('cancelado', 'Cancelado'),
    ]
    
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="compliance_eventos",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name="compliance",
        verbose_name="Evento"
    )
    tipo = models.CharField(max_length=20, choices=TIPO_COMPLIANCE_CHOICES, verbose_name="Tipo")
    nome_documento = models.CharField(max_length=200, verbose_name="Nome do Documento")
    numero_documento = models.CharField(max_length=100, verbose_name="Número do Documento")
    orgao_emissor = models.CharField(max_length=200, verbose_name="Órgão Emissor")
    data_emissao = models.DateField(verbose_name="Data de Emissão")
    data_vencimento = models.DateField(verbose_name="Data de Vencimento")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente', verbose_name="Status")
    arquivo_documento = models.FileField(upload_to='compliance/', blank=True, null=True, verbose_name="Arquivo do Documento")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    responsavel = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="compliance_responsavel",
        verbose_name="Responsável"
    )
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    
    class Meta:
        verbose_name = "Compliance de Evento"
        verbose_name_plural = "Compliance de Eventos"
        ordering = ['data_vencimento']
    
    def __str__(self):
        return f"{self.nome_documento} - {self.evento.nome}"
    
    @property
    def dias_para_vencimento(self):
        """Calcula dias para vencimento"""
        from datetime import date
        hoje = date.today()
        return (self.data_vencimento - hoje).days


class SeguroEvento(models.Model):
    """
    Gestão de seguros para eventos
    """
    TIPO_SEGURO_CHOICES = [
        ('responsabilidade_civil', 'Responsabilidade Civil'),
        ('equipamentos', 'Equipamentos'),
        ('pessoas', 'Pessoas'),
        ('evento_cancelamento', 'Cancelamento de Evento'),
        ('outro', 'Outro'),
    ]
    
    STATUS_CHOICES = [
        ('cotacao', 'Cotação'),
        ('aprovado', 'Aprovado'),
        ('ativo', 'Ativo'),
        ('vencido', 'Vencido'),
        ('cancelado', 'Cancelado'),
    ]
    
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="seguros_eventos",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name="seguros",
        verbose_name="Evento"
    )
    tipo = models.CharField(max_length=30, choices=TIPO_SEGURO_CHOICES, verbose_name="Tipo")
    seguradora = models.CharField(max_length=200, verbose_name="Seguradora")
    numero_apolice = models.CharField(max_length=100, verbose_name="Número da Apólice")
    valor_segurado = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Valor Segurado")
    valor_premio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor do Prêmio")
    franquia = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Franquia")
    data_inicio = models.DateField(verbose_name="Data de Início")
    data_fim = models.DateField(verbose_name="Data de Fim")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='cotacao', verbose_name="Status")
    coberturas = models.JSONField(default=list, verbose_name="Coberturas")
    exclusoes = models.JSONField(default=list, verbose_name="Exclusões")
    contato_seguradora = models.JSONField(default=dict, verbose_name="Contato da Seguradora")
    arquivo_apolice = models.FileField(upload_to='seguros/', blank=True, null=True, verbose_name="Arquivo da Apólice")
    responsavel = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="seguros_responsavel",
        verbose_name="Responsável"
    )
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    
    class Meta:
        verbose_name = "Seguro de Evento"
        verbose_name_plural = "Seguros de Eventos"
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.evento.nome} ({self.seguradora})"


# =============================================================================
# INTELIGÊNCIA ARTIFICIAL E PREDIÇÃO
# =============================================================================

class PrevisaoDemanda(models.Model):
    """
    Previsões de demanda usando IA para eventos
    """
    TIPO_PREVISAO_CHOICES = [
        ('participantes', 'Participantes'),
        ('equipamentos', 'Equipamentos'),
        ('insumos', 'Insumos'),
        ('pessoal', 'Pessoal'),
        ('receita', 'Receita'),
        ('custo', 'Custo'),
    ]
    
    STATUS_CHOICES = [
        ('processando', 'Processando'),
        ('concluida', 'Concluída'),
        ('erro', 'Erro'),
        ('cancelada', 'Cancelada'),
    ]
    
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="previsoes_demanda",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name="previsoes_demanda",
        verbose_name="Evento"
    )
    tipo = models.CharField(max_length=20, choices=TIPO_PREVISAO_CHOICES, verbose_name="Tipo")
    modelo_ia = models.CharField(max_length=100, verbose_name="Modelo de IA")
    dados_entrada = models.JSONField(verbose_name="Dados de Entrada")
    resultado_previsao = models.JSONField(verbose_name="Resultado da Previsão")
    confiabilidade = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Confiabilidade (%)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processando', verbose_name="Status")
    data_previsao = models.DateTimeField(auto_now_add=True, verbose_name="Data da Previsão")
    data_validade = models.DateTimeField(verbose_name="Data de Validade")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    class Meta:
        verbose_name = "Previsão de Demanda"
        verbose_name_plural = "Previsões de Demanda"
        ordering = ['-data_previsao']
    
    def __str__(self):
        return f"Previsão {self.get_tipo_display()} - {self.evento.nome}"


class OtimizacaoRecursos(models.Model):
    """
    Otimização automática de recursos usando IA
    """
    TIPO_OTIMIZACAO_CHOICES = [
        ('equipamentos', 'Equipamentos'),
        ('pessoal', 'Pessoal'),
        ('espaco', 'Espaço'),
        ('tempo', 'Tempo'),
        ('custo', 'Custo'),
        ('qualidade', 'Qualidade'),
    ]
    
    STATUS_CHOICES = [
        ('analisando', 'Analisando'),
        ('otimizada', 'Otimizada'),
        ('aplicada', 'Aplicada'),
        ('rejeitada', 'Rejeitada'),
    ]
    
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="otimizacoes_recursos",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name="otimizacoes_recursos",
        verbose_name="Evento"
    )
    tipo = models.CharField(max_length=20, choices=TIPO_OTIMIZACAO_CHOICES, verbose_name="Tipo")
    algoritmo_ia = models.CharField(max_length=100, verbose_name="Algoritmo de IA")
    configuracao_atual = models.JSONField(verbose_name="Configuração Atual")
    configuracao_otimizada = models.JSONField(verbose_name="Configuração Otimizada")
    ganho_estimado = models.JSONField(verbose_name="Ganho Estimado")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='analisando', verbose_name="Status")
    aprovado_por = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="otimizacoes_aprovadas",
        verbose_name="Aprovado por",
        null=True,
        blank=True
    )
    data_otimizacao = models.DateTimeField(auto_now_add=True, verbose_name="Data da Otimização")
    data_aplicacao = models.DateTimeField(null=True, blank=True, verbose_name="Data de Aplicação")
    
    class Meta:
        verbose_name = "Otimização de Recursos"
        verbose_name_plural = "Otimizações de Recursos"
        ordering = ['-data_otimizacao']
    
    def __str__(self):
        return f"Otimização {self.get_tipo_display()} - {self.evento.nome}"


class DeteccaoAnomalias(models.Model):
    """
    Detecção de anomalias usando IA
    """
    TIPO_ANOMALIA_CHOICES = [
        ('financeira', 'Financeira'),
        ('operacional', 'Operacional'),
        ('qualidade', 'Qualidade'),
        ('seguranca', 'Segurança'),
        ('performance', 'Performance'),
        ('outro', 'Outro'),
    ]
    
    SEVERIDADE_CHOICES = [
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    ]
    
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="deteccoes_anomalias",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name="deteccoes_anomalias",
        verbose_name="Evento",
        null=True,
        blank=True
    )
    tipo = models.CharField(max_length=20, choices=TIPO_ANOMALIA_CHOICES, verbose_name="Tipo")
    severidade = models.CharField(max_length=20, choices=SEVERIDADE_CHOICES, verbose_name="Severidade")
    descricao = models.TextField(verbose_name="Descrição")
    dados_anomalia = models.JSONField(verbose_name="Dados da Anomalia")
    algoritmo_deteccao = models.CharField(max_length=100, verbose_name="Algoritmo de Detecção")
    confiabilidade = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Confiabilidade (%)")
    status = models.CharField(max_length=20, default='detectada', verbose_name="Status")
    responsavel = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="anomalias_responsavel",
        verbose_name="Responsável",
        null=True,
        blank=True
    )
    acao_tomada = models.TextField(blank=True, null=True, verbose_name="Ação Tomada")
    data_deteccao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Detecção")
    data_resolucao = models.DateTimeField(null=True, blank=True, verbose_name="Data de Resolução")
    
    class Meta:
        verbose_name = "Detecção de Anomalia"
        verbose_name_plural = "Detecções de Anomalias"
        ordering = ['-data_deteccao']
    
    def __str__(self):
        return f"Anomalia {self.get_tipo_display()} - {self.get_severidade_display()}"


class RecomendacaoInteligente(models.Model):
    """
    Recomendações automáticas baseadas em IA
    """
    TIPO_RECOMENDACAO_CHOICES = [
        ('melhoria_processo', 'Melhoria de Processo'),
        ('reducao_custo', 'Redução de Custo'),
        ('aumento_qualidade', 'Aumento de Qualidade'),
        ('otimizacao_tempo', 'Otimização de Tempo'),
        ('gestao_risco', 'Gestão de Risco'),
        ('outro', 'Outro'),
    ]
    
    STATUS_CHOICES = [
        ('gerada', 'Gerada'),
        ('visualizada', 'Visualizada'),
        ('aplicada', 'Aplicada'),
        ('rejeitada', 'Rejeitada'),
    ]
    
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="recomendacoes_inteligentes",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name="recomendacoes_inteligentes",
        verbose_name="Evento",
        null=True,
        blank=True
    )
    tipo = models.CharField(max_length=30, choices=TIPO_RECOMENDACAO_CHOICES, verbose_name="Tipo")
    titulo = models.CharField(max_length=200, verbose_name="Título")
    descricao = models.TextField(verbose_name="Descrição")
    justificativa = models.TextField(verbose_name="Justificativa")
    impacto_estimado = models.JSONField(verbose_name="Impacto Estimado")
    acoes_sugeridas = models.JSONField(verbose_name="Ações Sugeridas")
    algoritmo_ia = models.CharField(max_length=100, verbose_name="Algoritmo de IA")
    confiabilidade = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Confiabilidade (%)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='gerada', verbose_name="Status")
    destinatario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recomendacoes_recebidas",
        verbose_name="Destinatário"
    )
    data_geracao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Geração")
    data_visualizacao = models.DateTimeField(null=True, blank=True, verbose_name="Data de Visualização")
    data_aplicacao = models.DateTimeField(null=True, blank=True, verbose_name="Data de Aplicação")
    
    class Meta:
        verbose_name = "Recomendação Inteligente"
        verbose_name_plural = "Recomendações Inteligentes"
        ordering = ['-data_geracao']
    
    def __str__(self):
        return f"{self.titulo} - {self.get_tipo_display()}"


# =============================================================================
# MARKETPLACE E NETWORKING
# =============================================================================

class MarketplaceFreelancer(models.Model):
    """
    Plataforma de marketplace para freelancers
    """
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
        ('suspenso', 'Suspenso'),
        ('verificando', 'Verificando'),
    ]
    
    freelancer = models.OneToOneField(
        Freelance,
        on_delete=models.CASCADE,
        related_name="marketplace",
        verbose_name="Freelancer"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='verificando', verbose_name="Status")
    perfil_publico = models.JSONField(default=dict, verbose_name="Perfil Público")
    portfolio = models.JSONField(default=list, verbose_name="Portfolio")
    especialidades = models.JSONField(default=list, verbose_name="Especialidades")
    disponibilidade = models.JSONField(default=dict, verbose_name="Disponibilidade")
    avaliacao_media = models.DecimalField(max_digits=3, decimal_places=2, default=0, verbose_name="Avaliação Média")
    total_avaliacoes = models.PositiveIntegerField(default=0, verbose_name="Total de Avaliações")
    projetos_concluidos = models.PositiveIntegerField(default=0, verbose_name="Projetos Concluídos")
    taxa_sucesso = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Taxa de Sucesso (%)")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    data_ultima_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Última Atualização")
    
    class Meta:
        verbose_name = "Marketplace Freelancer"
        verbose_name_plural = "Marketplace Freelancers"
    
    def __str__(self):
        return f"Marketplace - {self.freelancer.nome}"


class RedeFornecedores(models.Model):
    """
    Rede de fornecedores qualificados
    """
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
        ('suspenso', 'Suspenso'),
        ('verificando', 'Verificando'),
    ]
    
    CATEGORIA_CHOICES = [
        ('premium', 'Premium'),
        ('gold', 'Gold'),
        ('silver', 'Silver'),
        ('bronze', 'Bronze'),
    ]
    
    fornecedor = models.OneToOneField(
        Fornecedor,
        on_delete=models.CASCADE,
        related_name="rede",
        verbose_name="Fornecedor"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='verificando', verbose_name="Status")
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES, default='bronze', verbose_name="Categoria")
    perfil_publico = models.JSONField(default=dict, verbose_name="Perfil Público")
    certificacoes = models.JSONField(default=list, verbose_name="Certificações")
    portfolio = models.JSONField(default=list, verbose_name="Portfolio")
    avaliacao_media = models.DecimalField(max_digits=3, decimal_places=2, default=0, verbose_name="Avaliação Média")
    total_avaliacoes = models.PositiveIntegerField(default=0, verbose_name="Total de Avaliações")
    projetos_concluidos = models.PositiveIntegerField(default=0, verbose_name="Projetos Concluídos")
    taxa_sucesso = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Taxa de Sucesso (%)")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    data_ultima_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Última Atualização")
    
    class Meta:
        verbose_name = "Rede de Fornecedor"
        verbose_name_plural = "Rede de Fornecedores"
    
    def __str__(self):
        return f"Rede - {self.fornecedor.nome_fantasia}"


class AvaliacaoFornecedor(models.Model):
    """
    Sistema de avaliações para fornecedores
    """
    TIPO_AVALIACAO_CHOICES = [
        ('qualidade', 'Qualidade'),
        ('prazo', 'Prazo'),
        ('atendimento', 'Atendimento'),
        ('preco', 'Preço'),
        ('geral', 'Geral'),
    ]
    
    fornecedor = models.ForeignKey(
        Fornecedor,
        on_delete=models.CASCADE,
        related_name="avaliacoes",
        verbose_name="Fornecedor"
    )
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name="avaliacoes_fornecedores",
        verbose_name="Evento"
    )
    tipo = models.CharField(max_length=20, choices=TIPO_AVALIACAO_CHOICES, verbose_name="Tipo")
    nota = models.PositiveIntegerField(verbose_name="Nota (1-10)")
    comentarios = models.TextField(verbose_name="Comentários")
    aspectos_positivos = models.TextField(blank=True, null=True, verbose_name="Aspectos Positivos")
    aspectos_melhorar = models.TextField(blank=True, null=True, verbose_name="Aspectos a Melhorar")
    recomendaria = models.BooleanField(default=True, verbose_name="Recomendaria")
    avaliador = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="avaliacoes_fornecedores_dadas",
        verbose_name="Avaliador"
    )
    data_avaliacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Avaliação")
    anonima = models.BooleanField(default=False, verbose_name="Avaliação Anônima")
    
    class Meta:
        verbose_name = "Avaliação de Fornecedor"
        verbose_name_plural = "Avaliações de Fornecedores"
        ordering = ['-data_avaliacao']
    
    def __str__(self):
        return f"Avaliação {self.fornecedor.nome_fantasia} - {self.evento.nome} ({self.nota}/10)"


class ContratoInteligente(models.Model):
    """
    Contratos automatizados e inteligentes
    """
    TIPO_CONTRATO_CHOICES = [
        ('freelancer', 'Freelancer'),
        ('fornecedor', 'Fornecedor'),
        ('cliente', 'Cliente'),
        ('parceiro', 'Parceiro'),
    ]
    
    STATUS_CHOICES = [
        ('rascunho', 'Rascunho'),
        ('pendente_assinatura', 'Pendente Assinatura'),
        ('ativo', 'Ativo'),
        ('vencido', 'Vencido'),
        ('cancelado', 'Cancelado'),
    ]
    
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="contratos_inteligentes",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name="contratos_inteligentes",
        verbose_name="Evento",
        null=True,
        blank=True
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CONTRATO_CHOICES, verbose_name="Tipo")
    titulo = models.CharField(max_length=200, verbose_name="Título")
    template_contrato = models.TextField(verbose_name="Template do Contrato")
    clausulas_automaticas = models.JSONField(default=list, verbose_name="Cláusulas Automáticas")
    condicoes_ativacao = models.JSONField(default=dict, verbose_name="Condições de Ativação")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='rascunho', verbose_name="Status")
    valor_contrato = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Valor do Contrato")
    data_inicio = models.DateField(null=True, blank=True, verbose_name="Data de Início")
    data_fim = models.DateField(null=True, blank=True, verbose_name="Data de Fim")
    assinaturas = models.JSONField(default=list, verbose_name="Assinaturas")
    responsavel = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="contratos_inteligentes_responsavel",
        verbose_name="Responsável"
    )
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_ativacao = models.DateTimeField(null=True, blank=True, verbose_name="Data de Ativação")
    
    class Meta:
        verbose_name = "Contrato Inteligente"
        verbose_name_plural = "Contratos Inteligentes"
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"{self.titulo} - {self.get_tipo_display()}"


# =============================================================================
# GESTÃO DE CRESCIMENTO E EXPANSÃO
# =============================================================================

class FranchiseEvento(models.Model):
    """
    Modelo de franquia para expansão de eventos
    """
    STATUS_CHOICES = [
        ('rascunho', 'Rascunho'),
        ('aprovado', 'Aprovado'),
        ('ativo', 'Ativo'),
        ('suspenso', 'Suspenso'),
        ('cancelado', 'Cancelado'),
    ]
    
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="franchises",
        verbose_name="Empresa Contratante"
    )
    nome_franquia = models.CharField(max_length=200, verbose_name="Nome da Franquia")
    descricao = models.TextField(verbose_name="Descrição")
    modelo_negocio = models.TextField(verbose_name="Modelo de Negócio")
    investimento_inicial = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Investimento Inicial")
    taxa_franquia = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Taxa de Franquia (%)")
    royalties = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Royalties (%)")
    suporte_incluido = models.JSONField(default=list, verbose_name="Suporte Incluído")
    requisitos_franqueado = models.JSONField(default=list, verbose_name="Requisitos do Franqueado")
    territorio_exclusivo = models.BooleanField(default=False, verbose_name="Território Exclusivo")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='rascunho', verbose_name="Status")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    responsavel = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="franchises_responsavel",
        verbose_name="Responsável"
    )
    
    class Meta:
        verbose_name = "Franquia de Evento"
        verbose_name_plural = "Franquias de Eventos"
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"{self.nome_franquia} - {self.empresa_contratante.nome_fantasia}"


class Licenciamento(models.Model):
    """
    Licenciamento de metodologias e processos
    """
    TIPO_LICENCA_CHOICES = [
        ('metodologia', 'Metodologia'),
        ('processo', 'Processo'),
        ('tecnologia', 'Tecnologia'),
        ('marca', 'Marca'),
        ('conhecimento', 'Conhecimento'),
    ]
    
    STATUS_CHOICES = [
        ('disponivel', 'Disponível'),
        ('licenciado', 'Licenciado'),
        ('exclusivo', 'Exclusivo'),
        ('suspenso', 'Suspenso'),
    ]
    
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="licenciamentos",
        verbose_name="Empresa Contratante"
    )
    nome_licenca = models.CharField(max_length=200, verbose_name="Nome da Licença")
    tipo = models.CharField(max_length=20, choices=TIPO_LICENCA_CHOICES, verbose_name="Tipo")
    descricao = models.TextField(verbose_name="Descrição")
    valor_licenca = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Valor da Licença")
    duracao_licenca = models.CharField(max_length=100, verbose_name="Duração da Licença")
    termos_uso = models.TextField(verbose_name="Termos de Uso")
    restricoes = models.JSONField(default=list, verbose_name="Restrições")
    beneficios_incluidos = models.JSONField(default=list, verbose_name="Benefícios Incluídos")
    suporte_incluido = models.JSONField(default=list, verbose_name="Suporte Incluído")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='disponivel', verbose_name="Status")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    responsavel = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="licenciamentos_responsavel",
        verbose_name="Responsável"
    )
    
    class Meta:
        verbose_name = "Licenciamento"
        verbose_name_plural = "Licenciamentos"
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"{self.nome_licenca} - {self.get_tipo_display()}"


class ExpansaoMercado(models.Model):
    """
    Análise e planejamento de expansão para novos mercados
    """
    TIPO_MERCADO_CHOICES = [
        ('geografico', 'Geográfico'),
        ('segmento', 'Segmento'),
        ('produto', 'Produto'),
        ('servico', 'Serviço'),
    ]
    
    STATUS_CHOICES = [
        ('analise', 'Análise'),
        ('planejamento', 'Planejamento'),
        ('implementacao', 'Implementação'),
        ('concluido', 'Concluído'),
        ('cancelado', 'Cancelado'),
    ]
    
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="expansoes_mercado",
        verbose_name="Empresa Contratante"
    )
    nome_projeto = models.CharField(max_length=200, verbose_name="Nome do Projeto")
    tipo = models.CharField(max_length=20, choices=TIPO_MERCADO_CHOICES, verbose_name="Tipo")
    descricao = models.TextField(verbose_name="Descrição")
    mercado_alvo = models.CharField(max_length=200, verbose_name="Mercado Alvo")
    analise_mercado = models.JSONField(default=dict, verbose_name="Análise de Mercado")
    estrategia_expansao = models.TextField(verbose_name="Estratégia de Expansão")
    investimento_necessario = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Investimento Necessário")
    retorno_esperado = models.JSONField(default=dict, verbose_name="Retorno Esperado")
    riscos_identificados = models.JSONField(default=list, verbose_name="Riscos Identificados")
    cronograma = models.JSONField(default=dict, verbose_name="Cronograma")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='analise', verbose_name="Status")
    responsavel = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="expansoes_mercado_responsavel",
        verbose_name="Responsável"
    )
    data_inicio = models.DateField(verbose_name="Data de Início")
    data_fim_prevista = models.DateField(verbose_name="Data de Fim Prevista")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    
    class Meta:
        verbose_name = "Expansão de Mercado"
        verbose_name_plural = "Expansões de Mercado"
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"{self.nome_projeto} - {self.mercado_alvo}"


class ParceriaEstrategica(models.Model):
    """
    Gestão de parcerias estratégicas
    """
    TIPO_PARCERIA_CHOICES = [
        ('comercial', 'Comercial'),
        ('tecnologica', 'Tecnológica'),
        ('operacional', 'Operacional'),
        ('estrategica', 'Estratégica'),
        ('distribuicao', 'Distribuição'),
    ]
    
    STATUS_CHOICES = [
        ('proposta', 'Proposta'),
        ('negociacao', 'Negociação'),
        ('ativa', 'Ativa'),
        ('suspensa', 'Suspensa'),
        ('encerrada', 'Encerrada'),
    ]
    
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="parcerias_estrategicas",
        verbose_name="Empresa Contratante"
    )
    nome_parceria = models.CharField(max_length=200, verbose_name="Nome da Parceria")
    tipo = models.CharField(max_length=20, choices=TIPO_PARCERIA_CHOICES, verbose_name="Tipo")
    parceiro_nome = models.CharField(max_length=200, verbose_name="Nome do Parceiro")
    parceiro_contato = models.JSONField(default=dict, verbose_name="Contato do Parceiro")
    descricao = models.TextField(verbose_name="Descrição")
    objetivos = models.JSONField(default=list, verbose_name="Objetivos")
    beneficios_esperados = models.JSONField(default=list, verbose_name="Benefícios Esperados")
    responsabilidades = models.JSONField(default=dict, verbose_name="Responsabilidades")
    investimento_necessario = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Investimento Necessário")
    retorno_esperado = models.JSONField(default=dict, verbose_name="Retorno Esperado")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='proposta', verbose_name="Status")
    data_inicio = models.DateField(null=True, blank=True, verbose_name="Data de Início")
    data_fim = models.DateField(null=True, blank=True, verbose_name="Data de Fim")
    responsavel = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="parcerias_estrategicas_responsavel",
        verbose_name="Responsável"
    )
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    
    class Meta:
        verbose_name = "Parceria Estratégica"
        verbose_name_plural = "Parcerias Estratégicas"
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"{self.nome_parceria} - {self.parceiro_nome}"