"""
Views para notificações manuais de vagas
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
import logging

from app_eventos.models import Evento, Vaga, Freelance
from app_eventos.services.notificacao_vagas import NotificacaoVagasService

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class NotificarFreelancersEventoView(View):
    """
    View para notificar freelancers sobre vagas de um evento
    """
    
    def get(self, request, evento_id):
        """Mostra página de notificação"""
        evento = get_object_or_404(Evento, id=evento_id)
        
        # Verificar se usuário tem permissão para este evento
        if not self._tem_permissao_evento(request.user, evento):
            messages.error(request, 'Você não tem permissão para acessar este evento.')
            return redirect('dashboard_empresa')
        
        # Buscar vagas ativas do evento
        vagas = Vaga.objects.filter(
            evento=evento,
            ativa=True
        ).select_related('funcao', 'setor')
        
        # Agrupar vagas por função
        vagas_por_funcao = {}
        for vaga in vagas:
            funcao_nome = vaga.funcao.nome if vaga.funcao else 'Sem função'
            if funcao_nome not in vagas_por_funcao:
                vagas_por_funcao[funcao_nome] = []
            vagas_por_funcao[funcao_nome].append(vaga)
        
        # Contar freelancers por função
        freelancers_por_funcao = {}
        for funcao_nome in vagas_por_funcao.keys():
            if funcao_nome != 'Sem função':
                try:
                    funcao = vagas_por_funcao[funcao_nome][0].funcao
                    freelancers = Freelance.objects.filter(
                        funcoes__funcao=funcao,
                        notificacoes_ativas=True,
                        telefone__isnull=False,
                        telefone__gt=''
                    ).distinct()
                    freelancers_por_funcao[funcao_nome] = freelancers.count()
                except:
                    freelancers_por_funcao[funcao_nome] = 0
            else:
                freelancers_por_funcao[funcao_nome] = 0
        
        context = {
            'evento': evento,
            'vagas_por_funcao': vagas_por_funcao,
            'freelancers_por_funcao': freelancers_por_funcao,
            'total_vagas': vagas.count(),
            'total_freelancers': sum(freelancers_por_funcao.values())
        }
        
        return render(request, 'dashboard_empresa/notificar_freelancers.html', context)
    
    def post(self, request, evento_id):
        """Envia notificações"""
        evento = get_object_or_404(Evento, id=evento_id)
        
        # Verificar permissão
        if not self._tem_permissao_evento(request.user, evento):
            return JsonResponse({'erro': 'Sem permissão'}, status=403)
        
        # Verificar se é AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return self._enviar_notificacoes_ajax(request, evento)
        else:
            return self._enviar_notificacoes_form(request, evento)
    
    def _enviar_notificacoes_ajax(self, request, evento):
        """Envia notificações via AJAX"""
        try:
            notificacao_service = NotificacaoVagasService()
            
            # Buscar vagas ativas do evento
            vagas = Vaga.objects.filter(evento=evento, ativa=True)
            
            if not vagas.exists():
                return JsonResponse({
                    'erro': 'Nenhuma vaga ativa encontrada neste evento'
                })
            
            # Enviar notificações por função
            resultados = {}
            total_enviados = 0
            total_erros = 0
            
            for vaga in vagas:
                if vaga.funcao:
                    resultado = notificacao_service.notificar_nova_vaga(vaga)
                    resultados[vaga.funcao.nome] = resultado
                    
                    if 'erro' not in resultado:
                        total_enviados += resultado.get('enviados', 0)
                        total_erros += resultado.get('erros', 0)
            
            return JsonResponse({
                'sucesso': True,
                'total_enviados': total_enviados,
                'total_erros': total_erros,
                'resultados': resultados,
                'mensagem': f'Notificações enviadas: {total_enviados} sucessos, {total_erros} erros'
            })
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificações: {str(e)}")
            return JsonResponse({
                'erro': f'Erro interno: {str(e)}'
            }, status=500)
    
    def _enviar_notificacoes_form(self, request, evento):
        """Envia notificações via formulário tradicional"""
        try:
            notificacao_service = NotificacaoVagasService()
            
            # Buscar vagas ativas do evento
            vagas = Vaga.objects.filter(evento=evento, ativa=True)
            
            if not vagas.exists():
                messages.warning(request, 'Nenhuma vaga ativa encontrada neste evento.')
                return redirect('notificar_freelancers_evento', evento_id=evento.id)
            
            # Enviar notificações
            total_enviados = 0
            total_erros = 0
            
            for vaga in vagas:
                if vaga.funcao:
                    resultado = notificacao_service.notificar_nova_vaga(vaga)
                    
                    if 'erro' not in resultado:
                        total_enviados += resultado.get('enviados', 0)
                        total_erros += resultado.get('erros', 0)
            
            if total_enviados > 0:
                messages.success(
                    request, 
                    f'✅ Notificações enviadas com sucesso! {total_enviados} freelancers notificados.'
                )
            else:
                messages.warning(request, '⚠️ Nenhuma notificação foi enviada.')
            
            if total_erros > 0:
                messages.warning(request, f'⚠️ {total_erros} notificações falharam.')
            
            return redirect('notificar_freelancers_evento', evento_id=evento.id)
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificações: {str(e)}")
            messages.error(request, f'❌ Erro ao enviar notificações: {str(e)}')
            return redirect('notificar_freelancers_evento', evento_id=evento.id)
    
    def _tem_permissao_evento(self, user, evento):
        """Verifica se usuário tem permissão para o evento"""
        # Implementar lógica de permissão baseada na empresa do usuário
        # Por enquanto, permitir para todos os usuários logados
        return user.is_authenticated


@require_http_methods(["POST"])
@login_required
def notificar_freelancers_vaga_especifica(request, vaga_id):
    """
    Notifica freelancers sobre uma vaga específica
    """
    try:
        vaga = get_object_or_404(Vaga, id=vaga_id)
        
        # Verificar permissão
        if not request.user.is_authenticated:
            return JsonResponse({'erro': 'Não autenticado'}, status=401)
        
        # Enviar notificação
        notificacao_service = NotificacaoVagasService()
        resultado = notificacao_service.notificar_nova_vaga(vaga)
        
        if 'erro' in resultado:
            return JsonResponse({
                'erro': resultado['erro']
            }, status=400)
        
        return JsonResponse({
            'sucesso': True,
            'enviados': resultado.get('enviados', 0),
            'erros': resultado.get('erros', 0),
            'mensagem': f'Notificação enviada para {resultado.get("enviados", 0)} freelancers'
        })
        
    except Exception as e:
        logger.error(f"Erro ao notificar vaga específica: {str(e)}")
        return JsonResponse({
            'erro': f'Erro interno: {str(e)}'
        }, status=500)
