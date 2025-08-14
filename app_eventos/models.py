
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# ========== AUTH ==========

class User(AbstractUser):
    ROLE_CHOICES = [
        ("EVENTIX", "Eventix"),
        ("CONTRATANTE", "Contratante"),
        ("FREELANCER", "Freelancer"),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    email = models.EmailField(unique=True)
    cpf = models.CharField(max_length=14, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)

    REQUIRED_FIELDS = ["email", "role"]

    def __str__(self):
        return f"{self.username} ({self.role})"


# ========== CORE ==========

class Empresa(models.Model):
    descricao  = models.CharField(max_length=255)
    cnpj       = models.CharField(max_length=18, unique=True)
    status     = models.CharField(max_length=1, null=True, blank=True)  # "A" ativo etc.
    email      = models.EmailField(max_length=80)

    def __str__(self):
        return self.descricao


class EmpresaUser(models.Model):
    ROLE = [("OWNER", "Proprietário"), ("MANAGER", "Gestor")]
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="membros")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="empresas")
    papel = models.CharField(max_length=20, choices=ROLE, default="MANAGER")

    class Meta:
        unique_together = ("empresa", "user")

# --- NOVO: Local do evento (venue) ---
class LocalEvento(models.Model):
    TIPO_CHOICES = [
        ("ARENA", "Arena / Ginásio"),
        ("PARQUE", "Parque / Área Aberta"),
        ("CASA_SHOW", "Casa de Show"),
        ("SALAO", "Salão / Centro de Eventos"),
        ("ESTABELECIMENTO", "Estabelecimento Comercial"),
        ("OUTRO", "Outro"),
    ]
    STATUS_CHOICES = [
        ("ATIVO", "Ativo"),
        ("INATIVO", "Inativo"),
        ("MANUTENCAO", "Em manutenção"),
    ]

    empresa = models.ForeignKey(
        Empresa, on_delete=models.CASCADE, related_name="locais",
        help_text="Empresa responsável/locatária do local (opcional)."
    )
    nome = models.CharField(max_length=120)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default="OUTRO")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ATIVO")

    # Endereço
    logradouro = models.CharField(max_length=120, blank=True, null=True)
    numero = models.CharField(max_length=20, blank=True, null=True)
    complemento = models.CharField(max_length=80, blank=True, null=True)
    bairro = models.CharField(max_length=80, blank=True, null=True)
    cidade = models.CharField(max_length=80, blank=True, null=True)
    estado = models.CharField(max_length=2, blank=True, null=True)  # UF
    cep = models.CharField(max_length=12, blank=True, null=True)
    pais = models.CharField(max_length=60, blank=True, null=True, default="Brasil")

    # Geo (sem GeoDjango, simples lat/lng)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    # Operacional
    capacidade_pessoas = models.PositiveIntegerField(blank=True, null=True)
    possui_estacionamento = models.BooleanField(default=False)
    possui_acessibilidade = models.BooleanField(default=True)
    observacoes = models.TextField(blank=True, null=True)

    # Contato
    contato_nome = models.CharField(max_length=120, blank=True, null=True)
    contato_email = models.EmailField(max_length=120, blank=True, null=True)
    contato_telefone = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        verbose_name = "Local de Evento"
        verbose_name_plural = "Locais de Evento"
        ordering = ["nome"]
        indexes = [
            models.Index(fields=["cidade", "estado"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return self.nome

class Evento(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="eventos")
    local = models.ForeignKey("LocalEvento", on_delete=models.PROTECT, related_name="eventos", null=True, blank=True)
    descricao = models.CharField(max_length=80)
    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField()
    meta_cmv = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.descricao


class Setor(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name="setores")
    nome = models.CharField(max_length=80)   # ex.: "Dogão 1", "Hambúrguer", "Bebidas"
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nome} ({self.evento.descricao})"


# app_eventos/models.py

class CategoriaFuncao(models.Model):
    nome = models.CharField(max_length=80, unique=True)  # Ex.: "Alimentação e Bebidas"
    descricao = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Categoria de Função"
        verbose_name_plural = "Categorias de Função"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Funcao(models.Model):
    categoria = models.ForeignKey(
        CategoriaFuncao,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="funcoes"
    )
    nome = models.CharField(max_length=80)  # Ex.: Cachorrista, Chapista
    descricao = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Função"
        verbose_name_plural = "Funções"
        ordering = ["nome"]
        unique_together = ("categoria", "nome")

    def __str__(self):
        return self.nome


class Vaga(models.Model):
    setor = models.ForeignKey(Setor, on_delete=models.CASCADE, related_name="vagas")
    funcao = models.ForeignKey(Funcao, on_delete=models.CASCADE, related_name="vagas")
    quantidade = models.PositiveIntegerField(default=1)
    descricao = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("aberta", "Aberta"),
            ("fechada", "Fechada"),
            ("em_andamento", "Em andamento"),
            ("finalizada", "Finalizada"),
        ],
        default="aberta"
    )

    def __str__(self):
        return f"{self.funcao.nome} - {self.setor.nome} ({self.quantidade} vagas)"


class FreelanceProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="freelance_profile")
    identidade = models.CharField(max_length=255, null=True, blank=True)
    cpf = models.CharField(max_length=14, null=True, blank=True)
    mob_no = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Candidatura(models.Model):
    vaga = models.ForeignKey(Vaga, on_delete=models.CASCADE, related_name="candidaturas")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="candidaturas")  # freelancer
    status = models.CharField(
        max_length=20,
        choices=[
            ("pendente", "Pendente"),
            ("confirmada", "Confirmada pelo candidato"),
            ("aceita_empresa", "Aceita pela empresa"),
            ("recusada", "Recusada"),
            ("cancelada", "Cancelada"),
        ],
        default="pendente"
    )
    data_candidatura = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("vaga", "user")

    def __str__(self):
        return f"{self.user} -> {self.vaga}"


class AlocacaoFinal(models.Model):
    candidatura = models.OneToOneField(Candidatura, on_delete=models.CASCADE, related_name="alocacao_final")
    setor = models.ForeignKey(Setor, on_delete=models.CASCADE)
    funcao = models.ForeignKey(Funcao, on_delete=models.CASCADE)
    data_alocacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.candidatura.user} em {self.setor.nome} - {self.funcao.nome}"
