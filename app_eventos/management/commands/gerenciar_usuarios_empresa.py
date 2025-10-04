#!/usr/bin/env python
"""
Comando para Admin da Empresa gerenciar usuários da sua empresa
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from app_eventos.models import GrupoPermissaoEmpresa

User = get_user_model()


class Command(BaseCommand):
    help = 'Admin da Empresa gerencia usuários da sua empresa'

    def add_arguments(self, parser):
        parser.add_argument(
            '--admin-username',
            type=str,
            required=True,
            help='Username do admin da empresa'
        )
        parser.add_argument(
            '--acao',
            type=str,
            choices=['listar', 'ativar', 'desativar', 'alterar-senha'],
            default='listar',
            help='Ação a ser executada'
        )
        parser.add_argument(
            '--username',
            type=str,
            help='Username do usuário para ações específicas'
        )
        parser.add_argument(
            '--nova-senha',
            type=str,
            help='Nova senha (para alterar-senha)'
        )

    def handle(self, *args, **options):
        admin_username = options.get('admin_username')
        acao = options.get('acao')
        username = options.get('username')
        nova_senha = options.get('nova_senha')

        try:
            # Verificar se o admin da empresa existe e é válido
            try:
                admin_user = User.objects.get(username=admin_username)
                if admin_user.tipo_usuario != 'admin_empresa':
                    self.stdout.write(
                        self.style.ERROR(f'Usuário {admin_username} não é um Admin da Empresa!')
                    )
                    return
                
                if not admin_user.empresa_contratante:
                    self.stdout.write(
                        self.style.ERROR(f'Admin {admin_username} não está associado a nenhuma empresa!')
                    )
                    return
                    
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Admin {admin_username} não encontrado!')
                )
                return

            empresa = admin_user.empresa_contratante

            if acao == 'listar':
                self._listar_usuarios(empresa)
            elif acao == 'ativar':
                self._ativar_usuario(username, empresa)
            elif acao == 'desativar':
                self._desativar_usuario(username, empresa)
            elif acao == 'alterar-senha':
                self._alterar_senha(username, nova_senha, empresa)

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro: {str(e)}')
            )

    def _listar_usuarios(self, empresa):
        """Lista todos os usuários da empresa"""
        usuarios = User.objects.filter(
            empresa_contratante=empresa
        ).select_related('grupo_permissao')

        if not usuarios.exists():
            self.stdout.write(
                self.style.WARNING('Nenhum usuário encontrado nesta empresa!')
            )
            return

        self.stdout.write(
            self.style.SUCCESS(f'Usuários da empresa {empresa.nome_fantasia}:')
        )
        self.stdout.write('=' * 80)

        for usuario in usuarios:
            self.stdout.write(f'\n👤 {usuario.get_full_name()} ({usuario.username})')
            self.stdout.write(f'   📧 Email: {usuario.email}')
            self.stdout.write(f'   👔 Tipo: {usuario.get_tipo_usuario_display()}')
            self.stdout.write(f'   🟢 Status: {"Ativo" if usuario.is_active else "Inativo"}')
            
            if usuario.grupo_permissao:
                self.stdout.write(f'   🔐 Grupo: {usuario.grupo_permissao.nome}')
                
                # Mostrar permissões
                permissoes = [
                    ('Gerenciar Usuários', usuario.grupo_permissao.pode_gerenciar_usuarios),
                    ('Gerenciar Eventos', usuario.grupo_permissao.pode_gerenciar_eventos),
                    ('Gerenciar Freelancers', usuario.grupo_permissao.pode_gerenciar_freelancers),
                    ('Gerenciar Equipamentos', usuario.grupo_permissao.pode_gerenciar_equipamentos),
                    ('Gerenciar Estoque', usuario.grupo_permissao.pode_gerenciar_estoque),
                    ('Gerenciar Financeiro', usuario.grupo_permissao.pode_gerenciar_financeiro),
                    ('Gerar Relatórios', usuario.grupo_permissao.pode_gerenciar_relatorios),
                ]
                
                self.stdout.write('   📋 Permissões:')
                for permissao, tem_permissao in permissoes:
                    status = '✓' if tem_permissao else '✗'
                    self.stdout.write(f'      {status} {permissao}')

    def _ativar_usuario(self, username, empresa):
        """Ativa um usuário da empresa"""
        if not username:
            self.stdout.write(self.style.ERROR('Username é obrigatório para ativar usuário!'))
            return

        try:
            usuario = User.objects.get(username=username, empresa_contratante=empresa)
            usuario.is_active = True
            usuario.save()
            self.stdout.write(
                self.style.SUCCESS(f'Usuário {username} ativado com sucesso!')
            )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Usuário {username} não encontrado nesta empresa!')
            )

    def _desativar_usuario(self, username, empresa):
        """Desativa um usuário da empresa"""
        if not username:
            self.stdout.write(self.style.ERROR('Username é obrigatório para desativar usuário!'))
            return

        try:
            usuario = User.objects.get(username=username, empresa_contratante=empresa)
            usuario.is_active = False
            usuario.save()
            self.stdout.write(
                self.style.SUCCESS(f'Usuário {username} desativado com sucesso!')
            )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Usuário {username} não encontrado nesta empresa!')
            )

    def _alterar_senha(self, username, nova_senha, empresa):
        """Altera a senha de um usuário da empresa"""
        if not username or not nova_senha:
            self.stdout.write(self.style.ERROR('Username e nova-senha são obrigatórios!'))
            return

        try:
            usuario = User.objects.get(username=username, empresa_contratante=empresa)
            usuario.set_password(nova_senha)
            usuario.save()
            self.stdout.write(
                self.style.SUCCESS(f'Senha do usuário {username} alterada com sucesso!')
            )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Usuário {username} não encontrado nesta empresa!')
            )
