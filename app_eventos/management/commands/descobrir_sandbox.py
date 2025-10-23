"""
Comando para descobrir o nome do sandbox do Twilio
"""
from django.core.management.base import BaseCommand
from twilio.rest import Client
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Descobre o nome do sandbox do Twilio'

    def handle(self, *args, **options):
        self.stdout.write('🔍 DESCOBRINDO NOME DO SANDBOX')
        self.stdout.write('=' * 50)
        
        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            
            # Buscar informações da conta
            account = client.api.accounts(settings.TWILIO_ACCOUNT_SID).fetch()
            self.stdout.write(f'📋 Conta: {account.friendly_name}')
            self.stdout.write(f'📋 Status: {account.status}')
            
            # Buscar números de telefone
            phone_numbers = client.incoming_phone_numbers.list(limit=5)
            self.stdout.write(f'📱 Números de telefone: {len(phone_numbers)}')
            
            for number in phone_numbers:
                self.stdout.write(f'   📞 {number.phone_number} - {number.friendly_name}')
            
            # Verificar Messaging Service
            if settings.TWILIO_MESSAGING_SERVICE_SID:
                try:
                    service = client.messaging.v1.services(settings.TWILIO_MESSAGING_SERVICE_SID).fetch()
                    self.stdout.write(f'🔧 Messaging Service: {service.friendly_name}')
                    
                    # Buscar números do serviço
                    service_numbers = client.messaging.v1.services(settings.TWILIO_MESSAGING_SERVICE_SID).phone_numbers.list()
                    self.stdout.write(f'📱 Números no serviço: {len(service_numbers)}')
                    
                    for number in service_numbers:
                        self.stdout.write(f'   📞 {number.phone_number}')
                        
                except Exception as e:
                    self.stdout.write(f'❌ Erro ao verificar Messaging Service: {str(e)}')
            
            self.stdout.write('')
            self.stdout.write('💡 INSTRUÇÕES:')
            self.stdout.write('1. Acesse: https://console.twilio.com/')
            self.stdout.write('2. Vá em "Messaging" → "Try it out" → "Send a WhatsApp message"')
            self.stdout.write('3. O nome do sandbox aparece lá')
            self.stdout.write('4. Envie WhatsApp para +12292644322: "join <nome-do-sandbox>"')
            
        except Exception as e:
            self.stdout.write(f'❌ Erro: {str(e)}')
        
        self.stdout.write('✅ Verificação concluída!')
