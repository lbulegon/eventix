"""
Serviço de Integração com Twilio (WhatsApp + SMS)
"""
from twilio.rest import Client
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class TwilioService:
    """
    Serviço para enviar mensagens via Twilio (WhatsApp e SMS)
    """
    
    def __init__(self):
        self.account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
        self.auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
        self.verify_sid = getattr(settings, 'TWILIO_VERIFY_SID', None)
        self.messaging_service_sid = getattr(settings, 'TWILIO_MESSAGING_SERVICE_SID', None)
        
        if not self.account_sid or not self.auth_token:
            logger.warning("AVISO: Credenciais Twilio não configuradas")
            self.client = None
        else:
            self.client = Client(self.account_sid, self.auth_token)
    
    def is_configured(self):
        """Verifica se o Twilio está configurado"""
        return self.client is not None
    
    # ========== VERIFY (Códigos OTP) ==========
    
    def start_verify(self, phone_e164, channel='whatsapp', locale='pt-BR'):
        """
        Inicia verificação enviando código OTP
        
        Args:
            phone_e164: Número no formato E.164 (+55DDDNNNNNNN)
            channel: 'sms' ou 'whatsapp'
            locale: Idioma da mensagem (pt-BR padrão)
        
        Returns:
            Objeto Verification do Twilio ou None
        """
        if not self.is_configured() or not self.verify_sid:
            logger.error("Twilio Verify não configurado")
            return None
        
        try:
            # Formato do número baseado no canal
            to_number = phone_e164 if channel == 'sms' else f"whatsapp:{phone_e164}"
            
            verification = self.client.verify.v2 \
                .services(self.verify_sid) \
                .verifications \
                .create(
                    to=to_number,
                    channel=channel,
                    locale=locale
                )
            
            logger.info(f"✓ Código OTP enviado via {channel} para {phone_e164}")
            return verification
            
        except Exception as e:
            logger.error(f"✗ Erro ao enviar OTP via {channel}: {str(e)}")
            return None
    
    def check_verify(self, phone_e164, code, channel='whatsapp'):
        """
        Verifica código OTP
        
        Args:
            phone_e164: Número no formato E.164
            code: Código de 6 dígitos
            channel: 'sms' ou 'whatsapp'
        
        Returns:
            True se verificado, False caso contrário
        """
        if not self.is_configured() or not self.verify_sid:
            logger.error("Twilio Verify não configurado")
            return False
        
        try:
            # Formato do número baseado no canal
            to_number = phone_e164 if channel == 'sms' else f"whatsapp:{phone_e164}"
            
            verification_check = self.client.verify.v2 \
                .services(self.verify_sid) \
                .verification_checks \
                .create(
                    to=to_number,
                    code=code
                )
            
            is_approved = verification_check.status == 'approved'
            
            if is_approved:
                logger.info(f"✓ Código verificado com sucesso para {phone_e164}")
            else:
                logger.warning(f"✗ Código inválido para {phone_e164}")
            
            return is_approved
            
        except Exception as e:
            logger.error(f"✗ Erro ao verificar código: {str(e)}")
            return False
    
    # ========== MENSAGENS (WhatsApp + SMS) ==========
    
    def send_whatsapp(self, phone_e164, body):
        """
        Envia mensagem via WhatsApp
        
        Args:
            phone_e164: Número no formato E.164
            body: Corpo da mensagem
        
        Returns:
            Message object do Twilio ou None
        """
        if not self.is_configured():
            logger.error("Twilio não configurado")
            return None
        
        try:
            message = self.client.messages.create(
                to=f"whatsapp:{phone_e164}",
                messaging_service_sid=self.messaging_service_sid,
                body=body
            )
            
            logger.info(f"✓ WhatsApp enviado para {phone_e164} (SID: {message.sid})")
            return message
            
        except Exception as e:
            logger.error(f"✗ Erro ao enviar WhatsApp: {str(e)}")
            return None
    
    def send_sms(self, phone_e164, body):
        """
        Envia SMS
        
        Args:
            phone_e164: Número no formato E.164
            body: Corpo da mensagem
        
        Returns:
            Message object do Twilio ou None
        """
        if not self.is_configured():
            logger.error("Twilio não configurado")
            return None
        
        try:
            message = self.client.messages.create(
                to=phone_e164,
                messaging_service_sid=self.messaging_service_sid,
                body=body
            )
            
            logger.info(f"✓ SMS enviado para {phone_e164} (SID: {message.sid})")
            return message
            
        except Exception as e:
            logger.error(f"✗ Erro ao enviar SMS: {str(e)}")
            return None
    
    def send_with_fallback(self, phone_e164, body, preferred_channel='whatsapp'):
        """
        Envia mensagem com fallback automático
        WhatsApp → se falhar → SMS
        
        Args:
            phone_e164: Número no formato E.164
            body: Corpo da mensagem
            preferred_channel: 'whatsapp' ou 'sms'
        
        Returns:
            dict com resultado {success, channel_used, message_sid, error}
        """
        result = {
            'success': False,
            'channel_used': None,
            'message_sid': None,
            'error': None
        }
        
        # Tentar canal preferencial
        if preferred_channel == 'whatsapp':
            msg = self.send_whatsapp(phone_e164, body)
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
            # Enviar direto por SMS
            msg = self.send_sms(phone_e164, body)
            if msg:
                result['success'] = True
                result['channel_used'] = 'sms'
                result['message_sid'] = msg.sid
                return result
        
        result['error'] = 'Falha ao enviar por ambos os canais'
        return result
    
    # ========== BROADCAST (Envio em Massa) ==========
    
    def send_broadcast(self, phone_list, body, preferred_channel='whatsapp', evento=None):
        """
        Envia mensagem para múltiplos números
        
        Args:
            phone_list: Lista de números no formato E.164
            body: Corpo da mensagem
            preferred_channel: 'whatsapp' ou 'sms'
            evento: Objeto Evento (opcional)
        
        Returns:
            dict com estatísticas {total, sent, delivered, failed, results}
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
                stats['delivered'] += 1  # Será atualizado pelo webhook
            else:
                stats['failed'] += 1
            
            stats['results'].append({
                'phone': phone,
                'success': result['success'],
                'channel': result['channel_used'],
                'sid': result['message_sid'],
                'error': result['error']
            })
        
        logger.info(f"✓ Broadcast concluído: {stats['sent']}/{stats['total']} enviados")
        return stats
    
    # ========== TEMPLATES PRÉ-DEFINIDOS ==========
    
    def send_onboarding_code(self, phone_e164, code, channel='whatsapp'):
        """Envia código de onboarding usando template aprovado"""
        body = f"""🎉 *Eventix*

