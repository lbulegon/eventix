#!/usr/bin/env python
"""
Comando para Admin da Empresa criar usuários operadores
Este comando deve ser executado por um Admin da Empresa
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from app_eventos.models import GrupoPermissaoEmpresa

User = get_user_model()


class Command(BaseCommand):
    help = 'Admin da Empresa cria usuário operador para sua empresa'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            required=True,
            help='Username do usuário operador'
        )
        parser.add_argument(
            '--email',
            type=str,
            required=True,
            help='Email do usuário operador'
        )
        parser.add_argument(
            '--password',
            type=str,
            required=True,
            help='Senha do usuário operador'
        )
        parser.add_argument(
            '--nome',
            type=str,
            required=True,
            help='Nome completo do usuário'
        )
        parser.add_argument(
            '--admin-username',
            type=str,
            required=True,
            help='Username do admin da empresa que está criando o usuário'
        )
        parser.add_argument(
            '--permissoes',
            type=str,
            nargs='+',
            default=['eventos', 'freelancers', 'equipamentos', 'estoque', 'relatorios'],
            help='Permissões específicas (eventos, freelancers, equipamentos, estoque, financeiro, relatorios)'
        )

    def handle(self, *args, **options):
        username = options.get('username')
        email = options.get('email')
        password = options.get('password')
        nome = options.get('nome')
        admin_username = options.get('admin_username')
        permissoes = options.get('permissoes')

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

            # Verificar se usuário operador já existe
            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.WARNING(f'Usuário {username} já existe!')
                )
                return

            empresa = admin_user.empresa_contratante

            # Criar grupo de permissões personalizado
            grupo_operador, created = GrupoPermissaoEmpresa.objects.get_or_create(
                empresa_contratante=empresa,
                nome=f'Operador - {username}',
                defaults={
                    'descricao': f'Grupo personalizado para {username}',
                    'pode_gerenciar_usuarios': False,
                    'pode_gerenciar_eventos': 'eventos' in permissoes,
                    'pode_gerenciar_freelancers': 'freelancers' in permissoes,
                    'pode_gerenciar_equipamentos': 'equipamentos' in permissoes,
                    'pode_gerenciar_estoque': 'estoque' in permissoes,
                    'pode_gerenciar_financeiro': 'financeiro' in permissoes,
                    'pode_gerenciar_relatorios': 'relatorios' in permissoes,
                    'ativo': True
                }
            )

            if created:
                self.stdout.write(f'Grupo de permissões criado: {grupo_operador.nome}')

            # Criar usuário operador
            usuario = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                tipo_usuario='operador_empresa',
                empresa_contratante=empresa,
                grupo_permissao=grupo_operador,
                is_staff=True,
                is_active=True,
                first_name=nome.split()[0] if nome.split() else nome,
                last_name=' '.join(nome.split()[1:]) if len(nome.split()) > 1 else ''
            )

            self.stdout.write(
                self.style.SUCCESS('Usuário operador criado com sucesso!')
            )
            self.stdout.write(f'Username: {username}')
            self.stdout.write(f'Email: {email}')
            self.stdout.write(f'Nome: {nome}')
            self.stdout.write(f'Empresa: {empresa.nome_fantasia}')
            self.stdout.write(f'Tipo: {usuario.get_tipo_usuario_display()}')
            self.stdout.write(f'Grupo: {grupo_operador.nome}')
            self.stdout.write(f'Criado por: {admin_username}')
            
            # Mostrar permissões do grupo
            self.stdout.write('\nPermissões do usuário:')
            permissoes_dict = {
                'Gerenciar Usuários': grupo_operador.pode_gerenciar_usuarios,
                'Gerenciar Eventos': grupo_operador.pode_gerenciar_eventos,
                'Gerenciar Freelancers': grupo_operador.pode_gerenciar_freelancers,
                'Gerenciar Equipamentos': grupo_operador.pode_gerenciar_equipamentos,
                'Gerenciar Estoque': grupo_operador.pode_gerenciar_estoque,
                'Gerenciar Financeiro': grupo_operador.pode_gerenciar_financeiro,
                'Gerar Relatórios': grupo_operador.pode_gerenciar_relatorios,
            }
            
            for permissao, tem_permissao in permissoes_dict.items():
                status = '✓' if tem_permissao else '✗'
                self.stdout.write(f'  {status} {permissao}')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro ao criar usuário: {str(e)}')
            )
