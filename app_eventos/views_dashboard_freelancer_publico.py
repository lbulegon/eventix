from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.db.models import Q
from app_eventos.models import Freelance, Vaga, Candidatura, Evento, Funcao
import logging

logger = logging.getLogger(__name__)

def login_freelancer(request):
    """Login do freelancer"""
    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        
        logger.info(f"🔐 Tentativa de login freelancer: {email}")
        
        # Autenticar freelancer
        user = authenticate(request, username=email, password=senha)
        
        if user and hasattr(user, 'freelance'):
            login(request, user)
            logger.info(f"✅ Login freelancer bem-sucedido: {user.email}")
            return redirect('freelancer_publico:dashboard')
        else:
            logger.warning(f"❌ Login freelancer falhou: {email}")
            messages.error(request, 'Email ou senha incorretos')
    
    return render(request, 'freelancer_publico/login.html')

def logout_freelancer(request):
    """Logout do freelancer"""
    logger.info(f"🔓 Logout freelancer: {request.user.email if request.user.is_authenticated else 'Anônimo'}")
    logout(request)
    return redirect('freelancer_publico:login')

@login_required(login_url='/freelancer/login/')
def dashboard_freelancer(request):
    """Dashboard principal do freelancer"""
    try:
        freelancer = request.user.freelance
        
        # Buscar candidaturas do freelancer
        candidaturas = Candidatura.objects.filter(freelance=freelancer).order_by('-data_candidatura')
        
        # Buscar vagas ativas (públicas)
        vagas_ativas = Vaga.objects.filter(ativa=True).order_by('-data_criacao')[:10]
        
        # Estatísticas
        stats = {
            'total_candidaturas': candidaturas.count(),
            'candidaturas_pendentes': candidaturas.filter(status='pendente').count(),
            'candidaturas_aprovadas': candidaturas.filter(status='aprovada').count(),
            'candidaturas_rejeitadas': candidaturas.filter(status='rejeitada').count(),
            'total_vagas_ativas': vagas_ativas.count()
        }
        
        logger.info(f"📊 Dashboard freelancer carregado: {freelancer.nome_completo}")
        
        context = {
            'freelancer': freelancer,
            'candidaturas': candidaturas[:5],  # Últimas 5
            'vagas_ativas': vagas_ativas,
            'stats': stats
        }
        
        return render(request, 'freelancer_publico/dashboard.html', context)
        
    except Exception as e:
        logger.error(f"❌ Erro no dashboard freelancer: {str(e)}")
        messages.error(request, 'Erro ao carregar dashboard')
        return redirect('freelancer_publico:login')

@login_required(login_url='/freelancer/login/')
def vagas_disponiveis(request):
    """Lista de vagas disponíveis para candidatura"""
    try:
        freelancer = request.user.freelance
        
        # Buscar vagas ativas
        vagas = Vaga.objects.filter(ativa=True).order_by('-data_criacao')
        
        # Filtros
        funcao_filtro = request.GET.get('funcao')
        if funcao_filtro:
            vagas = vagas.filter(funcao__nome__icontains=funcao_filtro)
        
        evento_filtro = request.GET.get('evento')
        if evento_filtro:
            vagas = vagas.filter(evento__nome__icontains=evento_filtro)
        
        # Buscar funções disponíveis para filtro
        funcoes_disponiveis = Funcao.objects.filter(vaga__ativa=True).distinct()
        
        logger.info(f"📋 Vagas disponíveis carregadas: {vagas.count()} vagas")
        
        context = {
            'freelancer': freelancer,
            'vagas': vagas,
            'funcoes_disponiveis': funcoes_disponiveis,
            'funcao_filtro': funcao_filtro,
            'evento_filtro': evento_filtro
        }
        
        return render(request, 'freelancer_publico/vagas_disponiveis.html', context)
        
    except Exception as e:
        logger.error(f"❌ Erro ao carregar vagas: {str(e)}")
        messages.error(request, 'Erro ao carregar vagas disponíveis')
        return redirect('freelancer_publico:dashboard')