Seu código de acesso é: *{code}*

⏰ Expira em 10 minutos.
🔒 Não compartilhe este código.

Bem-vindo ao Eventix!"""
        
        return self.send_with_fallback(phone_e164, body, channel)
    
    def send_vaga_notification(self, phone_e164, vaga, evento):
        """Envia notificação de nova vaga"""
        body = f"""💼 *Nova Vaga Disponível!*

*{vaga.titulo}*
💰 R$ {vaga.remuneracao} ({vaga.get_tipo_remuneracao_display()})

📅 Evento: {evento.nome}
📍 Local: {evento.local.nome if evento.local else 'A definir'}

🔗 Acesse o app Eventix para se candidatar!"""
        
        return self.send_with_fallback(phone_e164, body, 'whatsapp')
    
    def send_candidatura_aprovada(self, phone_e164, candidatura):
        """Notifica aprovação de candidatura"""
        vaga = candidatura.vaga
        evento = vaga.setor.evento if vaga.setor else vaga.evento
        
        body = f"""✅ *Candidatura Aprovada!*

Parabéns! Você foi aprovado para:

*{vaga.titulo}*
📅 Evento: {evento.nome}
📍 {evento.local.nome if evento.local else 'Local a confirmar'}
🗓️ Data: {evento.data_inicio.strftime('%d/%m/%Y')}

Em breve você receberá mais informações.

🎉 Nos vemos lá!"""
        
        return self.send_with_fallback(phone_e164, body, 'whatsapp')
    
    def send_alerta_emergencia(self, phone_e164, mensagem):
        """Envia alerta de emergência/atualização"""
        body = f"""⚠️ *EVENTIX - Atualização Importante*

{mensagem}

Para mais informações, acesse o app Eventix."""
        
        return self.send_with_fallback(phone_e164, body, 'whatsapp')
    
    # ========== UTILIDADES ==========
    
    def format_phone_e164(self, phone, country_code='55'):
        """
        Formata número para E.164
        
        Examples:
            (11) 99999-9999 → +5511999999999
            11999999999 → +5511999999999
        """
        # Remove caracteres não numéricos
        digits = ''.join(filter(str.isdigit, phone))
        
        # Adiciona código do país se não tiver
        if not digits.startswith(country_code):
            digits = country_code + digits
        
        return f"+{digits}"
    
    def validate_phone_e164(self, phone):
        """Valida formato E.164"""
        if not phone.startswith('+'):
            return False
        digits = phone[1:]
        return digits.isdigit() and len(digits) >= 10 and len(digits) <= 15

