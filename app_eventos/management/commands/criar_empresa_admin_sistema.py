"""
Comando para criar usuário admin do sistema
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = 'Cria usuário admin do sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin_sistema',
            help='Nome de usuário do admin do sistema'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@sistema.com',
            help='Email do admin do sistema'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin123',
            help='Senha do admin do sistema'
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        
        try:
            with transaction.atomic():
                # Verificar se já existe
                if User.objects.filter(username=username).exists():
                    self.stdout.write(
                        self.style.WARNING(f'Usuário {username} já existe!')
                    )
                    return
                
                # Criar usuário admin do sistema
                admin_sistema = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    tipo_usuario='admin_sistema',
                    is_staff=True,
                    is_superuser=True,
                    ativo=True,
                    first_name='Administrador',
                    last_name='do Sistema'
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Usuário admin do sistema criado com sucesso!')
                )
                self.stdout.write(f'Username: {username}')
                self.stdout.write(f'Email: {email}')
                self.stdout.write(f'Senha: {password}')
                self.stdout.write(f'Tipo: {admin_sistema.get_tipo_usuario_display()}')
                self.stdout.write(f'Staff: {admin_sistema.is_staff}')
                self.stdout.write(f'Superuser: {admin_sistema.is_superuser}')
                self.stdout.write(f'Ativo: {admin_sistema.ativo}')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao criar usuário: {str(e)}')
            )
