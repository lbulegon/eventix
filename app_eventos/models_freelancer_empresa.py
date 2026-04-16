"""
Freelancers associados a uma empresa contratante como quem já prestou serviço.

Após a primeira contratação efetiva com aquele estabelecimento, o freelancer
entra neste cadastro (par único empresa + freelancer), que serve de base para
planilha de pagamento, histórico operacional e contexto em que a empresa o
avalia (por exemplo via FeedbackFreelancer por evento/empresa).
"""
from django.db import models


class FreelancerPrestacaoServico(models.Model):
    """
    Registo de que o freelancer já trabalhou / presta serviço para a empresa,
    ou foi cadastrado explicitamente por ela (ex.: criação via API do tenant).

    Um registo por par (empresa, freelancer). Tipicamente criado na primeira
    contratação, ao constar no fichamento ou pelo cadastro manual no contexto
    da empresa; consolida o vínculo operacional com aquele estabelecimento.
    """
    empresa_contratante = models.ForeignKey(
        'EmpresaContratante',
        on_delete=models.CASCADE,
        related_name='freelancers_prestacao_servico',
        verbose_name='Empresa',
    )
    freelance = models.ForeignKey(
        'Freelance',
        on_delete=models.CASCADE,
        related_name='prestacao_servico_empresas',
        verbose_name='Freelancer',
    )
    ativo = models.BooleanField(default=True, verbose_name='Ativo na lista')
    observacoes = models.TextField(blank=True, null=True, verbose_name='Observações')
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Registado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Freelancer com histórico na empresa'
        verbose_name_plural = 'Freelancers com histórico na empresa'
        ordering = ['empresa_contratante_id', 'freelance__nome_completo']
        constraints = [
            models.UniqueConstraint(
                fields=['empresa_contratante', 'freelance'],
                name='uniq_freelancer_prestacao_por_empresa',
            ),
        ]
        indexes = [
            models.Index(fields=['empresa_contratante', 'ativo']),
        ]

    def __str__(self):
        return f'{self.freelance.nome_completo} @ {self.empresa_contratante.nome_fantasia}'
