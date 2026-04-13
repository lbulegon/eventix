"""
Registros manuais de presença/falta para cálculo de score de confiabilidade (Freelance).
Extensível para integração futura com FreelancerPrestacaoServico e ranking por empresa.
"""
from django.db import models


class RegistroPresencaFreelancer(models.Model):
    STATUS_PRESENTE = 'presente'
    STATUS_FALTA_AVISO = 'falta_com_aviso'
    STATUS_FALTA_SEM_AVISO = 'falta_sem_aviso'

    STATUS_CHOICES = [
        (STATUS_PRESENTE, 'Presente'),
        (STATUS_FALTA_AVISO, 'Falta com aviso'),
        (STATUS_FALTA_SEM_AVISO, 'Falta sem aviso'),
    ]

    freelance = models.ForeignKey(
        'Freelance',
        on_delete=models.CASCADE,
        related_name='registros_presenca',
        verbose_name='Freelancer',
    )
    empresa = models.ForeignKey(
        'EmpresaContratante',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='registros_presenca_freelancer',
        verbose_name='Empresa',
        help_text='Opcional; recomendado quando o registo é feito no contexto de uma empresa.',
    )
    data = models.DateField(verbose_name='Data')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, verbose_name='Status')
    observacao = models.TextField(blank=True, null=True, verbose_name='Observação')
    pontuacao_aplicada = models.BooleanField(
        default=False,
        verbose_name='Pontuação já aplicada',
        help_text='Uso interno: garante idempotência ao aplicar o score no Freelance.',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')

    class Meta:
        verbose_name = 'Registo de presença (freelancer)'
        verbose_name_plural = 'Registos de presença (freelancers)'
        ordering = ['-data', '-created_at']
        indexes = [
            models.Index(fields=['freelance', 'data']),
            models.Index(fields=['empresa', 'data']),
        ]

    def __str__(self):
        return f'{self.freelance_id} {self.data} {self.status}'
