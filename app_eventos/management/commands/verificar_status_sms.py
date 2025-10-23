"""
Comando para verificar o status real das mensagens SMS no Twilio
"""
from django.core.management.base import BaseCommand
from twilio.rest import Client
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Verifica o status real das mensagens SMS no Twilio'

    def handle(self, *args, **options):
        self.stdout.write('🔍 VERIFICANDO STATUS DAS MENSAGENS SMS')
        self.stdout.write('=' * 50)
        
        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            
            # Buscar últimas 10 mensagens
            messages = client.messages.list(limit=10)
            
            self.stdout.write(f'📱 Últimas {len(messages)} mensagens:')
            self.stdout.write('')
            
            for msg in messages:
                status_emoji = {
                    'queued': '⏳',
                    'sent': '📤',
                    'delivered': '✅',
                    'failed': '❌',
                    'undelivered': '⚠️'
                }.get(msg.status, '❓')
                
                self.stdout.write(f'{status_emoji} SID: {msg.sid}')
                self.stdout.write(f'   Para: {msg.to}')
                self.stdout.write(f'   Status: {msg.status}')
                self.stdout.write(f'   Data: {msg.date_sent}')
                self.stdout.write(f'   Erro: {getattr(msg, "error_code", "N/A")} - {getattr(msg, "error_message", "N/A")}')
                self.stdout.write('')
            
            # Verificar configuração do Messaging Service
            if settings.TWILIO_MESSAGING_SERVICE_SID:
                try:
                    service = client.messaging.v1.services(settings.TWILIO_MESSAGING_SERVICE_SID).fetch()
                    self.stdout.write(f'🔧 Messaging Service: {service.friendly_name}')
                    self.stdout.write(f'   Status: {service.status}')
                    self.stdout.write(f'   Números: {len(service.phone_numbers.list())}')
                except Exception as e:
                    self.stdout.write(f'❌ Erro ao verificar Messaging Service: {str(e)}')
            
        except Exception as e:
            self.stdout.write(f'❌ Erro: {str(e)}')
        
        self.stdout.write('✅ Verificação concluída!')
