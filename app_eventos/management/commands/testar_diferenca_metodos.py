from django.core.management.base import BaseCommand
from app_eventos.models import Freelance
from app_eventos.services.twilio_service_sandbox import TwilioServiceSandbox
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Testa diferença entre método do botão teste e notificações'

    def handle(self, *args, **options):
        self.stdout.write('🧪 TESTE DIFERENÇA MÉTODOS')
        self.stdout.write('=' * 50)
        
        try:
            # Buscar freelancer Liandro
            freelancer = Freelance.objects.filter(nome_completo__icontains='Liandro').first()
            
            if not freelancer:
                self.stdout.write(self.style.ERROR("❌ Freelancer Liandro não encontrado"))
                return
            
            twilio_service = TwilioServiceSandbox()
            
            if not twilio_service.is_configured():
                self.stdout.write(self.style.ERROR("❌ Twilio não configurado"))
                return
            
            # TESTE 1: Método do botão "Teste SMS" (que funciona)
            self.stdout.write("\n🧪 TESTE 1: Método do botão 'Teste SMS'")
            telefone_teste = "+5551994523847"  # Hardcoded como no botão
            mensagem_teste = "🧪 TESTE SMS SIMPLES - Sistema funcionando perfeitamente! ✅"
            
            self.stdout.write(f"📱 Telefone: {telefone_teste}")
            self.stdout.write(f"💬 Mensagem: {mensagem_teste}")
            self.stdout.write(f"📏 Tamanho: {len(mensagem_teste)} caracteres")
            
            resultado1 = twilio_service.send_sms(telefone_teste, mensagem_teste)
            if resultado1:
                self.stdout.write(self.style.SUCCESS(f"✅ SMS 1 enviado (SID: {resultado1.sid})"))
            else:
                self.stdout.write(self.style.ERROR("❌ SMS 1 falhou"))
            
            # TESTE 2: Método das notificações (que não funciona)
            self.stdout.write("\n🔔 TESTE 2: Método das notificações")
            
            # Formatar telefone como nas notificações
            telefone = freelancer.telefone
            codigo_pais = freelancer.codigo_telefonico_pais or '55'
            
            if telefone.startswith('+'):
                telefone_e164 = telefone
            else:
                telefone_e164 = f"+{codigo_pais}{telefone}"
            
            mensagem_notificacao = """🎉 NOVA VAGA DISPONÍVEL!

📅 Evento: Teste
💼 Função: Segurança
👥 Vagas: 2
💰 Valor: R$ 120.00/Por Dia

🔗 Acesse: https://eventix-development.up.railway.app/

#Eventix #Vagas #Trabalho"""
            
            self.stdout.write(f"📱 Telefone: {telefone_e164}")
            self.stdout.write(f"💬 Mensagem: {mensagem_notificacao[:50]}...")
            self.stdout.write(f"📏 Tamanho: {len(mensagem_notificacao)} caracteres")
            
            resultado2 = twilio_service.send_sms(telefone_e164, mensagem_notificacao)
            if resultado2:
                self.stdout.write(self.style.SUCCESS(f"✅ SMS 2 enviado (SID: {resultado2.sid})"))
            else:
                self.stdout.write(self.style.ERROR("❌ SMS 2 falhou"))
            
            # COMPARAR
            self.stdout.write("\n📊 COMPARAÇÃO:")
            self.stdout.write(f"Telefone teste: {telefone_teste}")
            self.stdout.write(f"Telefone notificação: {telefone_e164}")
            self.stdout.write(f"São iguais: {telefone_teste == telefone_e164}")
            
            if telefone_teste == telefone_e164:
                self.stdout.write(self.style.SUCCESS("✅ Telefones são iguais - problema não é formatação"))
            else:
                self.stdout.write(self.style.WARNING("⚠️ Telefones são diferentes - pode ser o problema"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro: {str(e)}"))
        
        self.stdout.write('\n✅ Teste concluído!')
