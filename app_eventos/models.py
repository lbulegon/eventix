from django.db import models


class Empresa(models.Model):
    descricao  = models.CharField(max_length=255)
    cnpj       = models.CharField(max_length=14, unique=True)
    status     = models.CharField(max_length=1, null=True, blank=True)
    email       = models.EmailField(max_length=80)

    def __str__(self):
        return self.descricao


class Evento(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    descricao = models.CharField(max_length=80)
    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField()
    meta_cmv = models.FloatField()

    def __str__(self):
        return self.descricao

class Freelance(models.Model):
    mrx_empresa    = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    username       = models.CharField(max_length=24, unique=True)
    first_name     = models.CharField(max_length=255)
    last_name      = models.CharField(max_length=255)
    senha          = models.CharField(max_length=12)
    email          = models.EmailField(max_length=255, unique=True)
    mob_no         = models.CharField(max_length=15, null=True, blank=True)
    identidade     = models.CharField(max_length=255, null=True, blank=True)
    cpf            = models.CharField(max_length=255, null=True, blank=True)
    password_hash  = models.CharField(max_length=128)

    def __str__(self):
        return self.username
class Freelance_Evento(models.Model):
    evento      = models.ForeignKey(Evento, on_delete=models.CASCADE)
    freelance   = models.ForeignKey(Freelance, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.eve_evento.descricao} - {self.eve_freelance.username}"
