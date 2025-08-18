from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from app_eventos.models import EmpresaContratante

User = get_user_model()


class Command(BaseCommand):
    help = 'Verifica o status de um usuário'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username do usuário')

    def handle(self, *args, **options):
        username = options['username']
        
        try:
            user = User.objects.get(username=username)
            
            self.stdout.write(f'=== Status do Usuário: {username} ===')
            self.stdout.write(f'ID: {user.id}')
            self.stdout.write(f'Email: {user.email}')
            self.stdout.write(f'Tipo de Usuário: {user.tipo_usuario}')
            self.stdout.write(f'Ativo: {user.ativo}')
            self.stdout.write(f'is_staff: {user.is_staff}')
            self.stdout.write(f'is_active: {user.is_active}')
            self.stdout.write(f'is_superuser: {user.is_superuser}')
            
            if hasattr(user, 'empresa_contratante') and user.empresa_contratante:
                self.stdout.write(f'Empresa Contratante: {user.empresa_contratante.nome_fantasia}')
                self.stdout.write(f'Empresa Ativa: {user.empresa_contratante.ativo}')
            else:
                self.stdout.write('Empresa Contratante: Nenhuma')
            
            # Verifica permissões
            self.stdout.write('\n=== Permissões ===')
            self.stdout.write(f'Pode acessar admin: {user.is_staff}')
            self.stdout.write(f'Pode gerenciar empresa: {user.pode_gerenciar_empresa}')
            self.stdout.write(f'Pode operar sistema: {user.pode_operar_sistema}')
            
            # Verifica se tem dados para ver
            if user.empresa_contratante:
                from app_eventos.models import Evento, Equipamento, SetorEvento
                
                eventos = Evento.objects.filter(empresa_contratante=user.empresa_contratante)
                equipamentos = Equipamento.objects.filter(empresa_contratante=user.empresa_contratante)
                setores = SetorEvento.objects.filter(evento__empresa_contratante=user.empresa_contratante)
                
                self.stdout.write(f'\n=== Dados da Empresa ===')
                self.stdout.write(f'Eventos: {eventos.count()}')
                self.stdout.write(f'Equipamentos: {equipamentos.count()}')
                self.stdout.write(f'Setores: {setores.count()}')
            
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Usuário {username} não encontrado!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro ao verificar usuário: {str(e)}')
            )


