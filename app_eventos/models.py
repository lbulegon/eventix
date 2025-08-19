from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

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
    ativo = models.BooleanField(default=True)
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
    cnpj = models.CharField(max_length=18, unique=True, verbose_name="CNPJ")
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
    data_vencimento = models.DateField(verbose_name="Data de Vencimento")
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
        unique_together = ['empresa_contratante', 'cnpj']

    def __str__(self):
        return f"{self.nome} - {self.empresa_contratante.nome_fantasia}"


class LocalEvento(models.Model):
    nome = models.CharField(max_length=200)
    endereco = models.CharField(max_length=255)
    capacidade = models.IntegerField()
    empresa_contratante = models.ForeignKey(
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
        return f"{self.nome} - {self.empresa_contratante.nome_fantasia}"


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
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.nome} - {self.empresa_contratante.nome_fantasia}"


class EventoFreelancerInfo(models.Model):
    """
    Informações específicas do freelancer dentro de um Evento
    """
    evento = models.OneToOneField(
        "Evento",
        on_delete=models.CASCADE,
        related_name="freelancer_info"
    )

    horario_inicio = models.TimeField(help_text="Horário de chegada")
    horario_fim = models.TimeField(help_text="Horário de saída")

    cache = models.DecimalField(max_digits=8, decimal_places=2, help_text="Valor do cachê")
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





class SetorEvento(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name="setores")
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
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
        unique_together = ['empresa_contratante', 'nome']
    
    def __str__(self):
        return f"{self.nome} - {self.empresa_contratante.nome_fantasia}"


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
    codigo_patrimonial = models.CharField(max_length=200, verbose_name="Código Patrimonial", blank=True, null=True)
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
        return f"{codigo} - {self.empresa_contratante.nome_fantasia} ({self.categoria.nome})"


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
    ], default='disponivel')
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
        unique_together = ['setor', 'equipamento']
    
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
    ], default='agendada')
    observacoes = models.TextField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Manutenção de Equipamento"
        verbose_name_plural = "Manutenções de Equipamentos"
    
    def __str__(self):
        codigo = self.equipamento.codigo_patrimonial or "Sem código"
        return f"{codigo} - {self.tipo_manutencao} ({self.status})"


class Vaga(models.Model):
    setor = models.ForeignKey(SetorEvento, on_delete=models.CASCADE, related_name="vagas")
    titulo = models.CharField(max_length=100)
    quantidade = models.PositiveIntegerField()
    remuneracao = models.DecimalField(max_digits=10, decimal_places=2)
    descricao = models.TextField(blank=True, null=True)
    ativa = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.titulo} ({self.setor.evento.nome})"


class TipoFuncao(models.Model):
    empresa_contratante = models.ForeignKey(
        EmpresaContratante,
        on_delete=models.CASCADE,
        related_name="tipos_funcao",
        verbose_name="Empresa Contratante",
        null=True,
        blank=True
    )
    nome = models.CharField(max_length=80)
    descricao = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        unique_together = ['empresa_contratante', 'nome']

    def __str__(self):
        return f"{self.nome} - {self.empresa_contratante.nome_fantasia}"


class Funcao(models.Model):
    tipo_funcao = models.ForeignKey(TipoFuncao, on_delete=models.CASCADE, related_name="funcoes")
    nome = models.CharField(max_length=80)
    descricao = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nome} ({self.tipo_funcao.nome})"


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