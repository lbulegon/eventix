"""
Views para Dashboard Personalizado da Empresa
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from .models import (
    Evento, Vaga, Candidatura, ContratoFreelance, Freelance,
    Equipamento, ManutencaoEquipamento, DespesaEvento, ReceitaEvento,
    User, GrupoPermissaoEmpresa
)
from .mixins import EmpresaContratanteRequiredMixin


@login_required
def test_dashboard(request):
    """
    View de teste para verificar se o dashboard está funcionando
    """
    # Verificar se é usuário de empresa
    if request.user.tipo_usuario not in ['admin_empresa', 'operador_empresa']:
        messages.error(request, 'Acesso negado. Apenas usuários de empresa podem acessar este dashboard.')
        return redirect('home')
    
    if not request.user.empresa_contratante:
        messages.error(request, 'Usuário não está associado a nenhuma empresa.')
        return redirect('home')
    
    empresa = request.user.empresa_contratante
    
    context = {
        'empresa': empresa,
        'user': request.user,
    }
    
    return render(request, 'dashboard_empresa/test.html', context)


@login_required
def dashboard_empresa(request):
    """
    Dashboard principal da empresa
    """
    # Verificar se é usuário de empresa
    if request.user.tipo_usuario not in ['admin_empresa', 'operador_empresa']:
        messages.error(request, 'Acesso negado. Apenas usuários de empresa podem acessar este dashboard.')
        return redirect('home')
    
    if not request.user.empresa_contratante:
        messages.error(request, 'Usuário não está associado a nenhuma empresa.')
        return redirect('home')
    
    empresa = request.user.empresa_contratante
    
    # Estatísticas gerais
    stats = {
        'total_eventos': Evento.objects.filter(empresa_contratante=empresa).count(),
        'eventos_ativos': Evento.objects.filter(empresa_contratante=empresa, ativo=True).count(),
        'total_vagas': Vaga.objects.filter(empresa_contratante=empresa).count(),
        'vagas_ativas': Vaga.objects.filter(empresa_contratante=empresa, ativa=True).count(),
        'total_candidaturas': Candidatura.objects.filter(vaga__empresa_contratante=empresa).count(),
        'candidaturas_pendentes': Candidatura.objects.filter(vaga__empresa_contratante=empresa, status='pendente').count(),
        'total_freelancers': Freelance.objects.filter(
            candidaturas__vaga__empresa_contratante=empresa
        ).distinct().count(),
        'total_equipamentos': Equipamento.objects.filter(empresa_contratante=empresa).count(),
        'equipamentos_ativos': Equipamento.objects.filter(empresa_contratante=empresa, ativo=True).count(),
        'total_usuarios': User.objects.filter(empresa_contratante=empresa).count(),
    }
    
    # Eventos recentes
    eventos_recentes = Evento.objects.filter(
        empresa_contratante=empresa
    ).order_by('-data_criacao')[:5]
    
    # Candidaturas recentes
    candidaturas_recentes = Candidatura.objects.filter(
        vaga__empresa_contratante=empresa
    ).order_by('-data_candidatura')[:5]
    
    # Receitas e despesas do mês atual
    hoje = timezone.now()
    inicio_mes = hoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    receitas_mes = ReceitaEvento.objects.filter(
        evento__empresa_contratante=empresa,
        data_vencimento__gte=inicio_mes
    ).aggregate(total=Sum('valor'))['total'] or 0
    
    despesas_mes = DespesaEvento.objects.filter(
        evento__empresa_contratante=empresa,
        data_vencimento__gte=inicio_mes
    ).aggregate(total=Sum('valor'))['total'] or 0
    
    stats['receitas_mes'] = receitas_mes
    stats['despesas_mes'] = despesas_mes
    stats['saldo_mes'] = receitas_mes - despesas_mes
    
    context = {
        'empresa': empresa,
        'stats': stats,
        'eventos_recentes': eventos_recentes,
        'candidaturas_recentes': candidaturas_recentes,
        'user': request.user,
    }
    
    return render(request, 'dashboard_empresa/home.html', context)


@login_required
def eventos_empresa(request):
    """
    Lista de eventos da empresa
    """
    if request.user.tipo_usuario not in ['admin_empresa', 'operador_empresa']:
        messages.error(request, 'Acesso negado.')
        return redirect('home')
    
    empresa = request.user.empresa_contratante
    eventos = Evento.objects.filter(empresa_contratante=empresa).order_by('-data_criacao')
    
    context = {
        'empresa': empresa,
        'eventos': eventos,
        'user': request.user,
    }
    
    return render(request, 'dashboard_empresa/eventos.html', context)


@login_required
def candidaturas_empresa(request):
    """
    Lista de candidaturas da empresa
    """
    if request.user.tipo_usuario not in ['admin_empresa', 'operador_empresa']:
        messages.error(request, 'Acesso negado.')
        return redirect('home')
    
    empresa = request.user.empresa_contratante
    candidaturas = Candidatura.objects.filter(
        vaga__empresa_contratante=empresa
    ).order_by('-data_candidatura')
    
    context = {
        'empresa': empresa,
        'candidaturas': candidaturas,
        'user': request.user,
    }
    
    return render(request, 'dashboard_empresa/candidaturas.html', context)


@login_required
def freelancers_empresa(request):
    """
    Lista de freelancers da empresa
    """
    if request.user.tipo_usuario not in ['admin_empresa', 'operador_empresa']:
        messages.error(request, 'Acesso negado.')
        return redirect('home')
    
    empresa = request.user.empresa_contratante
    
    # Freelancers que se candidataram a vagas da empresa
    freelancers = Freelance.objects.filter(
        candidaturas__vaga__empresa_contratante=empresa
    ).distinct().order_by('nome_completo')
    
    context = {
        'empresa': empresa,
        'freelancers': freelancers,
        'user': request.user,
    }
    
    return render(request, 'dashboard_empresa/freelancers.html', context)


@login_required
def usuarios_empresa(request):
    """
    Lista de usuários da empresa (apenas para admin)
    """
    if request.user.tipo_usuario != 'admin_empresa':
        messages.error(request, 'Apenas administradores podem gerenciar usuários.')
        return redirect('dashboard_empresa')
    
    empresa = request.user.empresa_contratante
    usuarios = User.objects.filter(empresa_contratante=empresa).order_by('username')
    
    context = {
        'empresa': empresa,
        'usuarios': usuarios,
        'user': request.user,
    }
    
    return render(request, 'dashboard_empresa/usuarios.html', context)


@login_required
def equipamentos_empresa(request):
    """
    Lista de equipamentos da empresa
    """
    if request.user.tipo_usuario not in ['admin_empresa', 'operador_empresa']:
        messages.error(request, 'Acesso negado.')
        return redirect('home')
    
    empresa = request.user.empresa_contratante
    equipamentos = Equipamento.objects.filter(empresa_contratante=empresa).order_by('codigo_patrimonial')
    
    context = {
        'empresa': empresa,
        'equipamentos': equipamentos,
        'user': request.user,
    }
    
    return render(request, 'dashboard_empresa/equipamentos.html', context)


@login_required
def financeiro_empresa(request):
    """
    Dashboard financeiro da empresa
    """
    if request.user.tipo_usuario not in ['admin_empresa', 'operador_empresa']:
        messages.error(request, 'Acesso negado.')
        return redirect('home')
    
    empresa = request.user.empresa_contratante
    
    # Receitas e despesas por mês (últimos 6 meses)
    hoje = timezone.now()
    meses = []
    
    for i in range(6):
        data = hoje - timedelta(days=30*i)
        inicio_mes = data.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        fim_mes = (inicio_mes + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        receitas = ReceitaEvento.objects.filter(
            evento__empresa_contratante=empresa,
            data_vencimento__range=[inicio_mes, fim_mes]
        ).aggregate(total=Sum('valor'))['total'] or 0
        
        despesas = DespesaEvento.objects.filter(
            evento__empresa_contratante=empresa,
            data_vencimento__range=[inicio_mes, fim_mes]
        ).aggregate(total=Sum('valor'))['total'] or 0
        
        meses.append({
            'mes': inicio_mes.strftime('%m/%Y'),
            'receitas': receitas,
            'despesas': despesas,
            'saldo': receitas - despesas
        })
    
    context = {
        'empresa': empresa,
        'meses': reversed(meses),  # Mostrar do mais antigo para o mais recente
        'user': request.user,
    }
    
    return render(request, 'dashboard_empresa/financeiro.html', context)
