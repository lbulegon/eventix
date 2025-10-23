from django.core.management.base import BaseCommand
from app_eventos.services.twilio_service_sandbox import TwilioServiceSandbox
import time
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Testa rate limiting do Twilio enviando múltiplos SMS'

    def handle(self, *args, **options):
        self.stdout.write('🧪 TESTE RATE LIMITING TWILIO')
        self.stdout.write('=' * 50)
        
        telefone = "+5551994523847"
        mensagem_teste = "🧪 TESTE RATE LIMITING - SMS {}"
        
        twilio_service = TwilioServiceSandbox()
        
        if not twilio_service.is_configured():
            self.stdout.write(self.style.ERROR("❌ Twilio não configurado"))
            return
        
        self.stdout.write(f"📱 Telefone: {telefone}")
        self.stdout.write(f"📱 Número sandbox: {twilio_service.sandbox_number}")
        
        # Teste 1: SMS imediato
        self.stdout.write("\n🚀 TESTE 1: SMS imediato")
        resultado1 = twilio_service.send_sms(telefone, mensagem_teste.format("1"))
        if resultado1:
            self.stdout.write(self.style.SUCCESS(f"✅ SMS 1 enviado (SID: {resultado1.sid})"))
        else:
            self.stdout.write(self.style.ERROR("❌ SMS 1 falhou"))
        
        # Aguardar 5 segundos
        self.stdout.write("\n⏰ Aguardando 5 segundos...")
        time.sleep(5)
        
        # Teste 2: SMS após 5 segundos
        self.stdout.write("\n🚀 TESTE 2: SMS após 5 segundos")
        resultado2 = twilio_service.send_sms(telefone, mensagem_teste.format("2"))
        if resultado2:
            self.stdout.write(self.style.SUCCESS(f"✅ SMS 2 enviado (SID: {resultado2.sid})"))
        else:
            self.stdout.write(self.style.ERROR("❌ SMS 2 falhou"))
        
        # Aguardar 10 segundos
        self.stdout.write("\n⏰ Aguardando 10 segundos...")
        time.sleep(10)
        
        # Teste 3: SMS após 10 segundos
        self.stdout.write("\n🚀 TESTE 3: SMS após 10 segundos")
        resultado3 = twilio_service.send_sms(telefone, mensagem_teste.format("3"))
        if resultado3:
            self.stdout.write(self.style.SUCCESS(f"✅ SMS 3 enviado (SID: {resultado3.sid})"))
        else:
            self.stdout.write(self.style.ERROR("❌ SMS 3 falhou"))
        
        self.stdout.write("\n📊 RESULTADO:")
        self.stdout.write(f"SMS 1: {'✅' if resultado1 else '❌'}")
        self.stdout.write(f"SMS 2: {'✅' if resultado2 else '❌'}")
        self.stdout.write(f"SMS 3: {'✅' if resultado3 else '❌'}")
        
        if resultado1 and resultado2 and resultado3:
            self.stdout.write(self.style.SUCCESS("✅ Rate limiting não é o problema"))
        else:
            self.stdout.write(self.style.WARNING("⚠️ Possível rate limiting detectado"))
        
        self.stdout.write("\n✅ Teste concluído!")
