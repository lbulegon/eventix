"""
Serviço para notificações automáticas de vagas por função
"""
from django.conf import settings
from app_eventos.models import Freelance, Vaga, Funcao
from app_eventos.services.twilio_service_sandbox import TwilioServiceSandbox
import logging

logger = logging.getLogger(__name__)


class NotificacaoVagasService:
    """
    Serviço para enviar notificações de vagas para freelancers
    baseado na função da vaga
    """
    
    def __init__(self):
        self.twilio = TwilioServiceSandbox()
    
    def notificar_nova_vaga(self, vaga):
        """
        Notifica freelancers sobre uma nova vaga
        
        Args:
            vaga: Instância da Vaga criada
            
        Returns:
            dict: Estatísticas do envio
        """
        if not self.twilio.is_configured():
            logger.warning("Twilio não configurado - pulando notificação")
            return {'erro': 'Twilio não configurado'}
        
        # Buscar freelancers com a função da vaga
        freelancers = self._buscar_freelancers_por_funcao(vaga.funcao)
        
        if not freelancers:
            logger.info(f"Nenhum freelancer encontrado para função: {vaga.funcao}")
            return {'freelancers': 0, 'enviados': 0}
        
        # Criar mensagem personalizada
        mensagem = self._criar_mensagem_vaga(vaga)
        
        # Enviar notificações
        resultado = self._enviar_notificacoes(freelancers, mensagem, vaga)
        
        return resultado
    
    def _buscar_freelancers_por_funcao(self, funcao):
        """
        Busca freelancers que têm a função especificada
        
        Args:
            funcao: Instância de Funcao
            
        Returns:
            QuerySet: Freelancers com a função
        """
        if not funcao:
            logger.warning("Vaga sem função definida")
            return Freelance.objects.none()
        
        # Buscar freelancers que têm esta função (através de FreelancerFuncao)
        freelancers = Freelance.objects.filter(
            funcoes__funcao=funcao,
            notificacoes_ativas=True,  # Só quem quer receber notificações
            telefone__isnull=False,    # Só quem tem telefone
            telefone__gt=''            # Só quem tem telefone não vazio
        ).distinct()
        
        logger.info(f"Encontrados {freelancers.count()} freelancers para função: {funcao.nome}")
        return freelancers
    
    def _criar_mensagem_vaga(self, vaga):
        """
        Cria mensagem personalizada para a vaga
        
        Args:
            vaga: Instância da Vaga
            
        Returns:
            str: Mensagem formatada
        """
        # Informações básicas
        evento_nome = vaga.evento.nome if vaga.evento else "Evento"
        setor_nome = vaga.setor.nome if vaga.setor else "Geral"
        funcao_nome = vaga.funcao.nome if vaga.funcao else "Função"
        quantidade = vaga.quantidade
        
        # Template da mensagem
        mensagem = f"""🎉 NOVA VAGA DISPONÍVEL!

📅 Evento: {evento_nome}
🏢 Setor: {setor_nome}
💼 Função: {funcao_nome}
👥 Vagas: {quantidade}

💰 Valor: R$ {vaga.remuneracao:.2f}/{vaga.get_tipo_remuneracao_display()}
📝 Descrição: {vaga.descricao[:100]}{'...' if len(vaga.descricao) > 100 else ''}

🔗 Acesse: https://eventix-development.up.railway.app/

#Eventix #Vagas #Trabalho"""
        
        return mensagem
    
    def _enviar_notificacoes(self, freelancers, mensagem, vaga):
        """
        Envia notificações para lista de freelancers
        
        Args:
            freelancers: QuerySet de freelancers
            mensagem: Texto da mensagem
            vaga: Instância da vaga
            
        Returns:
            dict: Estatísticas do envio
        """
        stats = {
            'total_freelancers': freelancers.count(),
            'enviados': 0,
            'erros': 0,
            'detalhes': []
        }
        
        for freelancer in freelancers:
            try:
                # Formatar telefone para E.164
                telefone_e164 = self.twilio.format_phone_e164(freelancer.telefone)
                
                # Enviar SMS
                resultado = self.twilio.send_sms(telefone_e164, mensagem)
                
                if resultado:
                    stats['enviados'] += 1
                    stats['detalhes'].append({
                        'freelancer': freelancer.nome_completo,
                        'telefone': telefone_e164,
                        'status': 'enviado',
                        'sid': resultado.sid
                    })
                    logger.info(f"✅ Notificação enviada para {freelancer.nome_completo}")
                else:
                    stats['erros'] += 1
                    stats['detalhes'].append({
                        'freelancer': freelancer.nome_completo,
                        'telefone': telefone_e164,
                        'status': 'erro',
                        'erro': 'Falha no envio'
                    })
                    logger.error(f"❌ Erro ao enviar para {freelancer.nome_completo}")
                    
            except Exception as e:
                stats['erros'] += 1
                stats['detalhes'].append({
                    'freelancer': freelancer.nome_completo,
                    'telefone': freelancer.telefone,
                    'status': 'erro',
                    'erro': str(e)
                })
                logger.error(f"❌ Exceção ao enviar para {freelancer.nome_completo}: {str(e)}")
        
        # Log do resultado
        logger.info(f"📊 Notificação de vaga '{vaga.funcao.nome if vaga.funcao else 'Sem função'}': "
                   f"{stats['enviados']}/{stats['total_freelancers']} enviadas")
        
        return stats
    
    def notificar_vagas_por_funcao(self, funcao_nome):
        """
        Notifica freelancers sobre vagas de uma função específica
        
        Args:
            funcao_nome: Nome da função
            
        Returns:
            dict: Resultado das notificações
        """
        try:
            funcao = Funcao.objects.get(nome__iexact=funcao_nome)
            vagas = Vaga.objects.filter(funcao=funcao, ativa=True)
            
            if not vagas.exists():
                return {'erro': f'Nenhuma vaga ativa encontrada para função: {funcao_nome}'}
            
            # Buscar freelancers
            freelancers = self._buscar_freelancers_por_funcao(funcao)
            
            if not freelancers.exists():
                return {'erro': f'Nenhum freelancer encontrado para função: {funcao_nome}'}
            
            # Criar mensagem com múltiplas vagas
            mensagem = self._criar_mensagem_multiplas_vagas(vagas, funcao)
            
            # Enviar
            return self._enviar_notificacoes(freelancers, mensagem, vagas.first())
            
        except Funcao.DoesNotExist:
            return {'erro': f'Função não encontrada: {funcao_nome}'}
    
    def _criar_mensagem_multiplas_vagas(self, vagas, funcao):
        """
        Cria mensagem para múltiplas vagas da mesma função
        """
        mensagem = f"""🎉 VAGAS DISPONÍVEIS - {funcao.nome.upper()}!

📊 Total de vagas: {vagas.count()}

"""
        
        for vaga in vagas[:3]:  # Mostrar até 3 vagas
            evento_nome = vaga.evento.nome if vaga.evento else "Evento"
            mensagem += f"• {evento_nome}: {vaga.quantidade} vagas - R$ {vaga.remuneracao:.2f}/{vaga.get_tipo_remuneracao_display()}\n"
        
        if vagas.count() > 3:
            mensagem += f"• ... e mais {vagas.count() - 3} vagas\n"
        
        mensagem += "\n🔗 Acesse: https://eventix-development.up.railway.app/\n#Eventix #Vagas #Trabalho"
        
        return mensagem
