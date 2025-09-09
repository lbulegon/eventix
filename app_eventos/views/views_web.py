from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q, Sum, F
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator
from datetime import timedelta
import json

from app_eventos.models import (
    Evento, Vaga, Candidatura, ContratoFreelance, 
    EquipamentoSetor, ManutencaoEquipamento, EmpresaContratante, 
    Freelance, Fornecedor, SetorEvento, Equipamento, CategoriaEquipamento,
    DespesaEvento, ReceitaEvento, CategoriaFinanceira
)


def web_dashboard(request):
    """
    Dashboard principal da interface web
    """
    if not request.user.is_authenticated:
        # Renderizar uma página de boas-vindas em vez de redirecionar
        return render(request, 'web_admin/welcome.html')
    
    user = request.user
    
    if user.is_admin_sistema:
        return redirect('admin_admin_dashboard')
    elif user.is_empresa_user:
        return redirect('admin_empresa_dashboard')
    elif user.is_freelancer:
        return redirect('admin_freelancer_dashboard')
    else:
        messages.error(request, 'Tipo de usuário não reconhecido.')
        return redirect('/admin/login/?next=/admin-web/')


@login_required
def web_empresa_dashboard(request):
    """
    Dashboard da empresa na interface web
    """
    if not request.user.is_empresa_user:
        messages.error(request, 'Acesso negado.')
        return redirect('home')
    
    empresa = request.user.empresa_contratante
    if not empresa:
        messages.error(request, 'Usuário não está associado a nenhuma empresa.')
        return redirect('home')
    
    # Estatísticas gerais
    eventos_ativos = Evento.objects.filter(empresa_contratante=empresa, ativo=True).count()
    eventos_total = Evento.objects.filter(empresa_contratante=empresa).count()
    
    vagas_ativas = Vaga.objects.filter(setor__evento__empresa_contratante=empresa, ativa=True).count()
    candidaturas_pendentes = Candidatura.objects.filter(
        vaga__setor__evento__empresa_contratante=empresa, status='pendente'
    ).count()
    
    contratos_ativos = ContratoFreelance.objects.filter(
        vaga__setor__evento__empresa_contratante=empresa, status='ativo'
    ).count()
    
    equipamentos_manutencao = ManutencaoEquipamento.objects.filter(
        equipamento__empresa_contratante=empresa, status='em_andamento'
    ).count()
    
    # Eventos recentes
    eventos_recentes = Evento.objects.filter(
        empresa_contratante=empresa
    ).order_by('-data_inicio')[:5]
    
    # Candidaturas recentes
    candidaturas_recentes = Candidatura.objects.filter(
        vaga__setor__evento__empresa_contratante=empresa
    ).select_related('freelance', 'vaga__setor__evento').order_by('-data_candidatura')[:5]
    
    # Equipamentos em manutenção
    equipamentos_manutencao_list = ManutencaoEquipamento.objects.filter(
        equipamento__empresa_contratante=empresa, status='em_andamento'
    ).select_related('equipamento', 'responsavel')[:5]
    
    context = {
        'empresa': empresa,
        'eventos_ativos': eventos_ativos,
        'eventos_total': eventos_total,
        'vagas_ativas': vagas_ativas,
        'candidaturas_pendentes': candidaturas_pendentes,
        'contratos_ativos': contratos_ativos,
        'equipamentos_manutencao': equipamentos_manutencao,
        'eventos_recentes': eventos_recentes,
        'candidaturas_recentes': candidaturas_recentes,
        'equipamentos_manutencao_list': equipamentos_manutencao_list,
    }
    
    return render(request, 'web/dashboard_empresa.html', context)


