from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class User(AbstractUser):
    TIPO_USUARIO_CHOICES = [
        ('freelancer', 'Freelancer'),
        ('eventix', 'Eventix'),
        ('empresa', 'Empresa'),
    ]
    tipo_usuario = models.CharField(max_length=20, choices=TIPO_USUARIO_CHOICES, default='freelancer')

    def __str__(self):
        return self.username
# app_eventos/models.py
from django.db import models
from django.conf import settings

class TipoEmpresa(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Tipo de Empresa"
        verbose_name_plural = "Tipos de Empresas"

    def __str__(self):
        return self.nome


class Empresa(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="empresas"
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

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"

    def __str__(self):
        return self.nome


class LocalEvento(models.Model):
    nome        = models.CharField(max_length=200)
    endereco    = models.CharField(max_length=255)
    capacidade  = models.IntegerField()
    empresa_proprietaria = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        limit_choices_to={'tipo': 'proprietaria'},
        related_name="locais"
    )

    def __str__(self):
        return f"{self.nome} - {self.empresa_proprietaria.nome}"


class Evento(models.Model):
    nome              = models.CharField(max_length=200)
    data_inicio       = models.DateField()
    data_fim          = models.DateField()
    descricao         = models.TextField(blank=True, null=True)
    local             = models.ForeignKey(LocalEvento, on_delete=models.CASCADE, related_name="eventos")
    empresa_produtora = models.ForeignKey(
        Empresa,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        limit_choices_to={'tipo': 'produtora'},
        related_name="eventos_produzidos"
    )
    empresa_contratante = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        limit_choices_to={'tipo': 'contratante_mao_obra'},
        related_name="eventos_cadastrados"
    )

    def __str__(self):
        return self.nome


class SetorEvento(models.Model):
    evento     = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name="setores")
    nome       = models.CharField(max_length=100)
    descricao  = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nome} - {self.evento.nome}"


class Vaga(models.Model):
    setor         = models.ForeignKey(SetorEvento, on_delete=models.CASCADE, related_name="vagas")
    titulo        = models.CharField(max_length=100)
    quantidade    = models.PositiveIntegerField()
    remuneracao   = models.DecimalField(max_digits=10, decimal_places=2)
    descricao     = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.titulo} ({self.setor.evento.nome})"


class TipoFuncao(models.Model):
    nome      = models.CharField(max_length=80, unique=True)  # Ex: Atendimento, Segurança, Produção, Limpeza
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nome


class Funcao(models.Model):
    tipo_funcao = models.ForeignKey(TipoFuncao, on_delete=models.CASCADE, related_name="funcoes")
    nome        = models.CharField(max_length=80)  # ex.: Cachorrista, Chapista, Atendente, Caixa, Segurança
    descricao   = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nome} ({self.tipo_funcao.nome})"

from django.conf import settings
from django.db import models

from django.conf import settings
from django.db import models

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
    documento = models.CharField(max_length=50, blank=True, null=True)  # pode ser CPF
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

    # Vínculo
    tipo_vinculo = models.CharField(max_length=20, choices=VINCULO_CHOICES, blank=True, null=True)
    data_admissao = models.DateField(blank=True, null=True)
    data_rescisao = models.DateField(blank=True, null=True)
    cargo = models.CharField(max_length=100, blank=True, null=True)
    departamento = models.CharField(max_length=100, blank=True, null=True)
    valor_hora = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    carga_horaria = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)  # horas
    escala_trabalho = models.TextField(blank=True, null=True)

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

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    cadastro_completo = models.BooleanField(default=False)  # Status do cadastro
    
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


class ContratacaoFreelance(models.Model):
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