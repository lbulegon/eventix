"""
Operação híbrida Eventix: unidades operacionais (evento pontual vs operação contínua),
regras de recorrência, turnos materializados, vagas por turno e alocações.

Convenção dias_semana (JSON): inteiros 0–6 no formato Python weekday()
(segunda=0 … domingo=6), alinhado a date.weekday().
"""
from django.core.exceptions import ValidationError
from django.db import models


class UnidadeOperacional(models.Model):
    """Agrupa demanda de trabalho: evento fechado ou operação contínua (ex.: restaurante)."""

    TIPO_EVENTO = 'evento'
    TIPO_OPERACAO = 'operacao'
    TIPO_CHOICES = [
        (TIPO_EVENTO, 'Evento (pontual)'),
        (TIPO_OPERACAO, 'Operação contínua'),
    ]

    empresa_contratante = models.ForeignKey(
        'EmpresaContratante',
        on_delete=models.CASCADE,
        related_name='unidades_operacionais',
        verbose_name='Empresa (tenant)',
    )
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True, null=True, verbose_name='Descrição')

    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name='Modo de operação')

    evento = models.ForeignKey(
        'Evento',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='unidades_operacionais',
        verbose_name='Evento',
    )
    ponto_operacao = models.ForeignKey(
        'PontoOperacao',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='unidades_operacionais',
        verbose_name='Estabelecimento / ponto de operação',
    )

    data_inicio = models.DateTimeField(null=True, blank=True, verbose_name='Início (opcional)')
    data_fim = models.DateTimeField(null=True, blank=True, verbose_name='Fim (opcional)')

    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Unidade operacional'
        verbose_name_plural = 'Unidades operacionais'
        ordering = ['-criado_em']
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(tipo='evento', evento__isnull=False, ponto_operacao__isnull=True)
                    | models.Q(tipo='operacao', ponto_operacao__isnull=False, evento__isnull=True)
                ),
                name='unidade_operacional_evento_ou_ponto',
            ),
        ]

    def __str__(self):
        return f'{self.nome} ({self.get_tipo_display()})'

    def clean(self):
        super().clean()
        if self.tipo == self.TIPO_EVENTO and not self.evento_id:
            raise ValidationError({'evento': 'Unidade tipo evento exige um evento.'})
        if self.tipo == self.TIPO_OPERACAO and not self.ponto_operacao_id:
            raise ValidationError(
                {'ponto_operacao': 'Unidade tipo operação contínua exige estabelecimento (ponto de operação).'}
            )
        if self.ponto_operacao_id and self.empresa_contratante_id:
            if self.ponto_operacao.empresa_contratante_id != self.empresa_contratante_id:
                raise ValidationError('O ponto de operação deve ser da mesma empresa contratante.')
        if self.evento_id and self.empresa_contratante_id:
            if self.evento.empresa_contratante_id != self.empresa_contratante_id:
                raise ValidationError('O evento deve ser da mesma empresa contratante.')


class RegraRecorrencia(models.Model):
    """Padrão semanal + faixa horária que o motor usa para gerar turnos."""

    unidade = models.ForeignKey(
        UnidadeOperacional,
        on_delete=models.CASCADE,
        related_name='regras_recorrencia',
        verbose_name='Unidade operacional',
    )
    nome = models.CharField(max_length=120, blank=True, verbose_name='Nome da regra')
    dias_semana = models.JSONField(
        default=list,
        help_text='Lista de dias 0–6 (segunda=0 … domingo=6, como date.weekday()).',
    )
    hora_inicio = models.TimeField(verbose_name='Hora início')
    hora_fim = models.TimeField(verbose_name='Hora fim')
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Regra de recorrência'
        verbose_name_plural = 'Regras de recorrência'
        ordering = ['unidade_id', 'hora_inicio']

    def __str__(self):
        return self.nome or f'Regra #{self.pk} ({self.unidade.nome})'

    def clean(self):
        super().clean()
        if not isinstance(self.dias_semana, list) or not self.dias_semana:
            raise ValidationError({'dias_semana': 'Informe ao menos um dia da semana (0–6).'})
        for d in self.dias_semana:
            if not isinstance(d, int) or d < 0 or d > 6:
                raise ValidationError({'dias_semana': 'Cada dia deve ser inteiro entre 0 e 6.'})


class RegraRecorrenciaFuncao(models.Model):
    """Quantidade por função (tipo de vaga) dentro de uma regra de recorrência."""

    regra = models.ForeignKey(
        RegraRecorrencia,
        on_delete=models.CASCADE,
        related_name='demandas_por_funcao',
        verbose_name='Regra',
    )
    funcao = models.ForeignKey(
        'Funcao',
        on_delete=models.CASCADE,
        related_name='regras_recorrencia_demanda',
        verbose_name='Função',
    )
    quantidade = models.PositiveIntegerField(default=1, verbose_name='Quantidade por turno')

    class Meta:
        verbose_name = 'Demanda por função (regra)'
        verbose_name_plural = 'Demandas por função (regras)'
        constraints = [
            models.UniqueConstraint(fields=['regra', 'funcao'], name='uniq_regra_funcao_demanda'),
        ]

    def __str__(self):
        return f'{self.funcao.nome} x{self.quantidade}'

    def clean(self):
        super().clean()
        u_emp = self.regra.unidade.empresa_contratante_id
        if self.funcao.empresa_contratante_id and u_emp and self.funcao.empresa_contratante_id != u_emp:
            raise ValidationError({'funcao': 'A função deve ser da mesma empresa da unidade.'})


