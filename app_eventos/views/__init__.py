from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone
from ..models import Evento, EmpresaContratante

def home(request):
    """
    View inicial do Eventix - Redireciona baseado no status de autenticação
    Mantém compatibilidade com PWA (manifest.json e service-worker.js)
    """
    # Se não estiver autenticado, mostrar página inicial (com opções de login)
    if not request.user.is_authenticated:
        return render(request, "home.html")
    
    # Se estiver autenticado, redirecionar para o dashboard apropriado
    user = request.user
    
    # Verifica se é freelancer
    if hasattr(user, 'freelance') or user.tipo_usuario == 'freelancer':
        return redirect('freelancer_publico:dashboard')
    
    # Verifica se é usuário de empresa (admin_empresa ou operador_empresa)
    if user.tipo_usuario in ['admin_empresa', 'operador_empresa']:
        return redirect('dashboard_empresa:dashboard_empresa')
    
    # Verifica se é admin do sistema
    if user.tipo_usuario == 'admin_sistema':
        return redirect('admin:index')
    
    # Se não se encaixar em nenhum tipo, mostrar página inicial
    return render(request, "home.html")

def evento_list(request):
    """Lista de eventos com filtros e busca"""
    eventos = Evento.objects.filter(ativo=True).select_related('empresa_contratante')
    
    # Filtros
    busca = request.GET.get('busca', '')
    empresa_id = request.GET.get('empresa', '')
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')
    local = request.GET.get('local', '')
    
    # Aplicar filtros
    if busca:
        eventos = eventos.filter(
            Q(nome__icontains=busca) |
            Q(descricao__icontains=busca) |
            Q(local__icontains=busca)
        )
    
    if empresa_id:
        eventos = eventos.filter(empresa_contratante_id=empresa_id)
    
    if data_inicio:
        eventos = eventos.filter(data_inicio__gte=data_inicio)
    
    if data_fim:
        eventos = eventos.filter(data_fim__lte=data_fim)
    
    if local:
        eventos = eventos.filter(local__icontains=local)
    
    # Ordenar por data de início
    eventos = eventos.order_by('data_inicio')
    
    # Empresas para o filtro
    empresas = EmpresaContratante.objects.filter(ativo=True).order_by('nome_fantasia')
    
    context = {
        'eventos': eventos,
        'empresas': empresas,
        'filtros': {
            'busca': busca,
            'empresa_id': empresa_id,
            'data_inicio': data_inicio,
            'data_fim': data_fim,
            'local': local,
        }
    }
    
    return render(request, "evento_list.html", context)
