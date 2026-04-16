"""Formulários do dashboard empresa para fichamentos e lançamentos de pagamento."""
from decimal import Decimal

from django import forms

from app_eventos.models import ContratoFreelance, EmpresaContratante, Freelance, PontoOperacao
from app_eventos.models_pagamento_freelancers import (
    FichamentoSemanaFreelancer,
    LancamentoDescontoFreelancer,
    LancamentoPagoDiarioFreelancer,
)
from app_eventos.models_freelancer_empresa import FreelancerPrestacaoServico


def _freelances_empresa(empresa: EmpresaContratante):
    ids = FreelancerPrestacaoServico.objects.filter(
        empresa_contratante=empresa,
        ativo=True,
    ).values_list('freelance_id', flat=True)
    return Freelance.objects.filter(pk__in=ids).order_by('nome_completo')


def _contratos_para_fichamento(fichamento: FichamentoSemanaFreelancer, freelance_id=None):
    qs = ContratoFreelance.objects.filter(
        status='ativo',
        vaga__empresa_contratante_id=fichamento.empresa_contratante_id,
    ).select_related('vaga', 'freelance')
    if fichamento.ponto_operacao_id:
        qs = qs.filter(vaga__ponto_operacao_id=fichamento.ponto_operacao_id)
    if freelance_id:
        qs = qs.filter(freelance_id=freelance_id)
    return qs.order_by('-data_contratacao')


class FichamentoSemanaFreelancerForm(forms.ModelForm):
    class Meta:
        model = FichamentoSemanaFreelancer
        fields = ['ponto_operacao', 'dia_semana_fechamento', 'data_fechamento', 'observacoes']
        widgets = {
            'data_fechamento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'ponto_operacao': forms.Select(attrs={'class': 'form-select'}),
            'dia_semana_fechamento': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, empresa: EmpresaContratante, **kwargs):
        super().__init__(*args, **kwargs)
        self._empresa = empresa
        qs_ponto = PontoOperacao.objects.filter(
            empresa_contratante=empresa,
            ativo=True,
        ).order_by('nome')
        self.fields['ponto_operacao'].queryset = qs_ponto
        self.fields['ponto_operacao'].required = True
        if qs_ponto.count() == 1:
            self.fields['ponto_operacao'].widget = forms.HiddenInput()
            if not getattr(self.instance, 'pk', None):
                self.fields['ponto_operacao'].initial = qs_ponto.first().pk
        self.fields['dia_semana_fechamento'].required = False
        self.fields['dia_semana_fechamento'].empty_label = 'Usar o dia configurado no estabelecimento'

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.empresa_contratante = self._empresa
        if commit:
            obj.save()
        return obj


class LancamentoPagoDiarioFreelancerForm(forms.ModelForm):
    class Meta:
        model = LancamentoPagoDiarioFreelancer
        fields = ['freelance', 'data', 'valor_bruto', 'eh_folga', 'contrato_freelance']
        widgets = {
            'freelance': forms.Select(attrs={'class': 'form-select'}),
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'valor_bruto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'eh_folga': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'contrato_freelance': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, fichamento: FichamentoSemanaFreelancer, empresa: EmpresaContratante, **kwargs):
        super().__init__(*args, **kwargs)
        self._fichamento = fichamento
        self.fields['freelance'].queryset = _freelances_empresa(empresa)
        self.fields['freelance'].label_from_instance = lambda obj: obj.nome_completo
        fid = None
        if self.instance.pk:
            fid = self.instance.freelance_id
        elif self.data.get('freelance'):
            try:
                fid = int(self.data.get('freelance'))
            except (TypeError, ValueError):
                fid = None
        self.fields['contrato_freelance'].queryset = _contratos_para_fichamento(fichamento, fid)
        self.fields['contrato_freelance'].required = False
        self.fields['contrato_freelance'].empty_label = '— Nenhum (opcional) —'
        if not self.fields['freelance'].queryset.exists():
            self.fields['freelance'].help_text = (
                'Nenhum freelancer na lista desta empresa. Inclua em "histórico" (prestou serviço) ou use o Admin.'
            )

    def clean(self):
        cleaned = super().clean()
        eh = cleaned.get('eh_folga')
        valor = cleaned.get('valor_bruto')
        if eh and valor is not None and valor != Decimal('0'):
            raise forms.ValidationError({'valor_bruto': 'Em folga o valor deve ser zero.'})
        return cleaned


class LancamentoDescontoFreelancerForm(forms.ModelForm):
    class Meta:
        model = LancamentoDescontoFreelancer
        fields = ['freelance', 'tipo', 'valor', 'descricao', 'data', 'contrato_freelance']
        widgets = {
            'freelance': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'contrato_freelance': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, fichamento: FichamentoSemanaFreelancer, empresa: EmpresaContratante, **kwargs):
        super().__init__(*args, **kwargs)
        self._fichamento = fichamento
        self.fields['freelance'].queryset = _freelances_empresa(empresa)
        self.fields['freelance'].label_from_instance = lambda obj: obj.nome_completo
        fid = None
        if self.instance.pk:
            fid = self.instance.freelance_id
        elif self.data.get('freelance'):
            try:
                fid = int(self.data.get('freelance'))
            except (TypeError, ValueError):
                fid = None
        self.fields['contrato_freelance'].queryset = _contratos_para_fichamento(fichamento, fid)
        self.fields['contrato_freelance'].required = False
        self.fields['contrato_freelance'].empty_label = '— Nenhum (opcional) —'
        self.fields['data'].required = False
        self.fields['descricao'].required = False
        if not self.fields['freelance'].queryset.exists():
            self.fields['freelance'].help_text = (
                'Nenhum freelancer na lista desta empresa. Inclua em "histórico" (prestou serviço) ou use o Admin.'
            )
