"""
Serviço Twilio adaptado para funcionar com Sandbox (conta gratuita)
"""
from twilio.rest import Client
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class TwilioServiceSandbox:
    """
    Versão do TwilioService que funciona com conta gratuita/sandbox
    Não precisa de Messaging Service configurado
    """
    
    def __init__(self):
        self.account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
        self.auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
        self.messaging_service_sid = getattr(settings, 'TWILIO_MESSAGING_SERVICE_SID', None)
        self.sandbox_number = getattr(settings, 'TWILIO_SANDBOX_NUMBER', '+12292644322')  # Seu número Trial
        
        if not self.account_sid or not self.auth_token:
            logger.warning("AVISO: Credenciais Twilio não configuradas")
            self.client = None
        else:
            self.client = Client(self.account_sid, self.auth_token)
    
    def is_configured(self):
        """Verifica se o Twilio está configurado"""
        return self.client is not None
    
    def send_whatsapp_sandbox(self, phone_e164, body):
        """
        Envia WhatsApp usando Sandbox (conta gratuita)
        
        IMPORTANTE: O número destinatário precisa ter enviado "join [código]"
        para o número sandbox antes de receber mensagens.
        
        Args:
            phone_e164: Número no formato E.164 (+5511999999999)
            body: Corpo da mensagem
        
        Returns:
            Message object do Twilio ou None
        """
        if not self.is_configured():
            logger.error("Twilio não configurado")
            return None
        
        try:
            message = self.client.messages.create(
                from_=f"whatsapp:{self.sandbox_number}",
                to=f"whatsapp:{phone_e164}",
                body=body
            )
            
            logger.info(f"✓ WhatsApp Sandbox enviado para {phone_e164} (SID: {message.sid})")
            return message
            
        except Exception as e:
            logger.error(f"✗ Erro ao enviar WhatsApp Sandbox: {str(e)}")
            return None
    
    def send_sms(self, phone_e164, body):
        """
        Envia SMS com timeout
        
        Args:
            phone_e164: Número no formato E.164
            body: Corpo da mensagem
        
        Returns:
            Message object do Twilio ou None
        """
        logger.info(f"📱 TWILIO: Iniciando envio SMS para {phone_e164}")
        
        if not self.is_configured():
            logger.error("❌ TWILIO: Não configurado - Account SID ou Auth Token ausentes")
            return None
        
        logger.info("✅ TWILIO: Configuração OK")
        
        try:
            import socket
            socket.setdefaulttimeout(10)  # Timeout de 10 segundos
            logger.info("⏱️ TWILIO: Timeout configurado para 10 segundos")
            
            # SEMPRE usar número direto do sandbox (mais confiável)
            logger.info(f"🔧 TWILIO: Usando número direto do sandbox: {self.sandbox_number}")
            message = self.client.messages.create(
                from_=self.sandbox_number,
                to=phone_e164,
                body=body
            )
            
            logger.info(f"✅ TWILIO: SMS ENVIADO COM SUCESSO para {phone_e164} (SID: {message.sid})")
            return message
            
        except Exception as e:
            logger.error(f"💥 TWILIO: ERRO ao enviar SMS para {phone_e164}: {str(e)}", exc_info=True)
            return None
    
    def send_with_fallback(self, phone_e164, body, preferred_channel='whatsapp'):
        """
        Envia com fallback (WhatsApp → SMS)
        """
        result = {
            'success': False,
            'channel_used': None,
            'message_sid': None,
            'error': None
        }
        
        # Tentar WhatsApp Sandbox primeiro
        if preferred_channel == 'whatsapp':
            msg = self.send_whatsapp_sandbox(phone_e164, body)
            if msg:
                result['success'] = True
                result['channel_used'] = 'whatsapp'
                result['message_sid'] = msg.sid
                return result
            
            # Fallback para SMS
            logger.info(f"→ Tentando fallback SMS para {phone_e164}")
            msg = self.send_sms(phone_e164, body)
            if msg:
                result['success'] = True
                result['channel_used'] = 'sms'
                result['message_sid'] = msg.sid
                return result
        else:
            # SMS direto
            msg = self.send_sms(phone_e164, body)
            if msg:
                result['success'] = True
                result['channel_used'] = 'sms'
                result['message_sid'] = msg.sid
                return result
        
        result['error'] = 'Falha ao enviar'
        return result
    
    def send_broadcast(self, phone_list, body, preferred_channel='whatsapp', evento=None):
        """
        Envia para múltiplos números
        """
        stats = {
            'total': len(phone_list),
            'sent': 0,
            'delivered': 0,
            'failed': 0,
            'results': []
        }
        
        for phone in phone_list:
            result = self.send_with_fallback(phone, body, preferred_channel)
            
            if result['success']:
                stats['sent'] += 1
                stats['delivered'] += 1
            else:
                stats['failed'] += 1
            
            stats['results'].append({
                'phone': phone,
                'success': result['success'],
                'channel': result['channel_used'],
                'sid': result['message_sid'],
                'error': result['error']
            })
        
        return stats
    
    def format_phone_e164(self, phone, country_code='55'):
        """Formata número para E.164"""
        digits = ''.join(filter(str.isdigit, phone))
        if not digits.startswith(country_code):
            digits = country_code + digits
        return f"+{digits}"
    
    def validate_phone_e164(self, phone):
        """Valida formato E.164"""
        if not phone.startswith('+'):
            return False
        digits = phone[1:]
        return digits.isdigit() and len(digits) >= 10 and len(digits) <= 15

