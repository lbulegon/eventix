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


class Freelance(models.Model):
    usuario       = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nome_completo = models.CharField(max_length=255)
    telefone      = models.CharField(max_length=20, blank=True, null=True)
    documento     = models.CharField(max_length=50, blank=True, null=True)
    habilidades   = models.TextField(blank=True, null=True)

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