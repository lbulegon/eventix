"""
Comando para criar grupos de permissão para a empresa
"""
from django.core.management.base import BaseCommand
from app_eventos.models import EmpresaContratante, GrupoPermissaoEmpresa


class Command(BaseCommand):
    help = 'Cria grupos de permissão para a empresa'

    def add_arguments(self, parser):
        parser.add_argument(
            '--empresa-id',
            type=int,
            help='ID da empresa contratante'
        )

    def handle(self, *args, **options):
        empresa_id = options.get('empresa_id')
        
        try:
            # Buscar empresa
            if empresa_id:
                empresa = EmpresaContratante.objects.get(id=empresa_id)
            else:
                empresa = EmpresaContratante.objects.filter(ativo=True).first()
            
            if not empresa:
                self.stdout.write('Nenhuma empresa contratante encontrada!')
                return
            
            # Grupos de permissão padrão
            grupos_data = [
                {
                    'nome': 'Administradores',
                    'descricao': 'Acesso total à empresa',
                    'pode_gerenciar_usuarios': True,
                    'pode_gerenciar_eventos': True,
                    'pode_gerenciar_freelancers': True,
                    'pode_gerenciar_equipamentos': True,
                    'pode_gerenciar_estoque': True,
                    'pode_gerenciar_financeiro': True,
                    'pode_gerenciar_relatorios': True,
                    'pode_configurar_sistema': True,
                    'pode_ver_todos_eventos': True,
                    'pode_editar_todos_eventos': True,
                },
                {
                    'nome': 'Operadores',
                    'descricao': 'Operadores da empresa',
                    'pode_gerenciar_usuarios': False,
                    'pode_gerenciar_eventos': True,
                    'pode_gerenciar_freelancers': True,
                    'pode_gerenciar_equipamentos': True,
                    'pode_gerenciar_estoque': True,
                    'pode_gerenciar_financeiro': False,
                    'pode_gerenciar_relatorios': True,
                    'pode_configurar_sistema': False,
                    'pode_ver_todos_eventos': True,
                    'pode_editar_todos_eventos': True,
                },
                {
                    'nome': 'Visualizadores',
                    'descricao': 'Apenas visualização',
                    'pode_gerenciar_usuarios': False,
                    'pode_gerenciar_eventos': False,
                    'pode_gerenciar_freelancers': False,
                    'pode_gerenciar_equipamentos': False,
                    'pode_gerenciar_estoque': False,
                    'pode_gerenciar_financeiro': False,
                    'pode_gerenciar_relatorios': True,
                    'pode_configurar_sistema': False,
                    'pode_ver_todos_eventos': True,
                    'pode_editar_todos_eventos': False,
                },
                {
                    'nome': 'Financeiro',
                    'descricao': 'Acesso ao financeiro',
                    'pode_gerenciar_usuarios': False,
                    'pode_gerenciar_eventos': False,
                    'pode_gerenciar_freelancers': False,
                    'pode_gerenciar_equipamentos': False,
                    'pode_gerenciar_estoque': False,
                    'pode_gerenciar_financeiro': True,
                    'pode_gerenciar_relatorios': True,
                    'pode_configurar_sistema': False,
                    'pode_ver_todos_eventos': True,
                    'pode_editar_todos_eventos': False,
                }
            ]
            
            for grupo_data in grupos_data:
                grupo, created = GrupoPermissaoEmpresa.objects.get_or_create(
                    empresa_contratante=empresa,
                    nome=grupo_data['nome'],
                    defaults=grupo_data
                )
                
                if created:
                    self.stdout.write(f'[OK] Grupo criado: {grupo.nome}')
                else:
                    self.stdout.write(f'[INFO] Grupo ja existe: {grupo.nome}')
            
            self.stdout.write(f'Grupos de permissao criados para: {empresa.nome_fantasia}')
            
        except EmpresaContratante.DoesNotExist:
            self.stdout.write('Empresa contratante nao encontrada!')
        except Exception as e:
            self.stdout.write(f'Erro ao criar grupos: {str(e)}')
