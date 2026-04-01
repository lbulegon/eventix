"""
Tarifas de diária por função (especialidade) e estabelecimento, por tipo de turno.

Usado para alinhar oferta de vagas (``Vaga.remuneracao``) a turnos diurnos/noturnos
e picos (sexta/sábado noite, vésperas de feriado cadastradas).
"""
from django.core.exceptions import ValidationError
from django.db import models


class TarifaDiariaPorFuncaoPonto(models.Model):
    """
    Valores de referência por dia / noite / noite especial (fim de semana + vésperas).

    A classificação \"noite\" usa ``hora_corte_dia_noite`` (ex.: a partir das 18h)
    e madrugada antes de ``hora_fim_madrugada_noite`` (ex.: antes das 6h = noite).
    """

    empresa_contratante = models.ForeignKey(
        'EmpresaContratante',
        on_delete=models.CASCADE,
        related_name='tarifas_diaria_turno',
        verbose_name='Empresa (tenant)',
    )
    ponto_operacao = models.ForeignKey(
        'PontoOperacao',
        on_delete=models.CASCADE,
        related_name='tarifas_diaria_turno',
        verbose_name='Estabelecimento',
    )
    funcao = models.ForeignKey(
        'Funcao',
        on_delete=models.CASCADE,
        related_name='tarifas_diaria_turno',
        verbose_name='Função / especialidade',
    )

    valor_turno_dia = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Diária turno dia',
        help_text='Ex.: turno comercial / manhã-tarde conforme corte horário.',
    )
    valor_turno_noite = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Diária turno noite',
    )
    valor_noite_especial = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Noite especial',
        help_text='Sexta e sábado à noite, e noites em datas de véspera cadastradas.',
    )

    hora_corte_dia_noite = models.TimeField(
        default='18:00',
        verbose_name='A partir desta hora = noite (mesmo dia)',
    )
    hora_fim_madrugada_noite = models.TimeField(
        default='06:00',
        verbose_name='Antes desta hora = ainda noite (madrugada)',
    )

    ativo = models.BooleanField(default=True)
    observacoes = models.TextField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tarifa diária por função (estabelecimento)'
        verbose_name_plural = 'Tarifas diárias por função (estabelecimento)'
        constraints = [
            models.UniqueConstraint(
                fields=['empresa_contratante', 'ponto_operacao', 'funcao'],
                name='uniq_tarifa_ponto_funcao',
            ),
        ]

    def __str__(self):
        return f'{self.funcao.nome} @ {self.ponto_operacao.nome}'

    def clean(self):
        super().clean()
        if self.ponto_operacao_id and self.empresa_contratante_id:
            if self.ponto_operacao.empresa_contratante_id != self.empresa_contratante_id:
                raise ValidationError('O estabelecimento deve ser da mesma empresa.')
        if self.funcao_id and self.empresa_contratante_id:
            if self.funcao.empresa_contratante_id and self.funcao.empresa_contratante_id != self.empresa_contratante_id:
                raise ValidationError('A função deve ser da mesma empresa contratante.')


class DataCalendarioTarifa(models.Model):
    """
    Datas em que a noite deve usar ``valor_noite_especial`` (ex.: véspera de feriado).
    Por estabelecimento (cadastre a mesma data em mais de um ponto se necessário).
    """

    empresa_contratante = models.ForeignKey(
        'EmpresaContratante',
        on_delete=models.CASCADE,
        related_name='datas_calendario_tarifa',
        verbose_name='Empresa',
    )
    ponto_operacao = models.ForeignKey(
        'PontoOperacao',
        on_delete=models.CASCADE,
        related_name='datas_calendario_tarifa',
        verbose_name='Estabelecimento',
    )
    data = models.DateField(verbose_name='Data')
    descricao = models.CharField(max_length=200, blank=True, verbose_name='Descrição', help_text='Ex.: Véspera de Natal')
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Data especial (tarifa)'
        verbose_name_plural = 'Datas especiais (tarifas)'
        ordering = ['data']
        constraints = [
            models.UniqueConstraint(
                fields=['ponto_operacao', 'data'],
                name='uniq_data_tarifa_ponto_data',
            ),
        ]

    def __str__(self):
        return f'{self.data} — {self.descricao or "data especial"}'

    def clean(self):
        super().clean()
        if self.ponto_operacao_id and self.empresa_contratante_id:
            if self.ponto_operacao.empresa_contratante_id != self.empresa_contratante_id:
                raise ValidationError('O estabelecimento deve ser da mesma empresa.')
