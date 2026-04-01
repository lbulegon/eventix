"""
Pagamento de freelancers por estabelecimento (PontoOperacao) dentro do tenant (EmpresaContratante).
Período semanal de 7 dias; o último dia do período é o "fechamento", configurável por dia da semana.
"""
from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

# datetime.weekday(): segunda=0 … domingo=6
DIA_SEMANA_FECHAMENTO_CHOICES = [
    (0, 'Segunda-feira'),
    (1, 'Terça-feira'),
    (2, 'Quarta-feira'),
    (3, 'Quinta-feira'),
    (4, 'Sexta-feira'),
    (5, 'Sábado'),
    (6, 'Domingo'),
]


class FichamentoSemanaFreelancer(models.Model):
    """
    Uma semana de pagamento por estabelecimento: 7 dias consecutivos terminando em ``data_fechamento``.
    O dia da semana de fechamento vem do estabelecimento ou pode ser sobrescrito neste registro.
    """
    empresa_contratante = models.ForeignKey(
        'EmpresaContratante',
        on_delete=models.CASCADE,
        related_name='fichamentos_pagamento_freelancer',
        verbose_name='Empresa (tenant)',
    )
    ponto_operacao = models.ForeignKey(
        'PontoOperacao',
        on_delete=models.CASCADE,
        related_name='fichamentos_pagamento_freelancer',
        verbose_name='Estabelecimento',
    )
    dia_semana_fechamento = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        choices=DIA_SEMANA_FECHAMENTO_CHOICES,
        verbose_name='Dia de fechamento (sobrescreve o estabelecimento)',
        help_text='Se vazio, usa o dia configurado no ponto de operação.',
    )
    data_fechamento = models.DateField(
        verbose_name='Data de fechamento do período',
        help_text='Último dia da semana de pagamento (7 dias), deve ser o mesmo dia da semana configurado.',
    )
    observacoes = models.TextField(blank=True, null=True, verbose_name='Observações')
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Fichamento semanal (pagamento freelancer)'
        verbose_name_plural = 'Fichamentos semanais (pagamento freelancer)'
        ordering = ['-data_fechamento', 'ponto_operacao_id']
        constraints = [
            models.UniqueConstraint(
                fields=['empresa_contratante', 'ponto_operacao', 'data_fechamento'],
                name='uniq_fichamento_semana_por_estabelecimento',
            ),
        ]
        indexes = [
            models.Index(fields=['empresa_contratante', 'ponto_operacao', 'data_fechamento']),
        ]

    def __str__(self):
        return f'{self.ponto_operacao} — fechamento {self.data_fechamento}'

    def dia_fechamento_resolvido(self):
        if self.dia_semana_fechamento is not None:
            return self.dia_semana_fechamento
        if self.ponto_operacao_id and self.ponto_operacao.dia_semana_fechamento is not None:
            return self.ponto_operacao.dia_semana_fechamento
        return None

    @property
    def data_inicio_periodo(self):
        if not self.data_fechamento:
            return None
        return self.data_fechamento - timedelta(days=6)

    def clean(self):
        if self.ponto_operacao_id and self.empresa_contratante_id:
            if self.ponto_operacao.empresa_contratante_id != self.empresa_contratante_id:
                raise ValidationError(
                    'O estabelecimento deve pertencer à mesma empresa (tenant) do fichamento.'
                )
        dia = self.dia_fechamento_resolvido()
        if dia is None:
            raise ValidationError(
                'Defina o dia da semana de fechamento no estabelecimento ou neste fichamento.'
            )
        if self.data_fechamento and self.data_fechamento.weekday() != dia:
            raise ValidationError(
                {
                    'data_fechamento': (
                        'A data deve ser um dia da semana igual ao dia de fechamento configurado '
                        f'({dict(DIA_SEMANA_FECHAMENTO_CHOICES).get(dia, dia)}).'
                    )
                }
            )


def _periodo_lancamento_valido(fichamento, data):
    if not fichamento or not data:
        return True
    ini = fichamento.data_inicio_periodo
    fim = fichamento.data_fechamento
    if ini is None or fim is None:
        return True
    return ini <= data <= fim


def validar_contrato_com_fichamento(fichamento, freelance, contrato):
    """
    Garante que o contrato (freelancer + vaga aprovada/contratada) é coerente com o fichamento e o freelancer do lançamento.
    """
    if contrato is None:
        return
    if contrato.freelance_id != freelance.id:
        raise ValidationError(
            {'contrato_freelance': 'O contrato não corresponde ao freelancer deste lançamento.'}
        )
    if contrato.vaga.empresa_contratante_id != fichamento.empresa_contratante_id:
        raise ValidationError(
            {'contrato_freelance': 'A vaga do contrato não pertence ao mesmo tenant do fichamento.'}
        )
    if fichamento.ponto_operacao_id and contrato.vaga.ponto_operacao_id:
        if contrato.vaga.ponto_operacao_id != fichamento.ponto_operacao_id:
            raise ValidationError(
                {
                    'contrato_freelance': (
                        'A vaga do contrato é de outro estabelecimento (ponto de operação) que o fichamento.'
                    )
                }
            )


