from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from ..models import Evento

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
    eventos = Evento.objects.all()
    return render(request, "evento_list.html", {"eventos": eventos})
