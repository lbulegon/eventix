"""
Comando para debugar Twilio no Railway
"""
from django.core.management.base import BaseCommand
from django.conf import settings
import requests
import socket


class Command(BaseCommand):
    help = 'Debug Twilio no Railway'

    def handle(self, *args, **options):
        self.stdout.write('🔍 DEBUG TWILIO NO RAILWAY')
        self.stdout.write('=' * 50)
        
        # 1. Verificar variáveis
        self.stdout.write('\n📋 1. VERIFICANDO VARIÁVEIS:')
        self.stdout.write(f'TWILIO_ACCOUNT_SID: {settings.TWILIO_ACCOUNT_SID[:10] + "..." if settings.TWILIO_ACCOUNT_SID else "NÃO CONFIGURADO"}')
        self.stdout.write(f'TWILIO_AUTH_TOKEN: {"Configurado" if settings.TWILIO_AUTH_TOKEN else "NÃO CONFIGURADO"}')
        self.stdout.write(f'TWILIO_MESSAGING_SERVICE_SID: {settings.TWILIO_MESSAGING_SERVICE_SID[:10] + "..." if settings.TWILIO_MESSAGING_SERVICE_SID else "NÃO CONFIGURADO"}')
        
        # 2. Testar conectividade
        self.stdout.write('\n🌐 2. TESTANDO CONECTIVIDADE:')
        try:
            response = requests.get('https://api.twilio.com', timeout=5)
            self.stdout.write(f'✅ API Twilio acessível: {response.status_code}')
        except requests.exceptions.Timeout:
            self.stdout.write('❌ TIMEOUT: API Twilio não responde em 5s')
        except requests.exceptions.ConnectionError:
            self.stdout.write('❌ CONEXÃO: Não consegue conectar com API Twilio')
        except Exception as e:
            self.stdout.write(f'❌ ERRO: {str(e)}')
        
        # 3. Testar DNS
        self.stdout.write('\n🔍 3. TESTANDO DNS:')
        try:
            ip = socket.gethostbyname('api.twilio.com')
            self.stdout.write(f'✅ DNS resolve: {ip}')
        except Exception as e:
            self.stdout.write(f'❌ DNS falha: {str(e)}')
        
        # 4. Testar autenticação básica
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            self.stdout.write('\n🔑 4. TESTANDO AUTENTICAÇÃO:')
            try:
                import base64
                auth_string = f"{settings.TWILIO_ACCOUNT_SID}:{settings.TWILIO_AUTH_TOKEN}"
                auth_bytes = auth_string.encode('ascii')
                auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
                
                headers = {'Authorization': f'Basic {auth_b64}'}
                response = requests.get(
                    f'https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}.json',
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    self.stdout.write('✅ Autenticação OK')
                else:
                    self.stdout.write(f'❌ Autenticação falhou: {response.status_code}')
                    
            except Exception as e:
                self.stdout.write(f'❌ Erro na autenticação: {str(e)}')
        
        self.stdout.write('\n✅ Debug concluído!')

