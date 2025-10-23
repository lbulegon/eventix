"""
Comando para testar SMS direto (sem Messaging Service)
"""
from django.core.management.base import BaseCommand
from app_eventos.services.twilio_service_sandbox import TwilioServiceSandbox
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Testa SMS direto usando número do sandbox'

    def add_arguments(self, parser):
        parser.add_argument('--telefone', type=str, default='+5551994523847', help='Número para testar')
        parser.add_argument('--mensagem', type=str, default='Teste SMS direto do Railway', help='Mensagem de teste')

    def handle(self, *args, **options):
        telefone = options['telefone']
        mensagem = options['mensagem']
        
        self.stdout.write('📱 TESTE SMS DIRETO (SEM MESSAGING SERVICE)')
        self.stdout.write('=' * 50)
        self.stdout.write(f'📞 Telefone: {telefone}')
        self.stdout.write(f'💬 Mensagem: {mensagem}')
        self.stdout.write('')
        
        try:
            service = TwilioServiceSandbox()
            
            if not service.is_configured():
                self.stdout.write('❌ Twilio não configurado')
                return
            
            self.stdout.write('✅ Twilio configurado')
            self.stdout.write(f'📱 Número sandbox: {service.sandbox_number}')
            self.stdout.write('')
            
            self.stdout.write('🚀 Enviando SMS...')
            resultado = service.send_sms(telefone, mensagem)
            
            if resultado:
                self.stdout.write(f'✅ SUCESSO! SMS enviado (SID: {resultado.sid})')
                self.stdout.write(f'📊 Status: {resultado.status}')
            else:
                self.stdout.write('❌ FALHA! SMS não foi enviado')
                
        except Exception as e:
            self.stdout.write(f'💥 ERRO: {str(e)}')
        
        self.stdout.write('')
        self.stdout.write('✅ Teste concluído!')
