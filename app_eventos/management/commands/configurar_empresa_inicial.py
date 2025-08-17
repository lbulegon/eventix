from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from app_eventos.models import EmpresaContratante, TipoEmpresa
from datetime import date, timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Configura a empresa inicial do sistema Eventix'

    def add_arguments(self, parser):
        parser.add_argument(
            '--nome',
            type=str,
            default='Eventix',
            help='Nome da empresa contratante'
        )
        parser.add_argument(
            '--cnpj',
            type=str,
            default='00.000.000/0001-00',
            help='CNPJ da empresa contratante'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@eventix.com',
            help='Email da empresa contratante'
        )
        parser.add_argument(
            '--admin-username',
            type=str,
            default='admin',
            help='Username do administrador do sistema'
        )
        parser.add_argument(
            '--admin-email',
            type=str,
            default='admin@eventix.com',
            help='Email do administrador do sistema'
        )
        parser.add_argument(
            '--admin-password',
            type=str,
            default='admin123',
            help='Senha do administrador do sistema'
        )

    def handle(self, *args, **options):
        self.stdout.write('Configurando empresa inicial do sistema...')
        
        # Criar empresa contratante
        empresa_contratante, created = EmpresaContratante.objects.get_or_create(
            cnpj=options['cnpj'],
            defaults={
                'nome': options['nome'],
                'razao_social': f'{options["nome"]} LTDA',
                'nome_fantasia': options['nome'],
                'email': options['email'],
                'data_vencimento': date.today() + timedelta(days=365),
                'plano_contratado': 'Premium',
                'valor_mensal': 999.99,
                'ativo': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Empresa "{empresa_contratante.nome_fantasia}" criada com sucesso!')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Empresa "{empresa_contratante.nome_fantasia}" já existe.')
            )
        
        # Criar tipos de empresa padrão
        tipos_empresa = [
            {'nome': 'Produtora', 'descricao': 'Empresas produtoras de eventos'},
            {'nome': 'Contratante de Mão de Obra', 'descricao': 'Empresas que contratam freelancers'},
            {'nome': 'Proprietária de Local', 'descricao': 'Empresas proprietárias de locais de eventos'},
            {'nome': 'Fornecedora', 'descricao': 'Empresas fornecedoras de serviços e equipamentos'},
        ]
        
        for tipo_data in tipos_empresa:
            tipo, created = TipoEmpresa.objects.get_or_create(
                nome=tipo_data['nome'],
                defaults={'descricao': tipo_data['descricao']}
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Tipo de empresa "{tipo.nome}" criado com sucesso!')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Tipo de empresa "{tipo.nome}" já existe.')
                )
        
        # Criar administrador do sistema
        admin_user, created = User.objects.get_or_create(
            username=options['admin_username'],
            defaults={
                'email': options['admin_email'],
                'tipo_usuario': 'admin_sistema',
                'is_staff': True,
                'is_superuser': True,
                'ativo': True
            }
        )
        
        if created:
            admin_user.set_password(options['admin_password'])
            admin_user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Administrador do sistema "{admin_user.username}" criado com sucesso!')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Administrador do sistema "{admin_user.username}" já existe.')
            )
        
        self.stdout.write(
            self.style.SUCCESS('Configuração inicial concluída com sucesso!')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Login: {options["admin_username"]}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Senha: {options["admin_password"]}')
        )
