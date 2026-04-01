"""
CRUD web (dashboard empresa) para fichamentos e lançamentos de pagamento freelancer.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from app_eventos.forms_pagamento_freelancer import (
    FichamentoSemanaFreelancerForm,
    LancamentoDescontoFreelancerForm,
    LancamentoPagoDiarioFreelancerForm,
)
from app_eventos.models_pagamento_freelancers import (
    FichamentoSemanaFreelancer,
    LancamentoDescontoFreelancer,
    LancamentoPagoDiarioFreelancer,
)


def _empresa(request):
    if request.user.tipo_usuario not in ['admin_empresa', 'operador_empresa']:
        return None
    return request.user.empresa_contratante


def _deny(request):
    messages.error(request, 'Acesso negado.')
    return redirect('dashboard_empresa:login_empresa')


def _fichamento_empresa(request, pk):
    empresa = _empresa(request)
    if not empresa:
        return None, _deny(request)
    f = get_object_or_404(
        FichamentoSemanaFreelancer.objects.select_related('ponto_operacao'),
        pk=pk,
        empresa_contratante=empresa,
    )
    return f, None


@login_required(login_url='/empresa/login/')
def pagamento_fichamentos_lista(request):
    empresa = _empresa(request)
    if not empresa:
        return _deny(request)
    fichamentos = (
        FichamentoSemanaFreelancer.objects.filter(empresa_contratante=empresa)
        .select_related('ponto_operacao')
        .order_by('-data_fechamento')
    )
    return render(
        request,
        'dashboard_empresa/pagamento/fichamento_list.html',
        {'empresa': empresa, 'fichamentos': fichamentos, 'user': request.user},
    )


@login_required(login_url='/empresa/login/')
@require_http_methods(['GET', 'POST'])
def pagamento_fichamento_novo(request):
    empresa = _empresa(request)
    if not empresa:
        return _deny(request)
    if request.method == 'POST':
        form = FichamentoSemanaFreelancerForm(request.POST, empresa=empresa)
        if form.is_valid():
            obj = form.save(commit=False)
            try:
                obj.full_clean()
                obj.save()
            except ValidationError as e:
                for k, msgs in (e.message_dict or {}).items():
                    for m in msgs:
                        form.add_error(k if k != '__all__' else None, m)
            else:
                messages.success(request, 'Fichamento criado com sucesso.')
                return redirect('dashboard_empresa:pagamento_fichamento_detalhe', pk=obj.pk)
    else:
        form = FichamentoSemanaFreelancerForm(empresa=empresa)
    return render(
        request,
        'dashboard_empresa/pagamento/fichamento_form.html',
        {
            'empresa': empresa,
            'form': form,
            'titulo': 'Novo fichamento',
            'user': request.user,
        },
    )


@login_required(login_url='/empresa/login/')
@require_http_methods(['GET', 'POST'])
def pagamento_fichamento_editar(request, pk):
    f, err = _fichamento_empresa(request, pk)
    if err:
        return err
    empresa = _empresa(request)
    if request.method == 'POST':
        form = FichamentoSemanaFreelancerForm(request.POST, instance=f, empresa=empresa)
        if form.is_valid():
            obj = form.save(commit=False)
            try:
                obj.full_clean()
                obj.save()
            except ValidationError as e:
                for k, msgs in (e.message_dict or {}).items():
                    for m in msgs:
                        form.add_error(k if k != '__all__' else None, m)
            else:
                messages.success(request, 'Fichamento atualizado.')
                return redirect('dashboard_empresa:pagamento_fichamento_detalhe', pk=obj.pk)
    else:
        form = FichamentoSemanaFreelancerForm(instance=f, empresa=empresa)
    return render(
        request,
        'dashboard_empresa/pagamento/fichamento_form.html',
        {
            'empresa': empresa,
            'form': form,
            'titulo': 'Editar fichamento',
            'fichamento': f,
            'user': request.user,
        },
    )


@login_required(login_url='/empresa/login/')
def pagamento_fichamento_detalhe(request, pk):
    f, err = _fichamento_empresa(request, pk)
    if err:
        return err
    empresa = _empresa(request)
    lancamentos_pago = (
        f.lancamentos_pago.select_related('freelance', 'contrato_freelance__vaga')
        .order_by('data', 'freelance__nome_completo')
    )
    lancamentos_desc = (
        f.lancamentos_desconto.select_related('freelance', 'contrato_freelance__vaga')
        .order_by('data', 'id')
    )
    return render(
        request,
        'dashboard_empresa/pagamento/fichamento_detail.html',
        {
            'empresa': empresa,
            'fichamento': f,
            'lancamentos_pago': lancamentos_pago,
            'lancamentos_desc': lancamentos_desc,
            'user': request.user,
        },
    )


@login_required(login_url='/empresa/login/')
@require_http_methods(['GET', 'POST'])
def pagamento_fichamento_excluir(request, pk):
    f, err = _fichamento_empresa(request, pk)
    if err:
        return err
    empresa = _empresa(request)
    if request.method == 'POST':
        f.delete()
        messages.success(request, 'Fichamento excluído (lançamentos associados também foram removidos).')
        return redirect('dashboard_empresa:pagamento_fichamentos_lista')
    return render(
        request,
        'dashboard_empresa/pagamento/fichamento_confirm_delete.html',
        {'empresa': empresa, 'fichamento': f, 'user': request.user},
    )


def _salvar_lancamento_pago(request, fichamento, empresa, instance=None):
    form = LancamentoPagoDiarioFreelancerForm(
        request.POST,
        fichamento=fichamento,
        empresa=empresa,
        instance=instance,
    )
    if not form.is_valid():
        return form, None
    obj = form.save(commit=False)
    obj.fichamento = fichamento
    try:
        obj.full_clean()
        obj.save()
    except ValidationError as e:
        for k, msgs in (e.message_dict or {}).items():
            for m in msgs:
                form.add_error(k if k != '__all__' else None, m)
        return form, None
    return form, obj


@login_required(login_url='/empresa/login/')
@require_http_methods(['GET', 'POST'])
def pagamento_lancamento_pago_novo(request, fichamento_id):
    f, err = _fichamento_empresa(request, fichamento_id)
    if err:
        return err
    empresa = _empresa(request)
    if request.method == 'POST':
        form, obj = _salvar_lancamento_pago(request, f, empresa)
        if obj:
            messages.success(request, 'Lançamento de pago registado.')
            return redirect('dashboard_empresa:pagamento_fichamento_detalhe', pk=f.pk)
    else:
        form = LancamentoPagoDiarioFreelancerForm(fichamento=f, empresa=empresa)
    return render(
        request,
        'dashboard_empresa/pagamento/lancamento_pago_form.html',
        {
            'empresa': empresa,
            'fichamento': f,
            'form': form,
            'titulo': 'Novo lançamento — Pago (diário)',
            'user': request.user,
        },
    )


@login_required(login_url='/empresa/login/')
@require_http_methods(['GET', 'POST'])
def pagamento_lancamento_pago_editar(request, pk):
    empresa = _empresa(request)
    if not empresa:
        return _deny(request)
    lanc = get_object_or_404(
        LancamentoPagoDiarioFreelancer.objects.select_related('fichamento'),
        pk=pk,
        fichamento__empresa_contratante=empresa,
    )
    f = lanc.fichamento
    if request.method == 'POST':
        form, obj = _salvar_lancamento_pago(request, f, empresa, instance=lanc)
        if obj:
            messages.success(request, 'Lançamento atualizado.')
            return redirect('dashboard_empresa:pagamento_fichamento_detalhe', pk=f.pk)
    else:
        form = LancamentoPagoDiarioFreelancerForm(
            instance=lanc,
            fichamento=f,
            empresa=empresa,
        )
    return render(
        request,
        'dashboard_empresa/pagamento/lancamento_pago_form.html',
        {
            'empresa': empresa,
            'fichamento': f,
            'form': form,
            'titulo': 'Editar lançamento — Pago (diário)',
            'lancamento': lanc,
            'user': request.user,
        },
    )


@login_required(login_url='/empresa/login/')
@require_http_methods(['GET', 'POST'])
def pagamento_lancamento_pago_excluir(request, pk):
    empresa = _empresa(request)
    if not empresa:
        return _deny(request)
    lanc = get_object_or_404(
        LancamentoPagoDiarioFreelancer.objects.select_related('fichamento'),
        pk=pk,
        fichamento__empresa_contratante=empresa,
    )
    fid = lanc.fichamento_id
    if request.method == 'POST':
        lanc.delete()
        messages.success(request, 'Lançamento removido.')
        return redirect('dashboard_empresa:pagamento_fichamento_detalhe', pk=fid)
    return render(
        request,
        'dashboard_empresa/pagamento/lancamento_pago_confirm_delete.html',
        {'empresa': empresa, 'lancamento': lanc, 'fichamento': lanc.fichamento, 'user': request.user},
    )


def _salvar_lancamento_desc(request, fichamento, empresa, instance=None):
    form = LancamentoDescontoFreelancerForm(
        request.POST,
        fichamento=fichamento,
        empresa=empresa,
        instance=instance,
    )
    if not form.is_valid():
        return form, None
    obj = form.save(commit=False)
    obj.fichamento = fichamento
    try:
        obj.full_clean()
        obj.save()
    except ValidationError as e:
        for k, msgs in (e.message_dict or {}).items():
            for m in msgs:
                form.add_error(k if k != '__all__' else None, m)
        return form, None
    return form, obj


@login_required(login_url='/empresa/login/')
@require_http_methods(['GET', 'POST'])
def pagamento_lancamento_desconto_novo(request, fichamento_id):
    f, err = _fichamento_empresa(request, fichamento_id)
    if err:
        return err
    empresa = _empresa(request)
    if request.method == 'POST':
        form, obj = _salvar_lancamento_desc(request, f, empresa)
        if obj:
            messages.success(request, 'Desconto (vale/consumo) registado.')
            return redirect('dashboard_empresa:pagamento_fichamento_detalhe', pk=f.pk)
    else:
        form = LancamentoDescontoFreelancerForm(fichamento=f, empresa=empresa)
    return render(
        request,
        'dashboard_empresa/pagamento/lancamento_desconto_form.html',
        {
            'empresa': empresa,
            'fichamento': f,
            'form': form,
            'titulo': 'Novo desconto — Vales e consumos',
            'user': request.user,
        },
    )


@login_required(login_url='/empresa/login/')
@require_http_methods(['GET', 'POST'])
def pagamento_lancamento_desconto_editar(request, pk):
    empresa = _empresa(request)
    if not empresa:
        return _deny(request)
    lanc = get_object_or_404(
        LancamentoDescontoFreelancer.objects.select_related('fichamento'),
        pk=pk,
        fichamento__empresa_contratante=empresa,
    )
    f = lanc.fichamento
    if request.method == 'POST':
        form, obj = _salvar_lancamento_desc(request, f, empresa, instance=lanc)
        if obj:
            messages.success(request, 'Desconto atualizado.')
            return redirect('dashboard_empresa:pagamento_fichamento_detalhe', pk=f.pk)
    else:
        form = LancamentoDescontoFreelancerForm(
            instance=lanc,
            fichamento=f,
            empresa=empresa,
        )
    return render(
        request,
        'dashboard_empresa/pagamento/lancamento_desconto_form.html',
        {
            'empresa': empresa,
            'fichamento': f,
            'form': form,
            'titulo': 'Editar desconto — Vales e consumos',
            'lancamento': lanc,
            'user': request.user,
        },
    )


@login_required(login_url='/empresa/login/')
@require_http_methods(['GET', 'POST'])
def pagamento_lancamento_desconto_excluir(request, pk):
    empresa = _empresa(request)
    if not empresa:
        return _deny(request)
    lanc = get_object_or_404(
        LancamentoDescontoFreelancer.objects.select_related('fichamento'),
        pk=pk,
        fichamento__empresa_contratante=empresa,
    )
    fid = lanc.fichamento_id
    if request.method == 'POST':
        lanc.delete()
        messages.success(request, 'Desconto removido.')
        return redirect('dashboard_empresa:pagamento_fichamento_detalhe', pk=fid)
    return render(
        request,
        'dashboard_empresa/pagamento/lancamento_desconto_confirm_delete.html',
        {'empresa': empresa, 'lancamento': lanc, 'fichamento': lanc.fichamento, 'user': request.user},
    )
