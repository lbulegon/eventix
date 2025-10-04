#!/usr/bin/env python
"""
Comando para criar usuário administrador de empresa contratante
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from app_eventos.models import EmpresaContratante, GrupoPermissaoEmpresa

User = get_user_model()


class Command(BaseCommand):
    help = 'Cria usuário administrador para empresa contratante'

    def add_arguments(self, parser):
        parser.add_argument(
            '--empresa-id',
            type=int,
            help='ID da empresa contratante (opcional, será criada se não existir)'
        )
        parser.add_argument(
            '--username',
            type=str,
            default='admin_empresa',
            help='Username do usuário (padrão: admin_empresa)'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@empresa.com',
            help='Email do usuário (padrão: admin@empresa.com)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin123',
            help='Senha do usuário (padrão: admin123)'
        )
        parser.add_argument(
            '--nome-empresa',
            type=str,
            default='Empresa Admin',
            help='Nome da empresa (se for criar nova)'
        )

    def handle(self, *args, **options):
        empresa_id = options.get('empresa_id')
        username = options.get('username')
        email = options.get('email')
        password = options.get('password')
        nome_empresa = options.get('nome_empresa')

        try:
            # Verificar se usuário já existe
            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.WARNING(f'Usuário {username} já existe!')
                )
                return

            # Obter ou criar empresa contratante
            if empresa_id:
                try:
                    empresa = EmpresaContratante.objects.get(id=empresa_id)
                    self.stdout.write(f'Usando empresa existente: {empresa.nome_fantasia}')
                except EmpresaContratante.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f'Empresa com ID {empresa_id} não encontrada!')
                    )
                    return
            else:
                # Criar nova empresa
                empresa = EmpresaContratante.objects.create(
                    nome=nome_empresa,
                    nome_fantasia=nome_empresa,
                    razao_social=f"{nome_empresa} Ltda",
                    cnpj="98.765.432/0001-10",
                    email="admin@empresa.com",
                    telefone="(11) 88888-8888",
                    data_vencimento="2025-12-31",
                    valor_mensal=2000.00,
                    ativo=True
                )
                self.stdout.write(f'Empresa criada: {empresa.nome_fantasia}')

            # Criar grupo de permissões para administrador
            grupo_admin, created = GrupoPermissaoEmpresa.objects.get_or_create(
                empresa_contratante=empresa,
                nome='Administrador',
                defaults={
                    'descricao': 'Grupo com todas as permissões administrativas',
                    'pode_gerenciar_usuarios': True,
                    'pode_gerenciar_eventos': True,
                    'pode_gerenciar_freelancers': True,
                    'pode_gerenciar_equipamentos': True,
                    'pode_gerenciar_estoque': True,
                    'pode_gerenciar_financeiro': True,
                    'pode_gerenciar_relatorios': True,
                    'ativo': True
                }
            )

            if created:
                self.stdout.write(f'Grupo de permissões criado: {grupo_admin.nome}')

            # Criar usuário administrador
            usuario = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                tipo_usuario='admin_empresa',
                empresa_contratante=empresa,
                grupo_permissao=grupo_admin,
                is_staff=True,
                is_superuser=True,
                is_active=True,
                first_name='Administrador',
                last_name='da Empresa'
            )

            self.stdout.write(
                self.style.SUCCESS('Usuário administrador criado com sucesso!')
            )
            self.stdout.write(f'Username: {username}')
            self.stdout.write(f'Email: {email}')
            self.stdout.write(f'Senha: {password}')
            self.stdout.write(f'Empresa: {empresa.nome_fantasia}')
            self.stdout.write(f'Tipo: {usuario.get_tipo_usuario_display()}')
            self.stdout.write(f'Grupo: {grupo_admin.nome}')
            
            # Mostrar permissões do grupo
            self.stdout.write('\nPermissões do usuário:')
            permissoes = [
                ('Gerenciar Usuários', grupo_admin.pode_gerenciar_usuarios),
                ('Gerenciar Eventos', grupo_admin.pode_gerenciar_eventos),
                ('Gerenciar Freelancers', grupo_admin.pode_gerenciar_freelancers),
                ('Gerenciar Equipamentos', grupo_admin.pode_gerenciar_equipamentos),
                ('Gerenciar Estoque', grupo_admin.pode_gerenciar_estoque),
                ('Gerenciar Financeiro', grupo_admin.pode_gerenciar_financeiro),
                ('Gerar Relatórios', grupo_admin.pode_gerenciar_relatorios),
            ]
            
            for permissao, tem_permissao in permissoes:
                status = '✓' if tem_permissao else '✗'
                self.stdout.write(f'  {status} {permissao}')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro ao criar usuário: {str(e)}')
            )
