"""
Grupo empresarial: agrega várias empresas contratantes (CNPJs distintos).

Níveis de gestão (produto):
- Gestor do grupo: supervisiona todas as operações das empresas ligadas ao grupo.
- Gestor da empresa / ponto: utilizadores admin_empresa / operador_empresa ligados a
  uma EmpresaContratante específica (quadro local), como já existia no sistema.

Cada EmpresaContratante continua a ser o tenant operacional (eventos, vagas, pontos);
o grupo apenas agrupa e permite visão transversal aos gestores do grupo.
"""
from django.db import models


class GrupoEmpresarial(models.Model):
    """Ex.: Grupo Mister X — pode ter ou não CNPJ de holding; agrega N empresas no Eventix."""

    nome = models.CharField(max_length=255, verbose_name='Nome do grupo')
    nome_fantasia = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Nome fantasia',
    )
    cnpj = models.CharField(
        max_length=18,
        blank=True,
        null=True,
        verbose_name='CNPJ (opcional)',
        help_text='CNPJ da holding / grupo, se existir.',
    )
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Grupo empresarial'
        verbose_name_plural = 'Grupos empresariais'
        ordering = ['nome']

    def __str__(self):
        return self.nome_fantasia or self.nome
