from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from app_eventos.models import (
    Evento, Vaga, Candidatura, ContratoFreelance, 
    EquipamentoSetor, ManutencaoEquipamento, EmpresaContratante, Freelance, Fornecedor
)


@login_required
def dashboard_redirect(request):
    """
    Redireciona para o dashboard apropriado baseado no tipo de usuário
    """
    user = request.user
    
    if user.is_admin_sistema:
        return redirect('admin:index')
    elif user.is_empresa_user:
        return redirect('dashboard_empresa')
    elif user.is_freelancer:
        return redirect('dashboard_freelancer')
    else:
        messages.error(request, 'Tipo de usuário não reconhecido.')
        return redirect('home')


@login_required
def dashboard_empresa(request):
    """
    Dashboard para usuários de empresa
    """
    if not request.user.is_empresa_user:
        messages.error(request, 'Acesso negado.')
        return redirect('home')
    
    empresa = request.user.empresa_contratante
    if not empresa:
        messages.error(request, 'Usuário não está associado a nenhuma empresa.')
        return redirect('home')
    
    # Estatísticas dos últimos 30 dias
    data_inicio = timezone.now() - timedelta(days=30)
    
    # Eventos
    eventos_ativos = Evento.objects.filter(
        empresa_contratante=empresa,
        ativo=True
    ).count()
    
    eventos_recentes = Evento.objects.filter(
        empresa_contratante=empresa,
        data_inicio__gte=data_inicio
    ).order_by('-data_inicio')[:5]
    
    # Vagas
    vagas_ativas = Vaga.objects.filter(
        setor__evento__empresa_contratante=empresa,
        ativa=True
    ).count()
    
    # Candidaturas
    candidaturas_recentes = Candidatura.objects.filter(
        vaga__setor__evento__empresa_contratante=empresa,
        data_candidatura__gte=data_inicio
    ).count()
    
    candidaturas_pendentes = Candidatura.objects.filter(
        vaga__setor__evento__empresa_contratante=empresa,
        status='pendente'
    ).count()
    
    # Contratos
    contratos_ativos = ContratoFreelance.objects.filter(
        vaga__setor__evento__empresa_contratante=empresa,
        status='ativo'
    ).count()
    
    # Equipamentos
    equipamentos_setor = EquipamentoSetor.objects.filter(
        setor__evento__empresa_contratante=empresa
    )
    
    equipamentos_em_manutencao = ManutencaoEquipamento.objects.filter(
        equipamento__empresa_contratante=empresa,
        status='em_andamento'
    ).count()
    
    context = {
        'empresa': empresa,
        'eventos_ativos': eventos_ativos,
        'eventos_recentes': eventos_recentes,
        'vagas_ativas': vagas_ativas,
        'candidaturas_recentes': candidaturas_recentes,
        'candidaturas_pendentes': candidaturas_pendentes,
        'contratos_ativos': contratos_ativos,
        'equipamentos_em_manutencao': equipamentos_em_manutencao,
    }
    
    return render(request, 'dashboard_principal.html', context)


@login_required
def dashboard_freelancer(request):
    """
    Dashboard para freelancers
    """
    if not request.user.is_freelancer:
        messages.error(request, 'Acesso negado.')
        return redirect('home')
    
    try:
        freelance = Freelance.objects.get(usuario=request.user)
    except Freelance.DoesNotExist:
        messages.error(request, 'Perfil de freelancer não encontrado.')
        return redirect('home')
    
    # Estatísticas dos últimos 30 dias
    data_inicio = timezone.now() - timedelta(days=30)
    
    # Candidaturas
    candidaturas_recentes = Candidatura.objects.filter(
        freelance=freelance,
        data_candidatura__gte=data_inicio
    ).order_by('-data_candidatura')[:5]
    
    candidaturas_pendentes = Candidatura.objects.filter(
        freelance=freelance,
        status='pendente'
    ).count()
    
    candidaturas_aprovadas = Candidatura.objects.filter(
        freelance=freelance,
        status='aprovada'
    ).count()
    
    # Contratos
    contratos_ativos = ContratoFreelance.objects.filter(
        vaga__candidaturas__freelance=freelance,
        status='ativo'
    ).count()
    
    # Vagas disponíveis
    vagas_disponiveis = Vaga.objects.filter(
        ativa=True,
        setor__evento__ativo=True
    ).count()
    
    context = {
        'freelance': freelance,
        'candidaturas_recentes': candidaturas_recentes,
        'candidaturas_pendentes': candidaturas_pendentes,
        'candidaturas_aprovadas': candidaturas_aprovadas,
        'contratos_ativos': contratos_ativos,
        'vagas_disponiveis': vagas_disponiveis,
    }
    
    return render(request, 'dashboard_principal.html', context)


@login_required
def dashboard_admin_sistema(request):
    """
    Dashboard para administradores do sistema
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
    ).count()
    
    # Equipamentos em manutenção
    equipamentos_manutencao = ManutencaoEquipamento.objects.filter(
        status='em_andamento'
    ).count()
    
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
    
    return render(request, 'dashboard_principal.html', context)


@login_required
def fluxo_caixa_evento(request, evento_id):
    """
    View para visualizar o fluxo de caixa de um evento específico
    """
    try:
        evento = Evento.objects.get(id=evento_id)
    except Evento.DoesNotExist:
        messages.error(request, 'Evento não encontrado.')
        return redirect('dashboard_empresa')
    
    # Verificar permissão de acesso
    user = request.user
    if not user.is_admin_sistema and evento.empresa_contratante != user.empresa_owner:
        messages.error(request, 'Acesso negado a este evento.')
        return redirect('dashboard_empresa')
    
    # Carregar despesas e receitas com suas categorias
    despesas = evento.despesas.select_related('categoria').all()
    receitas = evento.receitas.select_related('categoria').all()
    
    context = {
        'evento': evento,
        'despesas': despesas,
        'receitas': receitas,
    }
    
    return render(request, 'fluxo_caixa_evento.html', context)


@login_required
def fornecedores_list(request):
    """
    View para listar fornecedores da empresa
    """
    if not request.user.is_empresa_user:
        messages.error(request, 'Acesso negado.')
        return redirect('home')
    
    empresa = request.user.empresa_owner
    if not empresa:
        messages.error(request, 'Usuário não está associado a nenhuma empresa.')
        return redirect('home')
    
    # Filtros
    tipo_fornecedor = request.GET.get('tipo_fornecedor')
    ativo = request.GET.get('ativo')
    
    fornecedores = Fornecedor.objects.filter(empresa_contratante=empresa)
    
    if tipo_fornecedor:
        fornecedores = fornecedores.filter(tipo_fornecedor=tipo_fornecedor)
    
    if ativo is not None:
        fornecedores = fornecedores.filter(ativo=ativo.lower() == 'true')
    
    # Ordenar por nome
    fornecedores = fornecedores.order_by('nome_fantasia')
    
    context = {
        'fornecedores': fornecedores,
        'empresa': empresa,
    }
    
    return render(request, 'fornecedores_list.html', context)
