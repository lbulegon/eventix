"""Formulários do dashboard da empresa (sem depender do Admin)."""
from django import forms

from app_eventos.models import EmpresaContratante, ModuloSistema


class EmpresaContratanteConfigForm(forms.ModelForm):
    """Dados da empresa contratante editáveis pelo próprio tenant."""

    modulos_contratados = forms.ModelMultipleChoiceField(
        label='Módulos adicionais contratados',
        queryset=ModuloSistema.objects.filter(ativo=True, modulo_basico=False).order_by('nome'),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        help_text='Módulos básicos já vêm no plano; marque aqui os extras contratados.',
    )

    class Meta:
        model = EmpresaContratante
        fields = [
            'nome',
            'razao_social',
            'nome_fantasia',
            'cnpj',
            'telefone',
            'email',
            'website',
            'cep',
            'logradouro',
            'numero',
            'complemento',
            'bairro',
            'cidade',
            'uf',
            'modo_dashboard',
            'modulos_contratados',
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'razao_social': forms.TextInput(attrs={'class': 'form-control'}),
            'nome_fantasia': forms.TextInput(attrs={'class': 'form-control'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'cep': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 9}),
            'logradouro': forms.TextInput(attrs={'class': 'form-control'}),
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'complemento': forms.TextInput(attrs={'class': 'form-control'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'uf': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 2}),
            'modo_dashboard': forms.Select(attrs={'class': 'form-select'}),
        }
