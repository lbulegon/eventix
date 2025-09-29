"""
Comando para zerar dados do modelo Funcao
"""
from django.core.management.base import BaseCommand
from app_eventos.models import Funcao, TipoFuncao


class Command(BaseCommand):
    help = 'Zera todos os dados do modelo Funcao e TipoFuncao'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirma a operação de limpeza',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING('ATENÇÃO: Este comando irá deletar TODOS os dados de Funcao e TipoFuncao!')
            )
            self.stdout.write('Use --confirm para confirmar a operação.')
            return

        # Contar registros antes da limpeza
        funcoes_count = Funcao.objects.count()
        tipos_count = TipoFuncao.objects.count()
        
        self.stdout.write(f'Encontrados {funcoes_count} funções e {tipos_count} tipos de função.')
        
        # Deletar todas as funções
        if funcoes_count > 0:
            Funcao.objects.all().delete()
            self.stdout.write(f'✓ {funcoes_count} funções deletadas.')
        
        # Deletar todos os tipos de função
        if tipos_count > 0:
            TipoFuncao.objects.all().delete()
            self.stdout.write(f'✓ {tipos_count} tipos de função deletados.')
        
        self.stdout.write(
            self.style.SUCCESS('✓ Dados do modelo Funcao zerados com sucesso!')
        )
