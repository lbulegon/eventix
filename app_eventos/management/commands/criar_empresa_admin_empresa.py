"""
Comando para criar usuário admin da empresa
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from app_eventos.models import EmpresaContratante

User = get_user_model()


class Command(BaseCommand):
    help = 'Cria usuário admin da empresa'

    def add_arguments(self, parser):
        parser.add_argument(
            '--empresa-id',
            type=int,
            help='ID da empresa contratante'
        )
        parser.add_argument(
            '--username',
            type=str,
            default='admin_empresa',
            help='Nome de usuário do admin da empresa'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@empresa.com',
            help='Email do admin da empresa'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin123',
            help='Senha do admin da empresa'
        )

    def handle(self, *args, **options):
        empresa_id = options.get('empresa_id')
        username = options['username']
        email = options['email']
        password = options['password']
        
        try:
            # Buscar empresa
            if empresa_id:
                empresa = EmpresaContratante.objects.get(id=empresa_id)
            else:
                empresa = EmpresaContratante.objects.filter(ativo=True).first()
            
            if not empresa:
                self.stdout.write('Nenhuma empresa contratante encontrada!')
                return
            
            # Verificar se já existe
            if User.objects.filter(username=username).exists():
                self.stdout.write('Usuario ja existe!')
                return
            
            # Criar usuário admin da empresa
            admin_empresa = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                tipo_usuario='admin_empresa',
                empresa_contratante=empresa,
                is_staff=True,
                is_superuser=False,
                ativo=True,
                first_name='Administrador',
                last_name=f'da {empresa.nome_fantasia}'
            )
            
            self.stdout.write('Usuario admin da empresa criado com sucesso!')
            self.stdout.write(f'Username: {username}')
            self.stdout.write(f'Email: {email}')
            self.stdout.write(f'Senha: {password}')
            self.stdout.write(f'Tipo: {admin_empresa.get_tipo_usuario_display()}')
            self.stdout.write(f'Empresa: {empresa.nome_fantasia}')
            self.stdout.write(f'CNPJ: {empresa.cnpj}')
            self.stdout.write(f'Staff: {admin_empresa.is_staff}')
            self.stdout.write(f'Ativo: {admin_empresa.ativo}')
            
        except EmpresaContratante.DoesNotExist:
            self.stdout.write('Empresa contratante nao encontrada!')
        except Exception as e:
            self.stdout.write(f'Erro ao criar usuario: {str(e)}')