@login_required
def web_eventos_list(request):
    """
    Lista de eventos da empresa
    """
    if not request.user.is_empresa_user:
        messages.error(request, 'Acesso negado.')
        return redirect('home')
    
    empresa = request.user.empresa_contratante
    if not empresa:
        messages.error(request, 'Usuário não está associado a nenhuma empresa.')
        return redirect('home')
    
    # Filtros
    status = request.GET.get('status', 'todos')
    search = request.GET.get('search', '')
    
    eventos = Evento.objects.filter(empresa_contratante=empresa)
    
    if status == 'ativos':
        eventos = eventos.filter(ativo=True)
    elif status == 'inativos':
        eventos = eventos.filter(ativo=False)
    
    if search:
        eventos = eventos.filter(
            Q(nome__icontains=search) | 
            Q(descricao__icontains=search) |
            Q(local__nome__icontains=search)
        )
    
    # Paginação
    paginator = Paginator(eventos.order_by('-data_inicio'), 10)
    page_number = request.GET.get('page')
    eventos_page = paginator.get_page(page_number)
    
    context = {
        'eventos': eventos_page,
        'status': status,
        'search': search,
        'empresa': empresa,
    }
    
    return render(request, 'web/eventos_list.html', context)


@login_required
def web_evento_detail(request, evento_id):
    """
    Detalhes de um evento específico
    """
    evento = get_object_or_404(Evento, id=evento_id)
    
    # Verificar permissão
    if not request.user.is_admin_sistema and evento.empresa_contratante != request.user.empresa_contratante:
        messages.error(request, 'Acesso negado a este evento.')
        return redirect('web_empresa_dashboard')
    
    # Estatísticas do evento
    setores = SetorEvento.objects.filter(evento=evento)
    vagas_total = Vaga.objects.filter(setor__evento=evento).count()
    vagas_ativas = Vaga.objects.filter(setor__evento=evento, ativa=True).count()
    candidaturas_total = Candidatura.objects.filter(vaga__setor__evento=evento).count()
    candidaturas_pendentes = Candidatura.objects.filter(vaga__setor__evento=evento, status='pendente').count()
    
    # Equipamentos
    equipamentos_setor = EquipamentoSetor.objects.filter(setor__evento=evento)
    equipamentos_total = equipamentos_setor.count()
    equipamentos_em_manutencao = ManutencaoEquipamento.objects.filter(
        equipamento__equipamentosetor__setor__evento=evento, status='em_andamento'
    ).count()
    
    # Financeiro
    despesas_total = DespesaEvento.objects.filter(evento=evento).aggregate(
        total=Sum('valor')
    )['total'] or 0
    
    receitas_total = ReceitaEvento.objects.filter(evento=evento).aggregate(
        total=Sum('valor')
    )['total'] or 0
    
    context = {
        'evento': evento,
        'setores': setores,
        'vagas_total': vagas_total,
        'vagas_ativas': vagas_ativas,
        'candidaturas_total': candidaturas_total,
        'candidaturas_pendentes': candidaturas_pendentes,
        'equipamentos_total': equipamentos_total,
        'equipamentos_em_manutencao': equipamentos_manutencao,
        'despesas_total': despesas_total,
        'receitas_total': receitas_total,
        'lucro': receitas_total - despesas_total,
    }
    
    return render(request, 'web/evento_detail.html', context)


@login_required
def web_equipamentos_list(request):
    """
    Lista de equipamentos da empresa
    """
    if not request.user.is_empresa_user:
        messages.error(request, 'Acesso negado.')
        return redirect('home')
    
    empresa = request.user.empresa_contratante
    if not empresa:
        messages.error(request, 'Usuário não está associado a nenhuma empresa.')
        return redirect('home')
    
    # Filtros
    categoria_id = request.GET.get('categoria')
    status = request.GET.get('status', 'todos')
    search = request.GET.get('search', '')
    
    equipamentos = Equipamento.objects.filter(empresa_contratante=empresa)
    
    if categoria_id:
        equipamentos = equipamentos.filter(categoria_id=categoria_id)
    
    if status == 'ativos':
        equipamentos = equipamentos.filter(ativo=True)
    elif status == 'inativos':
        equipamentos = equipamentos.filter(ativo=False)
    
    if search:
        equipamentos = equipamentos.filter(
            Q(nome__icontains=search) | 
            Q(marca__icontains=search) |
            Q(modelo__icontains=search)
        )
    
    # Paginação
    paginator = Paginator(equipamentos.order_by('nome'), 12)
    page_number = request.GET.get('page')
    equipamentos_page = paginator.get_page(page_number)
    
    # Categorias para filtro
    categorias = CategoriaEquipamento.objects.all()
    
    context = {
        'equipamentos': equipamentos_page,
        'categorias': categorias,
        'categoria_id': categoria_id,
        'status': status,
        'search': search,
        'empresa': empresa,
    }
    
    return render(request, 'web/equipamentos_list.html', context)


