# app_eventos/management/commands/gerenciar_usuarios_grupos.py
from django.core.management.base import BaseCommand
from django.db import transaction
from app_eventos.models import User, GrupoUsuario, UsuarioGrupo


class Command(BaseCommand):
    help = 'Gerencia usuários em grupos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--usuario',
            type=str,
            help='Username do usuário',
        )
        parser.add_argument(
            '--grupo',
            type=str,
            help='Nome do grupo',
        )
        parser.add_argument(
            '--acao',
            type=str,
            choices=['adicionar', 'remover', 'listar'],
            help='Ação a ser executada',
        )
        parser.add_argument(
            '--listar-grupos',
            action='store_true',
            help='Lista todos os grupos disponíveis',
        )
        parser.add_argument(
            '--listar-usuarios',
            action='store_true',
            help='Lista todos os usuários',
        )

    def handle(self, *args, **options):
        if options.get('listar_grupos'):
            self.listar_grupos()
            return
        
        if options.get('listar_usuarios'):
            self.listar_usuarios()
            return
        
        usuario = options.get('usuario')
        grupo = options.get('grupo')
        acao = options.get('acao')
        
        if not all([usuario, grupo, acao]):
            self.stdout.write(
                self.style.ERROR('É necessário fornecer --usuario, --grupo e --acao')
            )
            return
        
        try:
            user = User.objects.get(username=usuario)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Usuário "{usuario}" não encontrado')
            )
            return
        
        try:
            grupo_obj = GrupoUsuario.objects.get(nome=grupo)
        except GrupoUsuario.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Grupo "{grupo}" não encontrado')
            )
            return
        
        with transaction.atomic():
            if acao == 'adicionar':
                self.adicionar_usuario_grupo(user, grupo_obj)
            elif acao == 'remover':
                self.remover_usuario_grupo(user, grupo_obj)
            elif acao == 'listar':
                self.listar_grupos_usuario(user)

    def adicionar_usuario_grupo(self, user, grupo):
        """Adiciona usuário a um grupo"""
        usuario_grupo, created = user.adicionar_ao_grupo(grupo)
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Usuário "{user.username}" adicionado ao grupo "{grupo.nome}"'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'Usuário "{user.username}" já estava no grupo "{grupo.nome}" (reativado)'
                )
            )

    def remover_usuario_grupo(self, user, grupo):
        """Remove usuário de um grupo"""
        sucesso = user.remover_do_grupo(grupo)
        
        if sucesso:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Usuário "{user.username}" removido do grupo "{grupo.nome}"'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'Usuário "{user.username}" não estava no grupo "{grupo.nome}"'
                )
            )

    def listar_grupos_usuario(self, user):
        """Lista os grupos de um usuário"""
        grupos = user.get_grupos_ativos()
        
        self.stdout.write(f'\nGrupos do usuário "{user.username}":')
        if grupos:
            for usuario_grupo in grupos:
                grupo = usuario_grupo.grupo
                empresa = grupo.empresa_contratante.nome_fantasia if grupo.empresa_contratante else 'Sistema'
                self.stdout.write(f'  - {grupo.nome} ({empresa}) - {grupo.tipo_grupo}')
        else:
            self.stdout.write('  Nenhum grupo encontrado')
        
        # Listar permissões
        permissoes = user.get_permissoes()
        self.stdout.write(f'\nPermissões do usuário "{user.username}":')
        if permissoes:
            for permissao in sorted(permissoes):
                self.stdout.write(f'  - {permissao}')
        else:
            self.stdout.write('  Nenhuma permissão encontrada')

    def listar_grupos(self):
        """Lista todos os grupos disponíveis"""
        grupos = GrupoUsuario.objects.filter(ativo=True).order_by('tipo_grupo', 'nome')
        
        self.stdout.write('\nGrupos disponíveis:')
        tipo_atual = None
        for grupo in grupos:
            if grupo.tipo_grupo != tipo_atual:
                tipo_atual = grupo.tipo_grupo
                self.stdout.write(f'\n{tipo_atual.upper()}:')
            
            empresa = grupo.empresa_contratante.nome_fantasia if grupo.empresa_contratante else 'Sistema'
            self.stdout.write(f'  - {grupo.nome} ({empresa})')
            self.stdout.write(f'    Descrição: {grupo.descricao}')

    def listar_usuarios(self):
        """Lista todos os usuários"""
        usuarios = User.objects.filter(is_active=True).order_by('username')
        
        self.stdout.write('\nUsuários ativos:')
        for user in usuarios:
            tipo = user.get_user_type_display_name()
            empresa = user.empresa_contratante.nome_fantasia if user.empresa_contratante else 'N/A'
            self.stdout.write(f'  - {user.username} ({tipo}) - {empresa}')
