from django.core.management.base import BaseCommand
from app_eventos.models import Freelance
from app_eventos.services.twilio_service_sandbox import TwilioServiceSandbox
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Debug exato da diferença entre os métodos'

    def handle(self, *args, **options):
        self.stdout.write('🔍 DEBUG EXATO - DIFERENÇA ENTRE MÉTODOS')
        self.stdout.write('=' * 60)
        
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
            
            self.stdout.write(f"👤 Freelancer: {freelancer.nome_completo}")
            self.stdout.write(f"📱 Telefone no banco: {freelancer.telefone}")
            self.stdout.write(f"🌍 Código país: {freelancer.codigo_telefonico_pais}")
            
            # MÉTODO 1: Exatamente como o botão "Teste SMS"
            self.stdout.write("\n🧪 MÉTODO 1: Botão 'Teste SMS' (FUNCIONA)")
            self.stdout.write("-" * 40)
            
            telefone_teste = "+5551994523847"  # Hardcoded
            mensagem_teste = "🧪 TESTE SMS SIMPLES - Sistema funcionando perfeitamente! ✅"
            
            self.stdout.write(f"📱 Telefone: {telefone_teste}")
            self.stdout.write(f"💬 Mensagem: {mensagem_teste}")
            self.stdout.write(f"📏 Tamanho: {len(mensagem_teste)} caracteres")
            self.stdout.write(f"🔧 Método: twilio_service.send_sms(telefone, mensagem)")
            
            # MÉTODO 2: Exatamente como as notificações
            self.stdout.write("\n🔔 MÉTODO 2: Botões 'Notificar' (NÃO FUNCIONA)")
            self.stdout.write("-" * 40)
            
            # Formatar telefone como nas notificações
            telefone = freelancer.telefone
            codigo_pais = freelancer.codigo_telefonico_pais or '55'
            
            if telefone.startswith('+'):
                telefone_e164 = telefone
            else:
                telefone_e164 = f"+{codigo_pais}{telefone}"
            
            mensagem_notificacao = """🎉 NOVA VAGA DISPONÍVEL!

📅 Evento: Opinião 42 anos
💼 Função: Segurança
👥 Vagas: 2
💰 Valor: R$ 120.00/Por Dia

🔗 Acesse: https://eventix-development.up.railway.app/

#Eventix #Vagas #Trabalho"""
            
            self.stdout.write(f"📱 Telefone: {telefone_e164}")
            self.stdout.write(f"💬 Mensagem: {mensagem_notificacao[:50]}...")
            self.stdout.write(f"📏 Tamanho: {len(mensagem_notificacao)} caracteres")
            self.stdout.write(f"🔧 Método: twilio_service.send_sms(telefone_e164, mensagem)")
            
            # COMPARAR DIFERENÇAS
            self.stdout.write("\n📊 COMPARAÇÃO DETALHADA:")
            self.stdout.write("-" * 40)
            self.stdout.write(f"Telefone teste:     {telefone_teste}")
            self.stdout.write(f"Telefone notificação: {telefone_e164}")
            self.stdout.write(f"Telefones iguais:   {telefone_teste == telefone_e164}")
            
            self.stdout.write(f"\nTamanho teste:      {len(mensagem_teste)} caracteres")
            self.stdout.write(f"Tamanho notificação: {len(mensagem_notificacao)} caracteres")
            self.stdout.write(f"Diferença tamanho:  {len(mensagem_notificacao) - len(mensagem_teste)} caracteres")
            
            # ÚNICA DIFERENÇA POSSÍVEL
            if telefone_teste == telefone_e164:
                self.stdout.write(self.style.SUCCESS("✅ Telefones são IDÊNTICOS"))
                self.stdout.write(self.style.WARNING("⚠️ ÚNICA DIFERENÇA: Tamanho da mensagem"))
                self.stdout.write("💡 TEORIA: Mensagens longas podem ser bloqueadas")
            else:
                self.stdout.write(self.style.ERROR("❌ Telefones são DIFERENTES"))
                self.stdout.write("💡 TEORIA: Formatação do telefone é o problema")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro: {str(e)}"))
        
        self.stdout.write('\n✅ Debug concluído!')
