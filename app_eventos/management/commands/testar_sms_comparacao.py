from django.core.management.base import BaseCommand
from app_eventos.models import Freelance, Vaga
from app_eventos.services.twilio_service_sandbox import TwilioServiceSandbox
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Testa SMS usando o mesmo método das notificações para comparar'

    def handle(self, *args, **options):
        self.stdout.write('🧪 TESTE SMS COMPARAÇÃO')
        self.stdout.write('=' * 50)
        
        try:
            # Buscar freelancer Liandro
            freelancer = Freelance.objects.filter(nome_completo__icontains='Liandro').first()
            
            if not freelancer:
                self.stdout.write(self.style.ERROR("❌ Freelancer Liandro não encontrado"))
                return
            
            self.stdout.write(f"👤 Freelancer: {freelancer.nome_completo}")
            self.stdout.write(f"📱 Telefone: {freelancer.telefone}")
            
            # Buscar uma vaga de Segurança
            vaga = Vaga.objects.filter(funcao__nome='Segurança', ativa=True).first()
            
            if not vaga:
                self.stdout.write(self.style.ERROR("❌ Nenhuma vaga de Segurança encontrada"))
                return
            
            self.stdout.write(f"📋 Vaga: {vaga.id} - {vaga.funcao.nome}")
            
            # Criar mensagem igual às notificações
            mensagem = f"""🎉 NOVA VAGA DISPONÍVEL!

📅 Evento: {vaga.evento.nome if vaga.evento else "Evento"}
🏢 Setor: {vaga.setor.nome if vaga.setor else "Geral"}
💼 Função: {vaga.funcao.nome}
👥 Vagas: {vaga.quantidade}

💰 Valor: R$ {vaga.remuneracao:.2f}/{vaga.get_tipo_remuneracao_display()}
📝 Descrição: {vaga.descricao[:100]}{'...' if len(vaga.descricao) > 100 else ''}

🔗 Acesse: https://eventix-development.up.railway.app/

#Eventix #Vagas #Trabalho"""
            
            self.stdout.write(f"💬 Mensagem: {mensagem[:100]}...")
            self.stdout.write(f"📏 Tamanho: {len(mensagem)} caracteres")
            
            # Formatar telefone igual às notificações
            telefone_e164 = f"+55{freelancer.telefone}" if not freelancer.telefone.startswith('+') else freelancer.telefone
            self.stdout.write(f"📱 Telefone formatado: {telefone_e164}")
            
            # Usar o mesmo serviço das notificações
            twilio_service = TwilioServiceSandbox()
            
            if not twilio_service.is_configured():
                self.stdout.write(self.style.ERROR("❌ Twilio não configurado"))
                return
            
            self.stdout.write("✅ Twilio configurado")
            self.stdout.write(f"📱 Número sandbox: {twilio_service.sandbox_number}")
            
            # Enviar SMS
            self.stdout.write("\n🚀 Enviando SMS...")
            resultado = twilio_service.send_sms(telefone_e164, mensagem)
            
            if resultado:
                self.stdout.write(self.style.SUCCESS(f"✅ SUCESSO! SMS enviado (SID: {resultado.sid})"))
                self.stdout.write(f"📊 Status: {resultado.status}")
                self.stdout.write(f"📊 Para: {resultado.to}")
                self.stdout.write(f"📊 De: {resultado.from_}")
                self.stdout.write(f"📊 Data: {resultado.date_sent}")
            else:
                self.stdout.write(self.style.ERROR("❌ FALHA! Não foi possível enviar o SMS."))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ ERRO: {str(e)}"))
        
        self.stdout.write("\n✅ Teste concluído!")
