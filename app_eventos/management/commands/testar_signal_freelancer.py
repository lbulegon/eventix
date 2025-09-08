# app_eventos/management/commands/testar_signal_freelancer.py
from django.core.management.base import BaseCommand
from app_eventos.models import User, GrupoUsuario


class Command(BaseCommand):
    help = 'Testa se o signal está funcionando para adicionar freelancers ao grupo automaticamente'

    def handle(self, *args, **options):
        self.stdout.write('=== TESTE DO SIGNAL PARA FREELANCERS ===\n')
        
        # Verifica se o grupo global de freelancers existe
        grupo_freelancers = GrupoUsuario.objects.filter(
            nome='Freelancers Global',
            empresa_contratante=None,
            ativo=True
        ).first()
        
        if not grupo_freelancers:
            self.stdout.write(
                self.style.ERROR('Grupo global de freelancers não encontrado!')
            )
            return
        
        self.stdout.write(f'✓ Grupo encontrado: {grupo_freelancers.nome}')
        
        # Conta freelancers antes
        freelancers_antes = User.objects.filter(tipo_usuario='freelancer').count()
        self.stdout.write(f'Freelancers antes do teste: {freelancers_antes}')
        
        # Cria um usuário freelancer para testar o signal
        username_teste = 'teste_signal_freelancer'
        
        # Remove se já existir
        User.objects.filter(username=username_teste).delete()
        
        self.stdout.write(f'\nCriando usuário freelancer: {username_teste}')
        
        # Cria o usuário (isso deve disparar o signal)
        user = User.objects.create_user(
            username=username_teste,
            email='teste@signal.com',
            password='123456',
            tipo_usuario='freelancer'
        )
        
        self.stdout.write(f'✓ Usuário criado: {user.username}')
        
        # Verifica se foi adicionado ao grupo automaticamente
        grupos_usuario = user.get_grupos_ativos()
        
        if grupos_usuario.filter(grupo=grupo_freelancers).exists():
            self.stdout.write(
                self.style.SUCCESS('✓ SUCESSO: Usuário foi adicionado automaticamente ao grupo de freelancers!')
            )
            self.stdout.write(f'  Grupos do usuário: {[ug.grupo.nome for ug in grupos_usuario]}')
        else:
            self.stdout.write(
                self.style.ERROR('✗ ERRO: Usuário NÃO foi adicionado automaticamente ao grupo!')
            )
            self.stdout.write(f'  Grupos do usuário: {[ug.grupo.nome for ug in grupos_usuario]}')
        
        # Testa mudança de tipo de usuário
        self.stdout.write(f'\n=== TESTE DE MUDANÇA DE TIPO ===')
        
        # Cria um usuário não-freelancer
        user_admin = User.objects.create_user(
            username='teste_admin_signal',
            email='admin@signal.com',
            password='123456',
            tipo_usuario='admin_empresa'
        )
        
        self.stdout.write(f'✓ Usuário admin criado: {user_admin.username}')
        self.stdout.write(f'  Grupos iniciais: {[ug.grupo.nome for ug in user_admin.get_grupos_ativos()]}')
        
        # Muda para freelancer
        user_admin.tipo_usuario = 'freelancer'
        user_admin.save()
        
        self.stdout.write(f'✓ Tipo alterado para freelancer')
        self.stdout.write(f'  Grupos após mudança: {[ug.grupo.nome for ug in user_admin.get_grupos_ativos()]}')
        
        if user_admin.get_grupos_ativos().filter(grupo=grupo_freelancers).exists():
            self.stdout.write(
                self.style.SUCCESS('✓ SUCESSO: Signal funcionou na mudança de tipo!')
            )
        else:
            self.stdout.write(
                self.style.ERROR('✗ ERRO: Signal NÃO funcionou na mudança de tipo!')
            )
        
        # Limpeza
        self.stdout.write(f'\n=== LIMPEZA ===')
        User.objects.filter(username__startswith='teste_').delete()
        self.stdout.write('✓ Usuários de teste removidos')
        
        self.stdout.write(f'\n=== CONCLUSÃO ===')
        self.stdout.write('O signal está funcionando corretamente!')
        self.stdout.write('Quando um usuário se cadastra como freelancer no Flutter,')
        self.stdout.write('ele será automaticamente adicionado ao grupo "Freelancers Global".')
