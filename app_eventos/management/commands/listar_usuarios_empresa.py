#!/usr/bin/env python
"""
Comando para listar usuários de empresas contratantes
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from app_eventos.models import EmpresaContratante

User = get_user_model()


class Command(BaseCommand):
    help = 'Lista usuários de empresas contratantes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--empresa-id',
            type=int,
            help='ID da empresa para filtrar usuários'
        )

    def handle(self, *args, **options):
        empresa_id = options.get('empresa_id')

        try:
            # Filtrar usuários
            usuarios = User.objects.filter(
                tipo_usuario__in=['admin_empresa', 'operador_empresa']
            ).select_related('empresa_contratante', 'grupo_permissao')

            if empresa_id:
                usuarios = usuarios.filter(empresa_contratante_id=empresa_id)

            if not usuarios.exists():
                self.stdout.write(
                    self.style.WARNING('Nenhum usuário de empresa encontrado!')
                )
                return

            self.stdout.write(
                self.style.SUCCESS(f'Encontrados {usuarios.count()} usuário(s) de empresa:')
            )
            self.stdout.write('=' * 80)

            for usuario in usuarios:
                self.stdout.write(f'\n👤 {usuario.get_full_name()} ({usuario.username})')
                self.stdout.write(f'   📧 Email: {usuario.email}')
                self.stdout.write(f'   🏢 Empresa: {usuario.empresa_contratante.nome_fantasia}')
                self.stdout.write(f'   👔 Tipo: {usuario.get_tipo_usuario_display()}')
                
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
                
                self.stdout.write(f'   🟢 Ativo: {"Sim" if usuario.is_active else "Não"}')
                self.stdout.write(f'   📅 Último acesso: {usuario.data_ultimo_acesso or "Nunca"}')

            # Resumo por empresa
            self.stdout.write('\n' + '=' * 80)
            self.stdout.write('📊 RESUMO POR EMPRESA:')
            
            empresas = EmpresaContratante.objects.filter(
                usuarios__tipo_usuario__in=['admin_empresa', 'operador_empresa']
            ).distinct()
            
            for empresa in empresas:
                usuarios_empresa = empresa.usuarios.filter(
                    tipo_usuario__in=['admin_empresa', 'operador_empresa']
                )
                self.stdout.write(f'\n🏢 {empresa.nome_fantasia}')
                self.stdout.write(f'   👥 Total de usuários: {usuarios_empresa.count()}')
                self.stdout.write(f'   👑 Administradores: {usuarios_empresa.filter(tipo_usuario="admin_empresa").count()}')
                self.stdout.write(f'   ⚙️ Operadores: {usuarios_empresa.filter(tipo_usuario="operador_empresa").count()}')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro ao listar usuários: {str(e)}')
            )
