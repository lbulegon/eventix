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
        unique_together = ['empresa_contratante', 'nome']
    
    def __str__(self):
        return f"{self.nome} - {self.empresa_contratante.nome_fantasia}"


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
        unique_together = ['empresa_contratante', 'nome']
    
    def __str__(self):
        return f"{self.nome} - {self.empresa_contratante.nome_fantasia}"


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
        unique_together = ['empresa_contratante', 'nome']
    
    def __str__(self):
        return f"{self.nome} - {self.empresa_contratante.nome_fantasia}"


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
        return f"Backup {self.tipo_backup} - {self.empresa_contratante.nome_fantasia} - {self.data_inicio}"


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
        unique_together = ['empresa_contratante', 'nome']
    
    def __str__(self):
        return f"{self.nome} - {self.empresa_contratante.nome_fantasia}"


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
    codigo = models.CharField(max_length=50, verbose_name="Código do Insumo", blank=True, null=True)
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
        return f"{codigo} - {self.nome} ({self.empresa_contratante.nome_fantasia})"
    
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
        unique_together = ['evento', 'insumo']
    
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
        unique_together = ['setor', 'insumo_evento']
    
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
        unique_together = ['empresa_contratante', 'nome']
    
    def __str__(self):
        return f"{self.nome} - {self.empresa_contratante.nome_fantasia}"


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
        return f"{self.placa} - {self.modelo} ({self.empresa_contratante.nome_fantasia})"


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
        unique_together = ['empresa_contratante', 'nome']
    
    def __str__(self):
        return f"{self.nome} - {self.empresa_contratante.nome_fantasia}"


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
        unique_together = ['equipamento', 'tipo_controle']
    
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
        return f"{self.titulo} - {self.empresa_contratante.nome_fantasia}"


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
        return f"Dashboard - {self.empresa_contratante.nome_fantasia}"
    
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