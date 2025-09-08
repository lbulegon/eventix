# app_eventos/models_freelancer_funcao.py
from django.db import models
from django.utils import timezone

class FreelancerFuncao(models.Model):
    """
    Relação direta entre Freelancer e Função
    Substitui o sistema de especialidades JSON
    """
    NIVEL_CHOICES = [
        ('iniciante', 'Iniciante'),
        ('intermediario', 'Intermediário'),
        ('avancado', 'Avançado'),
        ('expert', 'Expert'),
    ]
    
    freelancer = models.ForeignKey(
        'Freelance',
        on_delete=models.CASCADE,
        related_name='funcoes',
        verbose_name="Freelancer"
    )
    funcao = models.ForeignKey(
        'Funcao',
        on_delete=models.CASCADE,
        related_name='freelancers',
        verbose_name="Função"
    )
    nivel = models.CharField(
        max_length=20,
        choices=NIVEL_CHOICES,
        default='iniciante',
        verbose_name="Nível de Proficiência"
    )
    data_adicionada = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Adição"
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    
    class Meta:
        verbose_name = "Função do Freelancer"
        verbose_name_plural = "Funções dos Freelancers"
        unique_together = ['freelancer', 'funcao']
        ordering = ['-data_adicionada']
    
    def __str__(self):
        return f"{self.freelancer.nome} - {self.funcao.nome} ({self.get_nivel_display()})"
    
    @property
    def nivel_pontuacao(self):
        """Retorna pontuação numérica do nível"""
        niveis = {
            'iniciante': 1,
            'intermediario': 2,
            'avancado': 3,
            'expert': 4,
        }
        return niveis.get(self.nivel, 1)