@login_required
def web_equipamento_detail(request, equipamento_id):
    """
    Detalhes de um equipamento específico
    """
    equipamento = get_object_or_404(Equipamento, id=equipamento_id)
    
    # Verificar permissão
    if not request.user.is_admin_sistema and equipamento.empresa_contratante != request.user.empresa_contratante:
        messages.error(request, 'Acesso negado a este equipamento.')
        return redirect('web_equipamentos_list')
    
    # Setores onde o equipamento é usado
    setores_uso = EquipamentoSetor.objects.filter(equipamento=equipamento).select_related('setor__evento')
    
    # Manutenções
    manutencoes = ManutencaoEquipamento.objects.filter(equipamento=equipamento).order_by('-data_inicio')
    
    # Estatísticas
    manutencoes_total = manutencoes.count()
    manutencoes_em_andamento = manutencoes.filter(status='em_andamento').count()
    custo_total_manutencao = manutencoes.aggregate(total=Sum('custo'))['total'] or 0
    
    context = {
        'equipamento': equipamento,
        'setores_uso': setores_uso,
        'manutencoes': manutencoes[:10],  # Últimas 10 manutenções
        'manutencoes_total': manutencoes_total,
        'manutencoes_em_andamento': manutencoes_em_andamento,
        'custo_total_manutencao': custo_total_manutencao,
    }
    
    return render(request, 'web/equipamento_detail.html', context)


@login_required
def web_vagas_list(request):
    """
    Lista de vagas da empresa
    """
    if not request.user.is_empresa_user:
        messages.error(request, 'Acesso negado.')
        return redirect('home')
    
    empresa = request.user.empresa_contratante
    if not empresa:
        messages.error(request, 'Usuário não está associado a nenhuma empresa.')
        return redirect('home')
    
    # Filtros
    status = request.GET.get('status', 'todas')
    evento_id = request.GET.get('evento')
    search = request.GET.get('search', '')
    
    vagas = Vaga.objects.filter(setor__evento__empresa_contratante=empresa)
    
    if status == 'ativas':
        vagas = vagas.filter(ativa=True)
    elif status == 'inativas':
        vagas = vagas.filter(ativa=False)
    
    if evento_id:
        vagas = vagas.filter(setor__evento_id=evento_id)
    
    if search:
        vagas = vagas.filter(
            Q(titulo__icontains=search) | 
            Q(descricao__icontains=search) |
            Q(setor__nome__icontains=search)
        )
    
    # Paginação
    paginator = Paginator(vagas.select_related('setor__evento', 'funcao').order_by('-data_criacao'), 10)
    page_number = request.GET.get('page')
    vagas_page = paginator.get_page(page_number)
    
    # Eventos para filtro
    eventos = Evento.objects.filter(empresa_contratante=empresa, ativo=True)
    
    context = {
        'vagas': vagas_page,
        'eventos': eventos,
        'status': status,
        'evento_id': evento_id,
        'search': search,
        'empresa': empresa,
    }
    
    return render(request, 'web/vagas_list.html', context)


