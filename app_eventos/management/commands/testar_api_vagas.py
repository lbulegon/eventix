# app_eventos/management/commands/testar_api_vagas.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from app_eventos.models import Vaga, Freelance

User = get_user_model()


class Command(BaseCommand):
    help = 'Testa a API de vagas para o usuário lbulegon'

    def handle(self, *args, **options):
        email = 'lbulegon@gmail.com'
        
        try:
            # Buscar usuário
            user = User.objects.get(email=email)
            self.stdout.write(f'👤 Usuário encontrado: {user.username} ({user.email})')
            
            # Verificar se é freelancer
            if user.tipo_usuario != 'freelancer':
                self.stdout.write(
                    self.style.ERROR(f'❌ Usuário {user.username} não é um freelancer!')
                )
                return

            # Buscar perfil freelancer
            try:
                freelance = user.freelance
                self.stdout.write(f'📋 Perfil freelancer: {freelance.nome_completo}')
                self.stdout.write(f'📋 Cadastro completo: {freelance.cadastro_completo}')
            except Freelance.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'❌ Perfil freelancer não encontrado!')
                )
                return

            # Gerar token JWT
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            self.stdout.write(f'🔑 Token gerado: {access_token[:50]}...')

            # Testar API de vagas
            client = Client()
            
            # Testar endpoint da API mobile
            url = '/api/v1/vagas/'
            headers = {
                'HTTP_AUTHORIZATION': f'Bearer {access_token}',
                'HTTP_CONTENT_TYPE': 'application/json'
            }
            
            self.stdout.write(f'🌐 Testando URL: {url}')
            response = client.get(url, **headers)
            
            self.stdout.write(f'📊 Status da resposta: {response.status_code}')
            
            if response.status_code == 200:
                data = response.json()
                count = data.get('count', 0)
                results = data.get('results', [])
                
                self.stdout.write(f'✅ Sucesso! Vagas encontradas: {count}')
                self.stdout.write(f'📋 Vagas retornadas: {len(results)}')
                
                if results:
                    self.stdout.write(f'\n🎯 Primeiras 3 vagas:')
                    for i, vaga in enumerate(results[:3]):
                        self.stdout.write(f'   {i+1}. {vaga.get("titulo", "Sem título")}')
                        self.stdout.write(f'      - Função: {vaga.get("funcao", {}).get("nome", "N/A")}')
                        self.stdout.write(f'      - Evento: {vaga.get("setor", {}).get("evento", {}).get("nome", "N/A")}')
                        self.stdout.write(f'      - Ativa: {vaga.get("ativa", False)}')
                        self.stdout.write(f'      - Publicada: {vaga.get("publicada", False)}')
                        self.stdout.write('')
                else:
                    self.stdout.write('⚠️  Nenhuma vaga retornada na resposta')
                    
            else:
                self.stdout.write(f'❌ Erro na API: {response.status_code}')
                self.stdout.write(f'📄 Resposta: {response.content.decode()}')
                
            # Testar também vagas recomendadas
            url_recomendadas = '/api/v1/vagas/recomendadas/'
            self.stdout.write(f'\n🌐 Testando URL: {url_recomendadas}')
            response_rec = client.get(url_recomendadas, **headers)
            
            self.stdout.write(f'📊 Status da resposta (recomendadas): {response_rec.status_code}')
            
            if response_rec.status_code == 200:
                data_rec = response_rec.json()
                count_rec = data_rec.get('count', 0)
                results_rec = data_rec.get('results', [])
                
                self.stdout.write(f'✅ Vagas recomendadas: {count_rec}')
                self.stdout.write(f'📋 Vagas recomendadas retornadas: {len(results_rec)}')
            else:
                self.stdout.write(f'❌ Erro nas vagas recomendadas: {response_rec.status_code}')
                self.stdout.write(f'📄 Resposta: {response_rec.content.decode()}')

        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'❌ Usuário com email "{email}" não encontrado!')
            )

