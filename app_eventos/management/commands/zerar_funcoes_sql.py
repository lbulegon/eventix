"""
Comando para zerar dados do modelo Funcao usando SQL direto
"""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Zera todos os dados do modelo Funcao e TipoFuncao usando SQL direto'

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

        with connection.cursor() as cursor:
            # Contar registros antes da limpeza
            cursor.execute("SELECT COUNT(*) FROM app_eventos_funcao")
            funcoes_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM app_eventos_tipofuncao")
            tipos_count = cursor.fetchone()[0]
            
            self.stdout.write(f'Encontrados {funcoes_count} funções e {tipos_count} tipos de função.')
            
            # Deletar todas as funções
            if funcoes_count > 0:
                cursor.execute("DELETE FROM app_eventos_funcao")
                self.stdout.write(f'✓ {funcoes_count} funções deletadas.')
            
            # Deletar todos os tipos de função
            if tipos_count > 0:
                cursor.execute("DELETE FROM app_eventos_tipofuncao")
                self.stdout.write(f'✓ {tipos_count} tipos de função deletados.')
        
        self.stdout.write(
            self.style.SUCCESS('✓ Dados do modelo Funcao zerados com sucesso!')
        )
