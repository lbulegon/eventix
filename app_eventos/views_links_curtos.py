from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.decorators import login_required
from app_eventos.models import Vaga, Evento, Freelance
import logging

logger = logging.getLogger(__name__)

def detectar_mobile(request):
    """Detecta se o dispositivo é móvel baseado no User-Agent"""
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    mobile_keywords = [
        'mobile', 'android', 'iphone', 'ipad', 'ipod', 
        'blackberry', 'windows phone', 'opera mini',
        'samsung', 'lg', 'motorola', 'nokia'
    ]
    return any(keyword in user_agent for keyword in mobile_keywords)

def redirecionar_vaga(request, vaga_id):
    """Redireciona para vaga específica (app ou web)"""
    try:
        vaga = get_object_or_404(Vaga, id=vaga_id)
        logger.info(f"🔗 Link curto vaga {vaga_id} acessado")
        
        is_mobile = detectar_mobile(request)
        logger.info(f"📱 Dispositivo móvel: {is_mobile}")
        
        if is_mobile:
            # Template com deep link + fallback
            return render(request, 'links_curtos/redirect_vaga.html', {
                'vaga': vaga,
                'vaga_id': vaga_id,
                'deep_link': f'eventix://vaga/{vaga_id}',
                'web_url': f'/links/vagas/{vaga_id}/'
            })
        else:
            # Desktop - ir direto para web
            return redirect('links_curtos:vaga_web', vaga_id=vaga_id)
            
    except Exception as e:
        logger.error(f"❌ Erro ao redirecionar vaga {vaga_id}: {str(e)}")
        return render(request, 'links_curtos/erro.html', {
            'mensagem': 'Vaga não encontrada ou inativa'
        })

def redirecionar_evento(request, evento_id):
    """Redireciona para evento específico (app ou web)"""
    try:
        evento = get_object_or_404(Evento, id=evento_id)
        logger.info(f"🔗 Link curto evento {evento_id} acessado")
        
        is_mobile = detectar_mobile(request)
        logger.info(f"📱 Dispositivo móvel: {is_mobile}")
        
        if is_mobile:
            # Template com deep link + fallback
            return render(request, 'links_curtos/redirect_evento.html', {
                'evento': evento,
                'evento_id': evento_id,
                'deep_link': f'eventix://evento/{evento_id}',
                'web_url': f'/links/eventos/{evento_id}/'
            })
        else:
            # Desktop - ir direto para web
            return redirect('links_curtos:evento_web', evento_id=evento_id)
            
    except Exception as e:
        logger.error(f"❌ Erro ao redirecionar evento {evento_id}: {str(e)}")
        return render(request, 'links_curtos/erro.html', {
            'mensagem': 'Evento não encontrado ou inativo'
        })

def redirecionar_freelancer(request, freelancer_id):
    """Redireciona para perfil do freelancer (app ou web)"""
    try:
        freelancer = get_object_or_404(Freelance, id=freelancer_id)
        logger.info(f"🔗 Link curto freelancer {freelancer_id} acessado")
        
        is_mobile = detectar_mobile(request)
        logger.info(f"📱 Dispositivo móvel: {is_mobile}")
        
        if is_mobile:
            # Template com deep link + fallback
            return render(request, 'links_curtos/redirect_freelancer.html', {
                'freelancer': freelancer,
                'freelancer_id': freelancer_id,
                'deep_link': f'eventix://freelancer/{freelancer_id}',
                'web_url': f'/links/freelancers/{freelancer_id}/'
            })
        else:
            # Desktop - ir direto para web
            return redirect('links_curtos:freelancer_web', freelancer_id=freelancer_id)
            
    except Exception as e:
        logger.error(f"❌ Erro ao redirecionar freelancer {freelancer_id}: {str(e)}")
        return render(request, 'links_curtos/erro.html', {
            'mensagem': 'Freelancer não encontrado'
        })

def vaga_web(request, vaga_id):
    """Página web da vaga (fallback) - Redireciona para área pública"""
    try:
        vaga = get_object_or_404(Vaga, id=vaga_id)
        logger.info(f"🌐 Redirecionando vaga {vaga_id} para área pública")
        
        # Redirecionar para a página pública da vaga
        return redirect('freelancer_publico:vaga_publica', vaga_id=vaga_id)
        
    except Exception as e:
        logger.error(f"❌ Erro ao acessar vaga web {vaga_id}: {str(e)}")
        return render(request, 'links_curtos/erro.html', {
            'mensagem': 'Vaga não encontrada'
        })

def evento_web(request, evento_id):
    """Página web do evento (fallback) - Redireciona para área pública"""
    try:
        evento = get_object_or_404(Evento, id=evento_id)
        logger.info(f"🌐 Redirecionando evento {evento_id} para área pública")
        
        # Redirecionar para a página pública do evento
        return redirect('freelancer_publico:evento_publico', evento_id=evento_id)
        
    except Exception as e:
        logger.error(f"❌ Erro ao acessar evento web {evento_id}: {str(e)}")
        return render(request, 'links_curtos/erro.html', {
            'mensagem': 'Evento não encontrado'
        })

def freelancer_web(request, freelancer_id):
    """Página web do freelancer (fallback)"""
    try:
        freelancer = get_object_or_404(Freelance, id=freelancer_id)
        logger.info(f"🌐 Acessando freelancer web {freelancer_id}")
        
        return render(request, 'links_curtos/freelancer_web.html', {
            'freelancer': freelancer
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao acessar freelancer web {freelancer_id}: {str(e)}")
        return render(request, 'links_curtos/erro.html', {
            'mensagem': 'Freelancer não encontrado'
        })

def gerar_link_curto(tipo, id):
    """Gera link curto para qualquer tipo de conteúdo"""
    base_url = "https://evtix.com.br"
    
    if tipo == 'vaga':
        return f"{base_url}/v/{id}"
    elif tipo == 'evento':
        return f"{base_url}/e/{id}"
    elif tipo == 'freelancer':
        return f"{base_url}/f/{id}"
    else:
        return f"{base_url}/"
