# app_eventos/management/commands/popular_grupos_permissoes.py
from django.core.management.base import BaseCommand
from django.db import transaction
from app_eventos.models import (
    PermissaoSistema, 
    GrupoUsuario, 
    EmpresaContratante,
    User
)


class Command(BaseCommand):
    help = 'Popula o sistema com grupos e permissões padrão'

    def add_arguments(self, parser):
        parser.add_argument(
            '--empresa-id',
            type=int,
            help='ID da empresa para criar grupos específicos (opcional)',
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Remove todos os grupos e permissões existentes antes de criar novos',
        )

    def handle(self, *args, **options):
        empresa_id = options.get('empresa_id')
        reset = options.get('reset', False)
        
        with transaction.atomic():
            if reset:
                self.stdout.write('Removendo grupos e permissões existentes...')
                GrupoUsuario.objects.all().delete()
                PermissaoSistema.objects.all().delete()
            
            # Criar permissões do sistema
            self.criar_permissoes()
            
            # Criar grupos do sistema
            self.criar_grupos_sistema()
            
            # Criar grupos para empresa específica se fornecida
            if empresa_id:
                try:
                    empresa = EmpresaContratante.objects.get(id=empresa_id)
                    self.criar_grupos_empresa(empresa)
                    self.stdout.write(
                        self.style.SUCCESS(f'Grupos criados para empresa: {empresa.nome_fantasia}')
                    )
                except EmpresaContratante.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f'Empresa com ID {empresa_id} não encontrada')
                    )
            else:
                # Criar grupos para todas as empresas
                empresas = EmpresaContratante.objects.filter(ativo=True)
                for empresa in empresas:
                    self.criar_grupos_empresa(empresa)
                    self.stdout.write(f'Grupos criados para: {empresa.nome_fantasia}')
        
        self.stdout.write(
            self.style.SUCCESS('Grupos e permissões criados com sucesso!')
        )

    def criar_permissoes(self):
        """Cria as permissões padrão do sistema"""
        permissoes_data = [
            # Módulo: Usuários
            ('gerenciar_usuarios', 'Gerenciar Usuários', 'Criar, editar e excluir usuários', 'usuarios'),
            ('visualizar_usuarios', 'Visualizar Usuários', 'Visualizar lista de usuários', 'usuarios'),
            ('gerenciar_grupos', 'Gerenciar Grupos', 'Criar, editar e excluir grupos de usuários', 'usuarios'),
            
            # Módulo: Eventos
            ('gerenciar_eventos', 'Gerenciar Eventos', 'Criar, editar e excluir eventos', 'eventos'),
            ('visualizar_eventos', 'Visualizar Eventos', 'Visualizar eventos', 'eventos'),
            ('aprovar_eventos', 'Aprovar Eventos', 'Aprovar eventos pendentes', 'eventos'),
            ('cancelar_eventos', 'Cancelar Eventos', 'Cancelar eventos', 'eventos'),
            
            # Módulo: Equipamentos
            ('gerenciar_equipamentos', 'Gerenciar Equipamentos', 'Criar, editar e excluir equipamentos', 'equipamentos'),
            ('visualizar_equipamentos', 'Visualizar Equipamentos', 'Visualizar equipamentos', 'equipamentos'),
            ('alugar_equipamentos', 'Alugar Equipamentos', 'Alugar equipamentos para eventos', 'equipamentos'),
            ('gerenciar_estoque', 'Gerenciar Estoque', 'Gerenciar estoque de equipamentos', 'equipamentos'),
            
            # Módulo: Financeiro
            ('gerenciar_financeiro', 'Gerenciar Financeiro', 'Gerenciar informações financeiras', 'financeiro'),
            ('visualizar_financeiro', 'Visualizar Financeiro', 'Visualizar informações financeiras', 'financeiro'),
            ('aprovar_pagamentos', 'Aprovar Pagamentos', 'Aprovar pagamentos', 'financeiro'),
            ('gerenciar_orcamentos', 'Gerenciar Orçamentos', 'Criar e gerenciar orçamentos', 'financeiro'),
            
            # Módulo: Relatórios
            ('visualizar_relatorios', 'Visualizar Relatórios', 'Visualizar relatórios do sistema', 'relatorios'),
            ('gerar_relatorios', 'Gerar Relatórios', 'Gerar relatórios personalizados', 'relatorios'),
            ('exportar_dados', 'Exportar Dados', 'Exportar dados do sistema', 'relatorios'),
            
            # Módulo: Fornecedores
            ('gerenciar_fornecedores', 'Gerenciar Fornecedores', 'Criar, editar e excluir fornecedores', 'fornecedores'),
            ('visualizar_fornecedores', 'Visualizar Fornecedores', 'Visualizar fornecedores', 'fornecedores'),
            ('avaliar_fornecedores', 'Avaliar Fornecedores', 'Avaliar fornecedores', 'fornecedores'),
            
            # Módulo: Freelancers
            ('gerenciar_freelancers', 'Gerenciar Freelancers', 'Gerenciar freelancers', 'freelancers'),
            ('visualizar_freelancers', 'Visualizar Freelancers', 'Visualizar freelancers', 'freelancers'),
            ('contratar_freelancers', 'Contratar Freelancers', 'Contratar freelancers para eventos', 'freelancers'),
            ('avaliar_freelancers', 'Avaliar Freelancers', 'Avaliar freelancers', 'freelancers'),
            
            # Módulo: Sistema
            ('gerenciar_sistema', 'Gerenciar Sistema', 'Configurações gerais do sistema', 'sistema'),
            ('visualizar_logs', 'Visualizar Logs', 'Visualizar logs do sistema', 'sistema'),
            ('gerenciar_backups', 'Gerenciar Backups', 'Gerenciar backups do sistema', 'sistema'),
        ]
        
        for codigo, nome, descricao, modulo in permissoes_data:
            permissao, created = PermissaoSistema.objects.get_or_create(
                codigo=codigo,
                defaults={
                    'nome': nome,
                    'descricao': descricao,
                    'modulo': modulo,
                    'ativo': True
                }
            )
            if created:
                self.stdout.write(f'Permissão criada: {nome}')

    def criar_grupos_sistema(self):
        """Cria os grupos padrão do sistema"""
        # Grupo Administrador do Sistema
        grupo_admin, created = GrupoUsuario.objects.get_or_create(
            nome='Administrador do Sistema',
            defaults={
                'descricao': 'Grupo com todas as permissões do sistema',
                'tipo_grupo': 'sistema',
                'empresa_contratante': None,
                'ativo': True
            }
        )
        
        if created:
            # Adicionar todas as permissões
            todas_permissoes = PermissaoSistema.objects.filter(ativo=True)
            grupo_admin.permissoes.set(todas_permissoes)
            self.stdout.write('Grupo "Administrador do Sistema" criado com todas as permissões')
        
        # Grupo Freelancers Global (sem empresa específica)
        grupo_freelancers_global, created = GrupoUsuario.objects.get_or_create(
            nome='Freelancers Global',
            empresa_contratante=None,
            defaults={
                'descricao': 'Grupo global para freelancers - podem ver vagas de todas as empresas',
                'tipo_grupo': 'sistema',
                'ativo': True
            }
        )
        
        if created:
            # Adicionar permissões específicas para freelancers
            permissoes_freelancers = PermissaoSistema.objects.filter(
                codigo__in=[
                    'visualizar_eventos',
                    'visualizar_equipamentos', 
                    'visualizar_freelancers',
                    'visualizar_fornecedores'
                ],
                ativo=True
            )
            grupo_freelancers_global.permissoes.set(permissoes_freelancers)
            self.stdout.write('Grupo "Freelancers Global" criado com permissões específicas')

    def criar_grupos_empresa(self, empresa):
        """Cria os grupos padrão para uma empresa"""
        # Buscar permissões por módulo
        permissoes_usuarios = PermissaoSistema.objects.filter(modulo='usuarios', ativo=True)
        permissoes_eventos = PermissaoSistema.objects.filter(modulo='eventos', ativo=True)
        permissoes_equipamentos = PermissaoSistema.objects.filter(modulo='equipamentos', ativo=True)
        permissoes_financeiro = PermissaoSistema.objects.filter(modulo='financeiro', ativo=True)
        permissoes_relatorios = PermissaoSistema.objects.filter(modulo='relatorios', ativo=True)
        permissoes_fornecedores = PermissaoSistema.objects.filter(modulo='fornecedores', ativo=True)
        permissoes_freelancers = PermissaoSistema.objects.filter(modulo='freelancers', ativo=True)
        
        # Grupo Administrador da Empresa
        grupo_admin_empresa, created = GrupoUsuario.objects.get_or_create(
            nome='Administrador da Empresa',
            empresa_contratante=empresa,
            defaults={
                'descricao': 'Administrador com todas as permissões da empresa',
                'tipo_grupo': 'empresa',
                'ativo': True
            }
        )
        
        if created:
            # Adicionar todas as permissões exceto sistema
            todas_permissoes_empresa = PermissaoSistema.objects.exclude(modulo='sistema').filter(ativo=True)
            grupo_admin_empresa.permissoes.set(todas_permissoes_empresa)
            self.stdout.write(f'Grupo "Administrador da Empresa" criado para {empresa.nome_fantasia}')
        
        # Grupo Operador da Empresa
        grupo_operador, created = GrupoUsuario.objects.get_or_create(
            nome='Operador da Empresa',
            empresa_contratante=empresa,
            defaults={
                'descricao': 'Operador com permissões limitadas para operação diária',
                'tipo_grupo': 'empresa',
                'ativo': True
            }
        )
        
        if created:
            # Adicionar permissões básicas
            permissoes_operador = (
                permissoes_eventos.filter(codigo__in=['visualizar_eventos', 'gerenciar_eventos']) |
                permissoes_equipamentos.filter(codigo__in=['visualizar_equipamentos', 'alugar_equipamentos']) |
                permissoes_financeiro.filter(codigo__in=['visualizar_financeiro']) |
                permissoes_relatorios.filter(codigo__in=['visualizar_relatorios']) |
                permissoes_fornecedores.filter(codigo__in=['visualizar_fornecedores']) |
                permissoes_freelancers.filter(codigo__in=['visualizar_freelancers'])
            )
            grupo_operador.permissoes.set(permissoes_operador)
            self.stdout.write(f'Grupo "Operador da Empresa" criado para {empresa.nome_fantasia}')
        
        # Grupo Visualizador
        grupo_visualizador, created = GrupoUsuario.objects.get_or_create(
            nome='Visualizador',
            empresa_contratante=empresa,
            defaults={
                'descricao': 'Usuário com permissões apenas de visualização',
                'tipo_grupo': 'empresa',
                'ativo': True
            }
        )
        
        if created:
            # Adicionar apenas permissões de visualização
            permissoes_visualizacao = PermissaoSistema.objects.filter(
                codigo__startswith='visualizar_',
                ativo=True
            ).exclude(modulo='sistema')
            grupo_visualizador.permissoes.set(permissoes_visualizacao)
            self.stdout.write(f'Grupo "Visualizador" criado para {empresa.nome_fantasia}')
        
        # Grupo Financeiro
        grupo_financeiro, created = GrupoUsuario.objects.get_or_create(
            nome='Financeiro',
            empresa_contratante=empresa,
            defaults={
                'descricao': 'Usuário com permissões financeiras',
                'tipo_grupo': 'empresa',
                'ativo': True
            }
        )
        
        if created:
            # Adicionar permissões financeiras
            permissoes_financeiro_grupo = (
                permissoes_financeiro |
                permissoes_relatorios.filter(codigo__in=['visualizar_relatorios', 'gerar_relatorios']) |
                permissoes_eventos.filter(codigo__in=['visualizar_eventos'])
            )
            grupo_financeiro.permissoes.set(permissoes_financeiro_grupo)
            self.stdout.write(f'Grupo "Financeiro" criado para {empresa.nome_fantasia}')
        
        # Nota: Grupo de freelancers foi movido para o sistema global
        # Freelancers não são vinculados a empresas específicas
