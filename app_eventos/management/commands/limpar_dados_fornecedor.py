from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Limpa dados antigos de fornecedores para permitir migração'

    def handle(self, *args, **options):
        self.stdout.write('Limpando dados antigos de fornecedores...')
        
        with connection.cursor() as cursor:
            # Verificar se a tabela existe e tem dados
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'app_eventos_despesaevento' 
                AND column_name = 'fornecedor'
            """)
            
            result = cursor.fetchone()
            if result:
                column_name, data_type = result
                self.stdout.write(f'Coluna fornecedor encontrada com tipo: {data_type}')
                
                if data_type == 'character varying':
                    # Limpar dados de texto antigos
                    cursor.execute("""
                        UPDATE app_eventos_despesaevento 
                        SET fornecedor = NULL 
                        WHERE fornecedor IS NOT NULL
                    """)
                    self.stdout.write(self.style.SUCCESS('Dados de fornecedores limpos com sucesso!'))
                else:
                    self.stdout.write('Coluna já foi convertida para ForeignKey')
            else:
                self.stdout.write('Coluna fornecedor não encontrada')
        
        self.stdout.write(self.style.SUCCESS('Processo concluído!'))
