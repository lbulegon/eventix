"""
Comando para criar empresa contratante
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from app_eventos.models import EmpresaContratante, PlanoContratacao


class Command(BaseCommand):
    help = 'Cria empresa contratante'

    def add_arguments(self, parser):
        parser.add_argument(
            '--nome',
            type=str,
            default='Empresa Demo',
            help='Nome da empresa'
        )
        parser.add_argument(
            '--cnpj',
            type=str,
            default='12.345.678/0001-90',
            help='CNPJ da empresa'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='contato@empresademo.com',
            help='Email da empresa'
        )

    def handle(self, *args, **options):
        nome = options['nome']
        cnpj = options['cnpj']
        email = options['email']
        
        try:
            # Verificar se já existe
            if EmpresaContratante.objects.filter(cnpj=cnpj).exists():
                self.stdout.write('Empresa com este CNPJ ja existe!')
                return
            
            # Buscar um plano disponível
            plano = PlanoContratacao.objects.filter(ativo=True).first()
            if not plano:
                self.stdout.write('Nenhum plano de contratacao encontrado!')
                return
            
            # Data de vencimento (1 ano a partir de hoje)
            data_vencimento = timezone.now().date() + timedelta(days=365)
            
            # Criar empresa contratante
            empresa = EmpresaContratante.objects.create(
                nome=nome,
                cnpj=cnpj,
                razao_social=f'{nome} Ltda',
                nome_fantasia=nome,
                telefone='(11) 99999-9999',
                email=email,
                website='https://www.empresademo.com',
                cep='01234-567',
                logradouro='Rua das Flores',
                numero='123',
                complemento='Sala 1',
                bairro='Centro',
                cidade='São Paulo',
                uf='SP',
                data_vencimento=data_vencimento,
                plano_contratado=plano,
                valor_mensal=plano.valor_mensal,
                ativo=True
            )
            
            self.stdout.write('Empresa contratante criada com sucesso!')
            self.stdout.write(f'Nome: {empresa.nome}')
            self.stdout.write(f'CNPJ: {empresa.cnpj}')
            self.stdout.write(f'Email: {empresa.email}')
            self.stdout.write(f'Plano: {empresa.plano_contratado.nome}')
            self.stdout.write(f'Valor Mensal: R$ {empresa.valor_mensal}')
            self.stdout.write(f'Vencimento: {empresa.data_vencimento}')
            self.stdout.write(f'Ativa: {empresa.ativo}')
            
        except Exception as e:
            self.stdout.write(f'Erro ao criar empresa: {str(e)}')