@login_required(login_url='/freelancer/login/')
def candidatar_vaga(request, vaga_id):
    """Candidatar-se a uma vaga"""
    try:
        freelancer = request.user.freelance
        vaga = get_object_or_404(Vaga, id=vaga_id)
        
        # Verificar se já se candidatou
        candidatura_existente = Candidatura.objects.filter(
            freelance=freelancer, 
            vaga=vaga
        ).first()
        
        if candidatura_existente:
            messages.warning(request, 'Você já se candidatou a esta vaga')
            return redirect('freelancer_publico:vagas_disponiveis')
        
        # Verificar se freelancer tem a função necessária
        if vaga.funcao and not freelancer.funcoes.filter(funcao=vaga.funcao).exists():
            messages.error(request, f'Você não possui a função "{vaga.funcao.nome}" necessária para esta vaga')
            return redirect('freelancer_publico:vagas_disponiveis')
        
        # Criar candidatura
        candidatura = Candidatura.objects.create(
            freelance=freelancer,
            vaga=vaga,
            status='pendente'
        )
        
        logger.info(f"📝 Candidatura criada: {freelancer.nome_completo} -> Vaga {vaga.id}")
        messages.success(request, f'Candidatura enviada para "{vaga.titulo}"')
        
        return redirect('freelancer_publico:minhas_candidaturas')
        
    except Exception as e:
        logger.error(f"❌ Erro ao candidatar vaga {vaga_id}: {str(e)}")
        messages.error(request, 'Erro ao enviar candidatura')
        return redirect('freelancer_publico:vagas_disponiveis')

@login_required(login_url='/freelancer/login/')
def minhas_candidaturas(request):
    """Lista de candidaturas do freelancer"""
    try:
        freelancer = request.user.freelance
        
        # Buscar candidaturas
        candidaturas = Candidatura.objects.filter(freelance=freelancer).order_by('-data_candidatura')
        
        # Filtros
        status_filtro = request.GET.get('status')
        if status_filtro:
            candidaturas = candidaturas.filter(status=status_filtro)
        
        logger.info(f"📋 Candidaturas carregadas: {candidaturas.count()} candidaturas")
        
        context = {
            'freelancer': freelancer,
            'candidaturas': candidaturas
        }
        
        return render(request, 'freelancer_publico/minhas_candidaturas.html', context)
        
    except Exception as e:
        logger.error(f"❌ Erro ao carregar candidaturas: {str(e)}")
        messages.error(request, 'Erro ao carregar candidaturas')
        return redirect('freelancer_publico:dashboard')

@login_required(login_url='/freelancer/login/')
def perfil_freelancer(request):
    """Perfil do freelancer"""
    try:
        freelancer = request.user.freelance
        
        # Buscar funções do freelancer
        funcoes = freelancer.funcoes.all()
        
        # Estatísticas
        candidaturas = Candidatura.objects.filter(freelance=freelancer)
        stats = {
            'total_candidaturas': candidaturas.count(),
            'candidaturas_pendentes': candidaturas.filter(status='pendente').count(),
            'candidaturas_aprovadas': candidaturas.filter(status='aprovada').count(),
            'candidaturas_rejeitadas': candidaturas.filter(status='rejeitada').count()
        }
        
        logger.info(f"👤 Perfil freelancer carregado: {freelancer.nome_completo}")
        
        context = {
            'freelancer': freelancer,
            'funcoes': funcoes,
            'stats': stats
        }
        
        return render(request, 'freelancer_publico/perfil.html', context)
        
    except Exception as e:
        logger.error(f"❌ Erro ao carregar perfil: {str(e)}")
        messages.error(request, 'Erro ao carregar perfil')
        return redirect('freelancer_publico:dashboard')

def vaga_publica(request, vaga_id):
    """Página pública da vaga (sem login)"""
    try:
        vaga = get_object_or_404(Vaga, id=vaga_id, ativa=True)
        
        logger.info(f"🌐 Vaga pública acessada: {vaga.titulo}")
        
        context = {
            'vaga': vaga,
            'evento': vaga.evento,
            'setor': vaga.setor
        }
        
        return render(request, 'freelancer_publico/vaga_publica.html', context)
        
    except Exception as e:
        logger.error(f"❌ Erro ao acessar vaga pública {vaga_id}: {str(e)}")
        return render(request, 'freelancer_publico/erro.html', {
            'mensagem': 'Vaga não encontrada ou inativa'
        })

def evento_publico(request, evento_id):
    """Página pública do evento (sem login)"""
    try:
        evento = get_object_or_404(Evento, id=evento_id)
        
        # Buscar vagas ativas do evento
        vagas = Vaga.objects.filter(evento=evento, ativa=True)
        
        logger.info(f"🌐 Evento público acessado: {evento.nome}")
        
        context = {
            'evento': evento,
            'vagas': vagas
        }
        
        return render(request, 'freelancer_publico/evento_publico.html', context)
        
    except Exception as e:
        logger.error(f"❌ Erro ao acessar evento público {evento_id}: {str(e)}")
        return render(request, 'freelancer_publico/erro.html', {
            'mensagem': 'Evento não encontrado'
        })