@login_required
def web_vaga_detail(request, vaga_id):
    """
    Detalhes de uma vaga específica
    """
    vaga = get_object_or_404(Vaga, id=vaga_id)
    
    # Verificar permissão
    if not request.user.is_admin_sistema and vaga.setor.evento.empresa_contratante != request.user.empresa_contratante:
        messages.error(request, 'Acesso negado a esta vaga.')
        return redirect('web_vagas_list')
    
    # Candidaturas
    candidaturas = Candidatura.objects.filter(vaga=vaga).select_related('freelance__usuario').order_by('-data_candidatura')
    
    # Estatísticas
    candidaturas_total = candidaturas.count()
    candidaturas_pendentes = candidaturas.filter(status='pendente').count()
    candidaturas_aprovadas = candidaturas.filter(status='aprovada').count()
    candidaturas_rejeitadas = candidaturas.filter(status='rejeitada').count()
    
    context = {
        'vaga': vaga,
        'candidaturas': candidaturas,
        'candidaturas_total': candidaturas_total,
        'candidaturas_pendentes': candidaturas_pendentes,
        'candidaturas_aprovadas': candidaturas_aprovadas,
        'candidaturas_rejeitadas': candidaturas_rejeitadas,
    }
    
    return render(request, 'web/vaga_detail.html', context)


@login_required
def web_candidaturas_list(request):
    """
    Lista de candidaturas da empresa
    """
    if not request.user.is_empresa_user:
        messages.error(request, 'Acesso negado.')
        return redirect('home')
    
    empresa = request.user.empresa_contratante
    if not empresa:
        messages.error(request, 'Usuário não está associado a nenhuma empresa.')
        return redirect('home')
    
    # Filtros
    status = request.GET.get('status', 'todas')
    evento_id = request.GET.get('evento')
    vaga_id = request.GET.get('vaga')
    
    candidaturas = Candidatura.objects.filter(vaga__setor__evento__empresa_contratante=empresa)
    
    if status != 'todas':
        candidaturas = candidaturas.filter(status=status)
    
    if evento_id:
        candidaturas = candidaturas.filter(vaga__setor__evento_id=evento_id)
    
    if vaga_id:
        candidaturas = candidaturas.filter(vaga_id=vaga_id)
    
    # Paginação
    paginator = Paginator(
        candidaturas.select_related('freelance__usuario', 'vaga__setor__evento', 'vaga__funcao').order_by('-data_candidatura'), 
        15
    )
    page_number = request.GET.get('page')
    candidaturas_page = paginator.get_page(page_number)
    
    # Filtros disponíveis
    eventos = Evento.objects.filter(empresa_contratante=empresa, ativo=True)
    vagas = Vaga.objects.filter(setor__evento__empresa_contratante=empresa, ativa=True)
    
    context = {
        'candidaturas': candidaturas_page,
        'eventos': eventos,
        'vagas': vagas,
        'status': status,
        'evento_id': evento_id,
        'vaga_id': vaga_id,
        'empresa': empresa,
    }
    
    return render(request, 'web/candidaturas_list.html', context)


@login_required
def web_financeiro_dashboard(request):
    """
    Dashboard financeiro da empresa
    """
    if not request.user.is_empresa_user:
        messages.error(request, 'Acesso negado.')
        return redirect('home')
    
    empresa = request.user.empresa_contratante
    if not empresa:
        messages.error(request, 'Usuário não está associado a nenhuma empresa.')
        return redirect('home')
    
    # Período (últimos 12 meses)
    data_inicio = timezone.now() - timedelta(days=365)
    
    # Despesas e receitas por evento
    eventos_financeiro = Evento.objects.filter(
        empresa_contratante=empresa,
        data_inicio__gte=data_inicio
    ).annotate(
        total_despesas=Sum('despesas__valor'),
        total_receitas=Sum('receitas__valor')
    ).order_by('-data_inicio')[:10]
    
    # Categorias financeiras
    categorias_despesas = CategoriaFinanceira.objects.filter(
        despesasevento__evento__empresa_contratante=empresa,
        despesasevento__evento__data_inicio__gte=data_inicio
    ).annotate(
        total=Sum('despesasevento__valor')
    ).order_by('-total')[:10]
    
    # Totais gerais
    total_despesas = DespesaEvento.objects.filter(
        evento__empresa_contratante=empresa,
        evento__data_inicio__gte=data_inicio
    ).aggregate(total=Sum('valor'))['total'] or 0
    
    total_receitas = ReceitaEvento.objects.filter(
        evento__empresa_contratante=empresa,
        evento__data_inicio__gte=data_inicio
    ).aggregate(total=Sum('valor'))['total'] or 0
    
    context = {
        'empresa': empresa,
        'eventos_financeiro': eventos_financeiro,
        'categorias_despesas': categorias_despesas,
        'total_despesas': total_despesas,
        'total_receitas': total_receitas,
        'lucro_total': total_receitas - total_despesas,
    }
    
    return render(request, 'web/financeiro_dashboard.html', context)