class TurnoOperacional(models.Model):
    """
    Turno concreto (data + intervalo). Gerado por recorrência ou criado manualmente.
    """

    ORIGEM_RECORRENCIA = 'recorrencia'
    ORIGEM_MANUAL = 'manual'
    ORIGEM_CHOICES = [
        (ORIGEM_RECORRENCIA, 'Recorrência'),
        (ORIGEM_MANUAL, 'Manual'),
    ]

    STATUS_ABERTO = 'aberto'
    STATUS_ENCERRADO = 'encerrado'
    STATUS_CANCELADO = 'cancelado'
    STATUS_CHOICES = [
        (STATUS_ABERTO, 'Aberto'),
        (STATUS_ENCERRADO, 'Encerrado'),
        (STATUS_CANCELADO, 'Cancelado'),
    ]

    unidade = models.ForeignKey(
        UnidadeOperacional,
        on_delete=models.CASCADE,
        related_name='turnos',
        verbose_name='Unidade',
    )
    data = models.DateField(verbose_name='Data')
    hora_inicio = models.TimeField(verbose_name='Hora início')
    hora_fim = models.TimeField(verbose_name='Hora fim')

    origem = models.CharField(
        max_length=20,
        choices=ORIGEM_CHOICES,
        default=ORIGEM_RECORRENCIA,
        verbose_name='Origem',
    )
    regra_recorrencia = models.ForeignKey(
        RegraRecorrencia,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='turnos_gerados',
        verbose_name='Regra que gerou o turno',
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ABERTO,
        verbose_name='Status',
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Turno operacional'
        verbose_name_plural = 'Turnos operacionais'
        ordering = ['data', 'hora_inicio']
        constraints = [
            models.UniqueConstraint(
                fields=['unidade', 'data', 'hora_inicio', 'hora_fim'],
                name='uniq_turno_unidade_data_intervalo',
            ),
        ]
        indexes = [
            models.Index(fields=['unidade', 'data', 'status']),
        ]

    def __str__(self):
        return f'{self.data} {self.hora_inicio}-{self.hora_fim} — {self.unidade.nome}'


class VagaTurno(models.Model):
    """Vagas por função dentro de um turno (capacidade e preenchimento)."""

    turno = models.ForeignKey(
        TurnoOperacional,
        on_delete=models.CASCADE,
        related_name='vagas_turno',
        verbose_name='Turno',
    )
    funcao = models.ForeignKey(
        'Funcao',
        on_delete=models.CASCADE,
        related_name='vagas_turno',
        verbose_name='Função',
    )
    quantidade_total = models.PositiveIntegerField(verbose_name='Vagas totais')
    quantidade_preenchida = models.PositiveIntegerField(default=0, verbose_name='Preenchidas')

    class Meta:
        verbose_name = 'Vaga do turno'
        verbose_name_plural = 'Vagas dos turnos'
        constraints = [
            models.UniqueConstraint(fields=['turno', 'funcao'], name='uniq_vaga_turno_funcao'),
            models.CheckConstraint(
                check=models.Q(quantidade_preenchida__lte=models.F('quantidade_total')),
                name='vaga_turno_preenchida_lte_total',
            ),
        ]

    def __str__(self):
        return f'{self.turno} — {self.funcao.nome} ({self.quantidade_preenchida}/{self.quantidade_total})'

    @property
    def vagas_disponiveis(self):
        return self.quantidade_total - self.quantidade_preenchida

    def incrementar_preenchida(self):
        if self.quantidade_preenchida < self.quantidade_total:
            self.quantidade_preenchida += 1
            self.save(update_fields=['quantidade_preenchida'])

    def decrementar_preenchida(self):
        if self.quantidade_preenchida > 0:
            self.quantidade_preenchida -= 1
            self.save(update_fields=['quantidade_preenchida'])


class AlocacaoTurno(models.Model):
    """Freelancer alocado a uma vaga de turno (substitui fluxo de candidatura quando aplicável)."""

    STATUS_PENDENTE = 'pendente'
    STATUS_CONFIRMADO = 'confirmado'
    STATUS_CANCELADO = 'cancelado'
    STATUS_CONCLUIDO = 'concluido'
    STATUS_CHOICES = [
        (STATUS_PENDENTE, 'Pendente'),
        (STATUS_CONFIRMADO, 'Confirmado'),
        (STATUS_CANCELADO, 'Cancelado'),
        (STATUS_CONCLUIDO, 'Concluído'),
    ]

    vaga_turno = models.ForeignKey(
        VagaTurno,
        on_delete=models.CASCADE,
        related_name='alocacoes',
        verbose_name='Vaga do turno',
    )
    freelance = models.ForeignKey(
        'Freelance',
        on_delete=models.CASCADE,
        related_name='alocacoes_turno',
        verbose_name='Freelancer',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDENTE)
    observacoes = models.TextField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Alocação (turno)'
        verbose_name_plural = 'Alocações (turnos)'
        ordering = ['-criado_em']
        constraints = [
            models.UniqueConstraint(
                fields=['vaga_turno', 'freelance'],
                name='uniq_alocacao_vaga_turno_freelance',
            ),
        ]

    def __str__(self):
        return f'{self.freelance.nome_completo} — {self.vaga_turno}'
