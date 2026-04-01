"""Formulários de tarifas de diária por função e estabelecimento."""
from django import forms

from app_eventos.models import EmpresaContratante, Funcao, PontoOperacao
from app_eventos.models_tarifa_diaria_turno import DataCalendarioTarifa, TarifaDiariaPorFuncaoPonto


class TarifaDiariaPorFuncaoPontoForm(forms.ModelForm):
    class Meta:
        model = TarifaDiariaPorFuncaoPonto
        fields = [
            'ponto_operacao',
            'funcao',
            'valor_turno_dia',
            'valor_turno_noite',
            'valor_noite_especial',
            'hora_corte_dia_noite',
            'hora_fim_madrugada_noite',
            'ativo',
            'observacoes',
        ]
        widgets = {
            'ponto_operacao': forms.Select(attrs={'class': 'form-select'}),
            'funcao': forms.Select(attrs={'class': 'form-select'}),
            'valor_turno_dia': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'valor_turno_noite': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'valor_noite_especial': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'hora_corte_dia_noite': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_fim_madrugada_noite': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observacoes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

    def __init__(self, *args, empresa: EmpresaContratante, **kwargs):
        super().__init__(*args, **kwargs)
        self._empresa = empresa
        qs_ponto = PontoOperacao.objects.filter(empresa_contratante=empresa, ativo=True).order_by('nome')
        qs_funcao = Funcao.objects.filter(empresa_contratante=empresa, ativo=True).order_by('nome')
        self.fields['ponto_operacao'].queryset = qs_ponto
        self.fields['funcao'].queryset = qs_funcao

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.empresa_contratante = self._empresa
        if commit:
            obj.save()
        return obj


class DataCalendarioTarifaForm(forms.ModelForm):
    class Meta:
        model = DataCalendarioTarifa
        fields = ['ponto_operacao', 'data', 'descricao', 'ativo']
        widgets = {
            'ponto_operacao': forms.Select(attrs={'class': 'form-select'}),
            'data': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, empresa: EmpresaContratante, **kwargs):
        super().__init__(*args, **kwargs)
        self._empresa = empresa
        self.fields['ponto_operacao'].queryset = PontoOperacao.objects.filter(
            empresa_contratante=empresa,
            ativo=True,
        ).order_by('nome')
        self.fields['ponto_operacao'].required = True

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.empresa_contratante = self._empresa
        if commit:
            obj.save()
        return obj