@login_required
def web_freelancer_dashboard(request):
    """
    Dashboard do freelancer na interface web
    """
    if not request.user.is_freelancer:
        messages.error(request, 'Acesso negado.')
        return redirect('home')
    
    try:
        freelance = Freelance.objects.get(usuario=request.user)
    except Freelance.DoesNotExist:
        messages.error(request, 'Perfil de freelancer não encontrado.')
        return redirect('home')
    
    # Candidaturas recentes
    candidaturas_recentes = Candidatura.objects.filter(
        freelance=freelance
    ).select_related('vaga__setor__evento', 'vaga__funcao').order_by('-data_candidatura')[:5]
    
    # Estatísticas
    candidaturas_total = Candidatura.objects.filter(freelance=freelance).count()
    candidaturas_pendentes = Candidatura.objects.filter(freelance=freelance, status='pendente').count()
    candidaturas_aprovadas = Candidatura.objects.filter(freelance=freelance, status='aprovada').count()
    
    # Contratos ativos
    contratos_ativos = ContratoFreelance.objects.filter(
        vaga__candidaturas__freelance=freelance, status='ativo'
    ).select_related('vaga__setor__evento', 'vaga__funcao')
    
    # Vagas recomendadas (simplificado)
    vagas_recomendadas = Vaga.objects.filter(
        ativa=True,
        setor__evento__ativo=True
    ).exclude(
        candidaturas__freelance=freelance
    ).select_related('setor__evento', 'funcao').order_by('-data_criacao')[:5]
    
    context = {
        'freelance': freelance,
        'candidaturas_recentes': candidaturas_recentes,
        'candidaturas_total': candidaturas_total,
        'candidaturas_pendentes': candidaturas_pendentes,
        'candidaturas_aprovadas': candidaturas_aprovadas,
        'contratos_ativos': contratos_ativos,
        'vagas_recomendadas': vagas_recomendadas,
    }
    
    return render(request, 'web/dashboard_freelancer.html', context)


@login_required
def web_admin_dashboard(request):
    """
    Dashboard do administrador do sistema
    """
    if not request.user.is_admin_sistema:
        messages.error(request, 'Acesso negado.')
        return redirect('home')
    
    # Estatísticas gerais
    total_empresas = EmpresaContratante.objects.count()
    empresas_ativas = EmpresaContratante.objects.filter(ativo=True).count()
    
    total_freelancers = Freelance.objects.count()
    freelancers_ativos = Freelance.objects.filter(usuario__ativo=True).count()
    
    total_eventos = Evento.objects.count()
    eventos_ativos = Evento.objects.filter(ativo=True).count()
    
    total_vagas = Vaga.objects.count()
    vagas_ativas = Vaga.objects.filter(ativa=True).count()
    
    # Candidaturas recentes
    candidaturas_recentes = Candidatura.objects.filter(
        data_candidatura__gte=timezone.now() - timedelta(days=7)
    ).select_related('freelance__usuario', 'vaga__setor__evento').order_by('-data_candidatura')[:10]
    
    # Equipamentos em manutenção
    equipamentos_manutencao = ManutencaoEquipamento.objects.filter(
        status='em_andamento'
    ).select_related('equipamento', 'responsavel')[:10]
    
    context = {
        'total_empresas': total_empresas,
        'empresas_ativas': empresas_ativas,
        'total_freelancers': total_freelancers,
        'freelancers_ativos': freelancers_ativos,
        'total_eventos': total_eventos,
        'eventos_ativos': eventos_ativos,
        'total_vagas': total_vagas,
        'vagas_ativas': vagas_ativas,
        'candidaturas_recentes': candidaturas_recentes,
        'equipamentos_manutencao': equipamentos_manutencao,
    }
    
    return render(request, 'web/dashboard_admin.html', context)
