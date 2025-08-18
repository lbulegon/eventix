from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from app_eventos.models import EmpresaContratante, TipoEmpresa

User = get_user_model()


class Command(BaseCommand):
    help = 'Cria um usuário de teste para uma empresa contratante'

    def handle(self, *args, **options):
        try:
            # Busca a empresa contratante UP Mix
            empresa_contratante = EmpresaContratante.objects.get(nome_fantasia='UP Mix')
            
            # Cria um usuário admin da empresa
            username = 'admin_upmix'
            email = 'admin@upmix.com'
            
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password='admin123',
                    first_name='Admin',
                    last_name='UP Mix',
                    tipo_usuario='admin_empresa',
                    empresa_contratante=empresa_contratante,
                    ativo=True,
                    is_staff=True,
                    is_active=True
                )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Usuário criado com sucesso!\n'
                        f'Username: {username}\n'
                        f'Email: {email}\n'
                        f'Senha: admin123\n'
                        f'Empresa: {empresa_contratante.nome_fantasia}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Usuário {username} já existe!')
                )
                
            # Cria um usuário operador da empresa
            username_operador = 'operador_upmix'
            email_operador = 'operador@upmix.com'
            
            if not User.objects.filter(username=username_operador).exists():
                user_operador = User.objects.create_user(
                    username=username_operador,
                    email=email_operador,
                    password='operador123',
                    first_name='Operador',
                    last_name='UP Mix',
                    tipo_usuario='operador_empresa',
                    empresa_contratante=empresa_contratante,
                    ativo=True,
                    is_staff=True,
                    is_active=True
                )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Operador criado com sucesso!\n'
                        f'Username: {username_operador}\n'
                        f'Email: {email_operador}\n'
                        f'Senha: operador123\n'
                        f'Empresa: {empresa_contratante.nome_fantasia}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Operador {username_operador} já existe!')
                )
                
        except EmpresaContratante.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Empresa contratante "UP Mix" não encontrada!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro ao criar usuários: {str(e)}')
            )
