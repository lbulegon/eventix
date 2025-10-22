"""
Serviço de notificação MOCK para testes (sem Twilio)
"""
from django.conf import settings
from app_eventos.models import Freelance, Vaga, Funcao
import logging

logger = logging.getLogger(__name__)


class NotificacaoVagasServiceMock:
    """
    Versão MOCK do serviço de notificação para testes
    Não envia SMS real, apenas simula
    """
    
    def __init__(self):
        self.mock_mode = True
    
    def is_configured(self):
        """Sempre configurado no modo mock"""
        return True
    
    def notificar_nova_vaga(self, vaga):
        """
        Simula notificação de vaga
        
        Args:
            vaga: Instância da Vaga
            
        Returns:
            dict: Estatísticas simuladas
        """
        if not vaga.funcao:
            logger.warning("Vaga sem função definida")
            return {'erro': 'Vaga sem função definida'}
        
        # Buscar freelancers com a função da vaga
        freelancers = self._buscar_freelancers_por_funcao(vaga.funcao)
        
        if not freelancers:
            logger.info(f"Nenhum freelancer encontrado para função: {vaga.funcao.nome}")
            return {'freelancers': 0, 'enviados': 0}
        
        # Simular envio
        resultado = self._simular_envio(freelancers, vaga)
        
        return resultado
    
    def _buscar_freelancers_por_funcao(self, funcao):
        """Busca freelancers que têm a função especificada"""
        if not funcao:
            logger.warning("Vaga sem função definida")
            return Freelance.objects.none()
        
        # Buscar freelancers que têm esta função
        freelancers = Freelance.objects.filter(
            funcoes__funcao=funcao,
            notificacoes_ativas=True,
            telefone__isnull=False,
            telefone__gt=''
        ).distinct()
        
        logger.info(f"Encontrados {freelancers.count()} freelancers para função: {funcao.nome}")
        return freelancers
    
    def _simular_envio(self, freelancers, vaga):
        """Simula envio de notificações"""
        stats = {
            'total_freelancers': freelancers.count(),
            'enviados': 0,
            'erros': 0,
            'results': []
        }
        
        for freelancer in freelancers:
            try:
                # Simular sucesso
                stats['enviados'] += 1
                stats['results'].append({
                    'freelancer': freelancer.nome_completo,
                    'telefone': freelancer.telefone,
                    'status': 'enviado',
                    'sid': f'MOCK_{freelancer.id}_{vaga.id}'
                })
                logger.info(f"✅ MOCK: Notificação simulada para {freelancer.nome_completo}")
                
            except Exception as e:
                stats['erros'] += 1
                stats['results'].append({
                    'freelancer': freelancer.nome_completo,
                    'telefone': freelancer.telefone,
                    'status': 'erro',
                    'erro': str(e)
                })
                logger.error(f"❌ MOCK: Erro simulado para {freelancer.nome_completo}: {str(e)}")
        
        # Log do resultado
        logger.info(f"📊 MOCK: Notificação de vaga '{vaga.funcao.nome}': "
                   f"{stats['enviados']}/{stats['total_freelancers']} simuladas")
        
        return stats
    
    def notificar_vagas_por_funcao(self, funcao_nome):
        """Simula notificação para função específica"""
        try:
            funcao = Funcao.objects.get(nome__iexact=funcao_nome)
            vagas = Vaga.objects.filter(funcao=funcao, ativa=True)
            
            if not vagas.exists():
                return {'erro': f'Nenhuma vaga ativa encontrada para função: {funcao_nome}'}
            
            # Buscar freelancers
            freelancers = self._buscar_freelancers_por_funcao(funcao)
            
            if not freelancers.exists():
                return {'erro': f'Nenhum freelancer encontrado para função: {funcao_nome}'}
            
            # Simular envio
            return self._simular_envio(freelancers, vagas.first())
            
        except Funcao.DoesNotExist:
            return {'erro': f'Função não encontrada: {funcao_nome}'}