class LancamentoPagoDiarioFreelancer(models.Model):
    """Valor pago por dia (ou folga) no período do fichamento."""
    fichamento = models.ForeignKey(
        FichamentoSemanaFreelancer,
        on_delete=models.CASCADE,
        related_name='lancamentos_pago',
        verbose_name='Fichamento',
    )
    freelance = models.ForeignKey(
        'Freelance',
        on_delete=models.CASCADE,
        related_name='lancamentos_pago_fichamento',
        verbose_name='Freelancer',
    )
    data = models.DateField(verbose_name='Data')
    valor_bruto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Valor bruto (pago)',
    )
    eh_folga = models.BooleanField(default=False, verbose_name='Folga')
    contrato_freelance = models.ForeignKey(
        'ContratoFreelance',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lancamentos_pago',
        verbose_name='Contrato (vaga contratada)',
        help_text='Opcional: vínculo com a vaga em que o freelancer foi aprovado e contratado.',
    )

    class Meta:
        verbose_name = 'Lançamento pago (diário)'
        verbose_name_plural = 'Lançamentos pagos (diários)'
        ordering = ['data', 'freelance_id']
        constraints = [
            models.UniqueConstraint(
                fields=['fichamento', 'freelance', 'data'],
                name='uniq_pago_diario_por_freelance_data',
            ),
        ]

    def __str__(self):
        return f'{self.freelance} — {self.data} — R$ {self.valor_bruto}'

    def clean(self):
        if self.eh_folga and self.valor_bruto and self.valor_bruto != Decimal('0.00'):
            raise ValidationError({'valor_bruto': 'Em folga o valor deve ser zero.'})
        if self.fichamento_id and self.data and not _periodo_lancamento_valido(self.fichamento, self.data):
            raise ValidationError({'data': 'Data fora do período de 7 dias deste fichamento.'})
        if self.fichamento_id and self.contrato_freelance_id and self.freelance_id:
            validar_contrato_com_fichamento(self.fichamento, self.freelance, self.contrato_freelance)


class LancamentoDescontoFreelancer(models.Model):
    """Vales, consumos e outros descontos na semana do fichamento."""
    TIPO_CHOICES = [
        ('vale', 'Vale'),
        ('consumo', 'Consumo'),
        ('outro', 'Outro'),
    ]
    fichamento = models.ForeignKey(
        FichamentoSemanaFreelancer,
        on_delete=models.CASCADE,
        related_name='lancamentos_desconto',
        verbose_name='Fichamento',
    )
    freelance = models.ForeignKey(
        'Freelance',
        on_delete=models.CASCADE,
        related_name='lancamentos_desconto_fichamento',
        verbose_name='Freelancer',
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name='Tipo')
    valor = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Valor do desconto',
        help_text='Valor positivo a abater do bruto.',
    )
    descricao = models.CharField(max_length=255, blank=True, null=True, verbose_name='Descrição')
    data = models.DateField(
        blank=True,
        null=True,
        verbose_name='Data de referência',
        help_text='Opcional; use para alinhar ao dia do vale/consumo.',
    )
    contrato_freelance = models.ForeignKey(
        'ContratoFreelance',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lancamentos_desconto',
        verbose_name='Contrato (vaga contratada)',
        help_text='Opcional: desconto associado ao contrato de uma vaga específica.',
    )

    class Meta:
        verbose_name = 'Lançamento de desconto (vale/consumo)'
        verbose_name_plural = 'Lançamentos de desconto (vales/consumos)'
        ordering = ['fichamento_id', 'freelance_id', 'id']

    def __str__(self):
        return f'{self.get_tipo_display()} — {self.freelance} — R$ {self.valor}'

    def clean(self):
        if self.valor is not None and self.valor <= 0:
            raise ValidationError({'valor': 'Informe um valor maior que zero.'})
        if self.fichamento_id and self.data and not _periodo_lancamento_valido(self.fichamento, self.data):
            raise ValidationError({'data': 'Data fora do período de 7 dias deste fichamento.'})
        if self.fichamento_id and self.contrato_freelance_id and self.freelance_id:
            validar_contrato_com_fichamento(self.fichamento, self.freelance, self.contrato_freelance)
