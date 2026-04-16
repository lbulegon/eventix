"""
CRUD de operação contínua no dashboard da empresa (pontos, unidades, regras, turnos, alocações).
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from app_eventos.forms_operacao_dashboard import (
    AlocacaoTurnoEditForm,
    AlocacaoTurnoNovaForm,
    DemandaFuncaoFormSet,
    PontoOperacaoForm,
    RegraRecorrenciaForm,
    TurnoOperacionalForm,
    UnidadeOperacionalForm,
)
from app_eventos.models import PontoOperacao
from app_eventos.models_operacao_continua import (
    AlocacaoTurno,
    RegraRecorrencia,
    TurnoOperacional,
    UnidadeOperacional,
    VagaTurno,
)
from app_eventos.services.motor_recorrencia_turnos import gerar_turnos_janela
from app_eventos.utils_empresa_ativa import empresa_ativa


def _empresa(request):
    if request.user.tipo_usuario not in ['admin_empresa', 'operador_empresa'] and not getattr(
        request.user, 'is_gestor_grupo', False
    ):
        return None
    return empresa_ativa(request)


def _deny(request):
    messages.error(request, 'Acesso negado.')
    return redirect('dashboard_empresa:login_empresa')


@login_required(login_url='/empresa/login/')
def operacao_pontos_lista(request):
    """Compatibilidade: cada empresa tem um único estabelecimento."""
    return redirect('dashboard_empresa:operacao_ponto_gerir')


@login_required(login_url='/empresa/login/')
@require_http_methods(['GET', 'POST'])
def operacao_ponto_novo(request):
    return redirect('dashboard_empresa:operacao_ponto_gerir')


@login_required(login_url='/empresa/login/')
@require_http_methods(['GET', 'POST'])
def operacao_ponto_gerir(request):
    """
    Único ponto de operação por empresa: criar ou editar o estabelecimento fixo.
    """
    empresa = _empresa(request)
    if not empresa:
        return _deny(request)
    ponto = PontoOperacao.objects.filter(empresa_contratante=empresa).first()
    if request.method == 'POST':
        form = PontoOperacaoForm(request.POST, instance=ponto, empresa=empresa)
        if form.is_valid():
            form.save()
            messages.success(request, 'Estabelecimento (ponto de operação) guardado.')
            return redirect('dashboard_empresa:operacao_ponto_gerir')
    else:
        form = PontoOperacaoForm(instance=ponto, empresa=empresa)
    titulo = 'Estabelecimento (ponto de operação)' if ponto else 'Cadastrar estabelecimento (ponto de operação)'
    return render(
        request,
        'dashboard_empresa/operacao/ponto_form.html',
        {
            'empresa': empresa,
            'form': form,
            'titulo': titulo,
            'ponto': ponto,
            'user': request.user,
        },
    )


@login_required(login_url='/empresa/login/')
@require_http_methods(['GET', 'POST'])
def operacao_ponto_editar(request, pk):
    empresa = _empresa(request)
    if not empresa:
        return _deny(request)
    ponto = PontoOperacao.objects.filter(empresa_contratante=empresa).first()
    if ponto is None or ponto.pk != pk:
        return redirect('dashboard_empresa:operacao_ponto_gerir')
    return redirect('dashboard_empresa:operacao_ponto_gerir')


@login_required(login_url='/empresa/login/')
@require_http_methods(['GET', 'POST'])
def operacao_ponto_excluir(request, pk):
    empresa = _empresa(request)
    if not empresa:
        return _deny(request)
    messages.info(
        request,
        'Cada empresa contratante tem um único estabelecimento; não é possível eliminá-lo por aqui.',
    )
    return redirect('dashboard_empresa:operacao_ponto_gerir')


@login_required(login_url='/empresa/login/')
def operacao_unidades_lista(request):
    empresa = _empresa(request)
    if not empresa:
        return _deny(request)
    unidades = (
        UnidadeOperacional.objects.filter(empresa_contratante=empresa)
        .select_related('evento', 'ponto_operacao')
        .order_by('-ativo', 'nome')
    )
    return render(
        request,
        'dashboard_empresa/operacao/unidade_list.html',
        {'empresa': empresa, 'unidades': unidades, 'user': request.user},
    )


@login_required(login_url='/empresa/login/')
@require_http_methods(['GET', 'POST'])
def operacao_unidade_nova(request):
    empresa = _empresa(request)
    if not empresa:
        return _deny(request)
    if request.method == 'POST':
        form = UnidadeOperacionalForm(request.POST, empresa=empresa)
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
                messages.success(request, 'Unidade operacional criada.')
                return redirect('dashboard_empresa:operacao_unidade_editar', pk=obj.pk)
    else:
        form = UnidadeOperacionalForm(empresa=empresa)
    return render(
        request,
        'dashboard_empresa/operacao/unidade_form.html',
        {
            'empresa': empresa,
            'form': form,
            'titulo': 'Nova unidade operacional',
            'user': request.user,
        },
    )


@login_required(login_url='/empresa/login/')
@require_http_methods(['GET', 'POST'])
def operacao_unidade_editar(request, pk):
    empresa = _empresa(request)
    if not empresa:
        return _deny(request)
    obj = get_object_or_404(UnidadeOperacional, pk=pk, empresa_contratante=empresa)
    if request.method == 'POST':
        form = UnidadeOperacionalForm(request.POST, instance=obj, empresa=empresa)
        if form.is_valid():
            try:
                form.instance.full_clean()
                form.save()
            except ValidationError as e:
                for k, msgs in (e.message_dict or {}).items():
                    for m in msgs:
                        form.add_error(k if k != '__all__' else None, m)
            else:
                messages.success(request, 'Unidade atualizada.')
                return redirect('dashboard_empresa:operacao_unidades_lista')
    else:
        form = UnidadeOperacionalForm(instance=obj, empresa=empresa)
    return render(
        request,
        'dashboard_empresa/operacao/unidade_form.html',
        {
            'empresa': empresa,
            'form': form,
            'titulo': 'Editar unidade operacional',
            'unidade': obj,
            'user': request.user,
        },
    )


@login_required(login_url='/empresa/login/')
@require_http_methods(['GET', 'POST'])
def operacao_unidade_excluir(request, pk):
    empresa = _empresa(request)
    if not empresa:
        return _deny(request)
    obj = get_object_or_404(UnidadeOperacional, pk=pk, empresa_contratante=empresa)
    if request.method == 'POST':
        nome = obj.nome
        obj.delete()
        messages.success(request, f'Unidade «{nome}» removida.')
        return redirect('dashboard_empresa:operacao_unidades_lista')
    return render(
        request,
        'dashboard_empresa/operacao/unidade_confirm_delete.html',
        {'empresa': empresa, 'unidade': obj, 'user': request.user},
    )


@login_required(login_url='/empresa/login/')
@require_http_methods(['POST'])
def operacao_gerar_turnos(request, unidade_pk):
    empresa = _empresa(request)
    if not empresa:
        return _deny(request)
    unidade = get_object_or_404(UnidadeOperacional, pk=unidade_pk, empresa_contratante=empresa)
    try:
        dias = int(request.POST.get('dias', 7))
    except ValueError:
        dias = 7
    dias = max(1, min(dias, 60))
    resultado = gerar_turnos_janela(unidade, dias_a_frente=dias)
    if resultado.get('erro'):
        messages.warning(request, resultado['erro'])
    else:
        messages.success(
            request,
            f"Turnos gerados: {resultado.get('turnos_criados', 0)}; "
            f"vagas: {resultado.get('vagas_turno_criadas', 0)}; "
            f"já existentes ignorados: {resultado.get('turnos_existentes_ignorados', 0)}.",
        )
    ref = request.META.get('HTTP_REFERER')
    if ref:
        return redirect(ref)
    return redirect(reverse('dashboard_empresa:operacao_unidade_editar', kwargs={'pk': unidade.pk}))


@login_required(login_url='/empresa/login/')
def operacao_regras_lista(request, unidade_pk):
    empresa = _empresa(request)
    if not empresa:
        return _deny(request)
    unidade = get_object_or_404(UnidadeOperacional, pk=unidade_pk, empresa_contratante=empresa)
    regras = RegraRecorrencia.objects.filter(unidade=unidade).prefetch_related('demandas_por_funcao__funcao')
    return render(
        request,
        'dashboard_empresa/operacao/regra_list.html',
        {'empresa': empresa, 'unidade': unidade, 'regras': regras, 'user': request.user},
    )


@login_required(login_url='/empresa/login/')
@require_http_methods(['GET', 'POST'])
def operacao_regra_nova(request, unidade_pk):
    empresa = _empresa(request)
    if not empresa:
        return _deny(request)
    unidade = get_object_or_404(UnidadeOperacional, pk=unidade_pk, empresa_contratante=empresa)
    if request.method == 'POST':
        form = RegraRecorrenciaForm(request.POST, unidade=unidade)
        if form.is_valid():
            regra = form.save()
            messages.success(request, 'Regra criada. Defina as funções e quantidades na edição.')
            return redirect('dashboard_empresa:operacao_regra_editar', pk=regra.pk)
    else:
        form = RegraRecorrenciaForm(unidade=unidade)
    return render(
        request,
        'dashboard_empresa/operacao/regra_form_simple.html',
        {
            'empresa': empresa,
            'unidade': unidade,
            'form': form,
            'titulo': 'Nova regra de recorrência',
            'user': request.user,
        },
    )


@login_required(login_url='/empresa/login/')
@require_http_methods(['GET', 'POST'])
def operacao_regra_editar(request, pk):
    empresa = _empresa(request)
    if not empresa:
        return _deny(request)
    regra = get_object_or_404(
        RegraRecorrencia.objects.select_related('unidade'),
        pk=pk,
        unidade__empresa_contratante=empresa,
    )
    unidade = regra.unidade
    if request.method == 'POST':
        form = RegraRecorrenciaForm(request.POST, instance=regra, unidade=unidade)
        fs = DemandaFuncaoFormSet(request.POST, instance=regra)
        if form.is_valid() and fs.is_valid():
            with transaction.atomic():
                form.save()
                fs.save()
            messages.success(request, 'Regra atualizada.')
            return redirect('dashboard_empresa:operacao_regras_lista', unidade_pk=unidade.pk)
    else:
        form = RegraRecorrenciaForm(instance=regra, unidade=unidade)
        fs = DemandaFuncaoFormSet(instance=regra)
    return render(
        request,
        'dashboard_empresa/operacao/regra_form.html',
        {
            'empresa': empresa,
            'unidade': unidade,
            'regra': regra,
            'form': form,
            'formset': fs,
            'titulo': 'Editar regra de recorrência',
            'user': request.user,
        },
    )


@login_required(login_url='/empresa/login/')
@require_http_methods(['GET', 'POST'])
def operacao_regra_excluir(request, pk):
    empresa = _empresa(request)
    if not empresa:
        return _deny(request)
    regra = get_object_or_404(
        RegraRecorrencia.objects.select_related('unidade'),
        pk=pk,
        unidade__empresa_contratante=empresa,
    )
    uid = regra.unidade_id
    if request.method == 'POST':
        regra.delete()
        messages.success(request, 'Regra removida.')
        return redirect('dashboard_empresa:operacao_regras_lista', unidade_pk=uid)
    return render(
        request,
        'dashboard_empresa/operacao/regra_confirm_delete.html',
        {'empresa': empresa, 'regra': regra, 'unidade': regra.unidade, 'user': request.user},
    )


@login_required(login_url='/empresa/login/')
def operacao_turnos_lista(request):
    empresa = _empresa(request)
    if not empresa:
        return _deny(request)
    unidade_id = request.GET.get('unidade')
    qs = (
        TurnoOperacional.objects.filter(unidade__empresa_contratante=empresa)
        .select_related('unidade')
        .order_by('-data', '-hora_inicio')
    )
    if unidade_id:
        qs = qs.filter(unidade_id=unidade_id)
    turnos = qs[:200]
    unidades = UnidadeOperacional.objects.filter(empresa_contratante=empresa).order_by('nome')
    return render(
        request,
        'dashboard_empresa/operacao/turno_list.html',
        {
            'empresa': empresa,
            'turnos': turnos,
            'unidades': unidades,
            'filtro_unidade': unidade_id,
            'user': request.user,
        },
    )


@login_required(login_url='/empresa/login/')
@require_http_methods(['GET', 'POST'])
def operacao_turno_novo(request):
    empresa = _empresa(request)
    if not empresa:
        return _deny(request)
    initial = {}
    uid = request.GET.get('unidade')
    if uid:
        initial['unidade'] = uid
    if request.method == 'POST':
        form = TurnoOperacionalForm(request.POST, empresa=empresa)
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
                messages.success(request, 'Turno criado.')
                return redirect('dashboard_empresa:operacao_turnos_lista')
    else:
        form = TurnoOperacionalForm(empresa=empresa, initial=initial)
    return render(
        request,
        'dashboard_empresa/operacao/turno_form.html',
        {
            'empresa': empresa,
            'form': form,
            'titulo': 'Novo turno',
            'user': request.user,
        },
    )


@login_required(login_url='/empresa/login/')
@require_http_methods(['GET', 'POST'])
def operacao_turno_editar(request, pk):
    empresa = _empresa(request)
    if not empresa:
        return _deny(request)
    obj = get_object_or_404(
        TurnoOperacional.objects.select_related('unidade'),
        pk=pk,
        unidade__empresa_contratante=empresa,
    )
    if request.method == 'POST':
        form = TurnoOperacionalForm(request.POST, instance=obj, empresa=empresa)
        if form.is_valid():
            try:
                form.instance.full_clean()
                form.save()
            except ValidationError as e:
                for k, msgs in (e.message_dict or {}).items():
                    for m in msgs:
                        form.add_error(k if k != '__all__' else None, m)
            else:
                messages.success(request, 'Turno atualizado.')
                return redirect('dashboard_empresa:operacao_turnos_lista')
    else:
        form = TurnoOperacionalForm(instance=obj, empresa=empresa)
    vagas = VagaTurno.objects.filter(turno=obj).select_related('funcao')
    return render(
        request,
        'dashboard_empresa/operacao/turno_form.html',
        {
            'empresa': empresa,
            'form': form,
            'titulo': 'Editar turno',
            'turno': obj,
            'vagas_turno': vagas,
            'user': request.user,
        },
    )


@login_required(login_url='/empresa/login/')
@require_http_methods(['GET', 'POST'])
def operacao_turno_excluir(request, pk):
    empresa = _empresa(request)
    if not empresa:
        return _deny(request)
    obj = get_object_or_404(TurnoOperacional, pk=pk, unidade__empresa_contratante=empresa)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Turno removido.')
        return redirect('dashboard_empresa:operacao_turnos_lista')
    return render(
        request,
        'dashboard_empresa/operacao/turno_confirm_delete.html',
        {'empresa': empresa, 'turno': obj, 'user': request.user},
    )


@login_required(login_url='/empresa/login/')
def operacao_alocacoes_lista(request):
    empresa = _empresa(request)
    if not empresa:
        return _deny(request)
    qs = (
        AlocacaoTurno.objects.filter(vaga_turno__turno__unidade__empresa_contratante=empresa)
        .select_related('freelance', 'vaga_turno__funcao', 'vaga_turno__turno__unidade')
    )
    unidade_id = request.GET.get('unidade')
    filtro_unidade_pk = None
    if unidade_id and str(unidade_id).isdigit():
        filtro_unidade_pk = int(unidade_id)
        qs = qs.filter(vaga_turno__turno__unidade_id=filtro_unidade_pk)
    status = request.GET.get('status')
    if status in {c[0] for c in AlocacaoTurno.STATUS_CHOICES}:
        qs = qs.filter(status=status)
    alocacoes = qs.order_by('-vaga_turno__turno__data', '-vaga_turno__turno__hora_inicio', '-criado_em')
    unidades = UnidadeOperacional.objects.filter(empresa_contratante=empresa).order_by('nome')
    return render(
        request,
        'dashboard_empresa/operacao/alocacao_list.html',
        {
            'empresa': empresa,
            'alocacoes': alocacoes,
            'unidades': unidades,
            'filtro_unidade': filtro_unidade_pk,
            'filtro_status': status or '',
            'status_choices': AlocacaoTurno.STATUS_CHOICES,
            'user': request.user,
        },
    )


@login_required(login_url='/empresa/login/')
@require_http_methods(['GET', 'POST'])
def operacao_alocacao_nova(request):
    empresa = _empresa(request)
    if not empresa:
        return _deny(request)
    initial = {}
    vaga_id = request.GET.get('vaga')
    if vaga_id:
        initial['vaga_turno'] = vaga_id
    if request.method == 'POST':
        form = AlocacaoTurnoNovaForm(request.POST, empresa=empresa)
        if form.is_valid():
            vaga = form.cleaned_data['vaga_turno']
            fl = form.cleaned_data['freelance']
            with transaction.atomic():
                vaga_locked = VagaTurno.objects.select_for_update().get(pk=vaga.pk)
                if vaga_locked.turno.unidade.empresa_contratante_id != empresa.pk:
                    form.add_error(None, 'Vaga inválida para esta empresa.')
                elif vaga_locked.quantidade_preenchida >= vaga_locked.quantidade_total:
                    form.add_error('vaga_turno', 'Esta vaga já está completa.')
                elif AlocacaoTurno.objects.filter(vaga_turno_id=vaga_locked.pk, freelance_id=fl.pk).exists():
                    form.add_error('freelance', 'Este freelancer já está alocado nesta vaga.')
                else:
                    aloc = form.save(commit=False)
                    aloc.save()
                    vaga_locked.incrementar_preenchida()
                    messages.success(request, 'Alocação registada.')
                    return redirect('dashboard_empresa:operacao_alocacoes_lista')
    else:
        form = AlocacaoTurnoNovaForm(empresa=empresa, initial=initial)
    return render(
        request,
        'dashboard_empresa/operacao/alocacao_form.html',
        {
            'empresa': empresa,
            'form': form,
            'titulo': 'Nova alocação',
            'modo': 'nova',
            'user': request.user,
        },
    )


@login_required(login_url='/empresa/login/')
@require_http_methods(['GET', 'POST'])
def operacao_alocacao_editar(request, pk):
    empresa = _empresa(request)
    if not empresa:
        return _deny(request)
    obj = get_object_or_404(
        AlocacaoTurno.objects.select_related('vaga_turno__turno__unidade', 'vaga_turno__funcao', 'freelance'),
        pk=pk,
        vaga_turno__turno__unidade__empresa_contratante=empresa,
    )
    if request.method == 'POST':
        form = AlocacaoTurnoEditForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Alocação atualizada.')
            return redirect('dashboard_empresa:operacao_alocacoes_lista')
    else:
        form = AlocacaoTurnoEditForm(instance=obj)
    return render(
        request,
        'dashboard_empresa/operacao/alocacao_form.html',
        {
            'empresa': empresa,
            'form': form,
            'titulo': 'Editar alocação',
            'modo': 'editar',
            'alocacao': obj,
            'user': request.user,
        },
    )


@login_required(login_url='/empresa/login/')
@require_http_methods(['GET', 'POST'])
def operacao_alocacao_excluir(request, pk):
    empresa = _empresa(request)
    if not empresa:
        return _deny(request)
    obj = get_object_or_404(
        AlocacaoTurno.objects.select_related('vaga_turno__turno'),
        pk=pk,
        vaga_turno__turno__unidade__empresa_contratante=empresa,
    )
    if request.method == 'POST':
        with transaction.atomic():
            vaga = VagaTurno.objects.select_for_update().get(pk=obj.vaga_turno_id)
            nome = obj.freelance.nome_completo
            obj.delete()
            vaga.decrementar_preenchida()
        messages.success(request, f'Alocação de «{nome}» removida.')
        return redirect('dashboard_empresa:operacao_alocacoes_lista')
    return render(
        request,
        'dashboard_empresa/operacao/alocacao_confirm_delete.html',
        {'empresa': empresa, 'alocacao': obj, 'user': request.user},
    )
