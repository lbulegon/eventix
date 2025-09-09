# app_eventos/management/commands/completar_cadastro_lbulegon.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from app_eventos.models import Freelance

User = get_user_model()


class Command(BaseCommand):
    help = 'Marca o cadastro do freelancer lbulegon como completo para fins de teste'

    def handle(self, *args, **options):
        email = 'lbulegon@gmail.com'
        
        try:
            # Buscar usuário pelo email
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
                self.stdout.write(f'📋 Perfil freelancer encontrado: {freelance.nome_completo}')
            except Freelance.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'❌ Perfil freelancer não encontrado para {user.username}!')
                )
                return

            # Verificar status atual
            self.stdout.write(f'📊 Status atual do cadastro:')
            self.stdout.write(f'   - Cadastro completo: {freelance.cadastro_completo}')
            self.stdout.write(f'   - Exame médico: {"✅" if freelance.arquivo_exame_medico else "❌"}')
            self.stdout.write(f'   - Comprovante residência: {"✅" if freelance.arquivo_comprovante_residencia else "❌"}')
            self.stdout.write(f'   - Identidade frente: {"✅" if freelance.arquivo_identidade_frente else "❌"}')
            self.stdout.write(f'   - Identidade verso: {"✅" if freelance.arquivo_identidade_verso else "❌"}')

            # Para fins de teste, vamos marcar como completo
            freelance.cadastro_completo = True
            freelance.save()
            
            self.stdout.write(f'\n✅ Cadastro marcado como COMPLETO para fins de teste!')
            self.stdout.write(f'🎯 Agora o usuário {user.username} deve conseguir ver as vagas no Flutter!')
            self.stdout.write(f'📱 Teste o app Flutter para confirmar que as vagas aparecem.')

        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'❌ Usuário com email "{email}" não encontrado!')
            )

