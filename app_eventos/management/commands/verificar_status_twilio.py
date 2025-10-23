from django.core.management.base import BaseCommand
from twilio.rest import Client
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Verifica o status real das mensagens SMS no Twilio'

    def handle(self, *args, **options):
        self.stdout.write('🔍 VERIFICANDO STATUS REAL DAS MENSAGENS')
        self.stdout.write('=' * 50)
        
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        
        if not account_sid or not auth_token:
            self.stdout.write(self.style.ERROR("❌ Credenciais Twilio não configuradas."))
            return
        
        client = Client(account_sid, auth_token)
        
        try:
            self.stdout.write('\n📱 Últimas 5 mensagens enviadas:\n')
            messages = client.messages.list(limit=5)
            
            for msg in messages:
                status_icon = "✅" if msg.status == 'delivered' else "❌" if msg.status == 'failed' else "⏳"
                self.stdout.write(f"{status_icon} SID: {msg.sid}")
                self.stdout.write(f"   Para: {msg.to}")
                self.stdout.write(f"   De: {msg.from_}")
                self.stdout.write(f"   Status: {msg.status}")
                self.stdout.write(f"   Data: {msg.date_sent}")
                self.stdout.write(f"   Erro: {msg.error_code} - {msg.error_message}")
                self.stdout.write(f"   Preço: {msg.price} {msg.price_unit}")
                self.stdout.write("")
            
            # Verificar se há mensagens com erro
            failed_messages = [msg for msg in messages if msg.status == 'failed']
            if failed_messages:
                self.stdout.write(self.style.ERROR(f"❌ {len(failed_messages)} mensagens falharam!"))
                for msg in failed_messages:
                    self.stdout.write(f"   Erro: {msg.error_code} - {msg.error_message}")
            else:
                self.stdout.write(self.style.SUCCESS("✅ Nenhuma mensagem falhou"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro ao buscar mensagens: {str(e)}"))
        
        self.stdout.write('\n✅ Verificação concluída!')
