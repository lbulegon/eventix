"""Formulários de operação contínua no dashboard da empresa."""
from django import forms
from django.forms import inlineformset_factory

from app_eventos.models import EmpresaContratante, Evento, Funcao, PontoOperacao
from app_eventos.models_operacao_continua import (
    RegraRecorrencia,
    RegraRecorrenciaFuncao,
    TurnoOperacional,
    UnidadeOperacional,
)

DIAS_SEMANA_CHOICES = [
    (0, 'Segunda'),
    (1, 'Terça'),
    (2, 'Quarta'),
    (3, 'Quinta'),
    (4, 'Sexta'),
    (5, 'Sábado'),
    (6, 'Domingo'),
]


class UnidadeOperacionalForm(forms.ModelForm):
    class Meta:
        model = UnidadeOperacional
        fields = [
            'nome',
            'descricao',
            'tipo',
            'evento',
            'ponto_operacao',
            'data_inicio',
            'data_fim',
            'ativo',
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'evento': forms.Select(attrs={'class': 'form-select'}),
            'ponto_operacao': forms.Select(attrs={'class': 'form-select'}),
            'data_inicio': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'data_fim': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, empresa: EmpresaContratante, **kwargs):
        super().__init__(*args, **kwargs)
        self._empresa = empresa
        self.fields['evento'].queryset = Evento.objects.filter(empresa_contratante=empresa).order_by('-data_inicio')
        self.fields['evento'].required = False
        self.fields['ponto_operacao'].queryset = PontoOperacao.objects.filter(
            empresa_contratante=empresa,
            ativo=True,
        ).order_by('nome')
        self.fields['ponto_operacao'].required = False
        self.fields['descricao'].required = False

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.empresa_contratante = self._empresa
        if commit:
            obj.save()
        return obj


class RegraRecorrenciaForm(forms.ModelForm):
    dias_semana = forms.MultipleChoiceField(
        label='Dias da semana',
        choices=DIAS_SEMANA_CHOICES,
        required=True,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
    )

    class Meta:
        model = RegraRecorrencia
        fields = ['nome', 'hora_inicio', 'hora_fim', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'hora_inicio': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_fim': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, unidade: UnidadeOperacional, **kwargs):
        super().__init__(*args, **kwargs)
        self._unidade = unidade
        if self.instance and self.instance.pk and self.instance.dias_semana:
            self.fields['dias_semana'].initial = [str(x) for x in self.instance.dias_semana]

    def clean_dias_semana(self):
        vals = self.cleaned_data.get('dias_semana') or []
        return sorted({int(x) for x in vals})

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.unidade = self._unidade
        obj.dias_semana = self.cleaned_data['dias_semana']
        if commit:
            obj.save()
        return obj


class DemandaFuncaoForm(forms.ModelForm):
    class Meta:
        model = RegraRecorrenciaFuncao
        fields = ['funcao', 'quantidade']
        widgets = {
            'funcao': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        regra = getattr(self.instance, 'regra', None)
        if regra and getattr(regra, 'unidade_id', None):
            emp = regra.unidade.empresa_contratante
            self.fields['funcao'].queryset = Funcao.objects.filter(
                empresa_contratante=emp,
                ativo=True,
            ).order_by('nome')
        self.fields['funcao'].required = True


DemandaFuncaoFormSet = inlineformset_factory(
    RegraRecorrencia,
    RegraRecorrenciaFuncao,
    form=DemandaFuncaoForm,
    extra=1,
    can_delete=True,
    min_num=0,
    validate_min=False,
)


class TurnoOperacionalForm(forms.ModelForm):
    class Meta:
        model = TurnoOperacional
        fields = [
            'unidade',
            'data',
            'hora_inicio',
            'hora_fim',
            'origem',
            'regra_recorrencia',
            'status',
        ]
        widgets = {
            'unidade': forms.Select(attrs={'class': 'form-select'}),
            'data': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'hora_inicio': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_fim': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'origem': forms.Select(attrs={'class': 'form-select'}),
            'regra_recorrencia': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, empresa: EmpresaContratante, **kwargs):
        super().__init__(*args, **kwargs)
        self._empresa = empresa
        qs = UnidadeOperacional.objects.filter(empresa_contratante=empresa)
        self.fields['unidade'].queryset = qs.order_by('nome')
        self.fields['regra_recorrencia'].queryset = RegraRecorrencia.objects.filter(
            unidade__empresa_contratante=empresa,
        ).select_related('unidade').order_by('unidade__nome', 'hora_inicio')
        self.fields['regra_recorrencia'].required = False
