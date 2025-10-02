"""
Comando para verificar se há problemas similares em outros modelos
"""
from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import models
import inspect


class Command(BaseCommand):
    help = 'Verifica se há problemas similares em outros modelos com campos nullable'

    def handle(self, *args, **options):
        self.stdout.write('🔍 Verificando modelos com possíveis problemas...')
        
        problemas_encontrados = []
        
        # Busca todos os modelos da aplicação
        for model in apps.get_models():
            if model._meta.app_label == 'app_eventos':
                # Verifica se o modelo tem método __str__
                if hasattr(model, '__str__'):
                    # Obtém o código fonte do método __str__
                    try:
                        source = inspect.getsource(model.__str__)
                        
                        # Verifica se há acesso direto a campos ForeignKey sem verificação de null
                        if 'empresa_contratante.' in source and 'if' not in source:
                            # Verifica se o campo empresa_contratante é nullable
                            for field in model._meta.fields:
                                if field.name == 'empresa_contratante' and field.null:
                                    problemas_encontrados.append({
                                        'modelo': model.__name__,
                                        'campo': 'empresa_contratante',
                                        'problema': 'Acesso direto sem verificação de null',
                                        'linha': source
                                    })
                                    break
                        
                        # Verifica outros padrões similares
                        for field in model._meta.fields:
                            if isinstance(field, models.ForeignKey) and field.null:
                                field_name = field.name
                                if f'{field_name}.' in source and f'if {field_name}' not in source:
                                    problemas_encontrados.append({
                                        'modelo': model.__name__,
                                        'campo': field_name,
                                        'problema': 'Acesso direto a ForeignKey nullable sem verificação',
                                        'linha': source
                                    })
                    
                    except Exception as e:
                        self.stdout.write(f'⚠️ Erro ao verificar {model.__name__}: {str(e)}')
        
        if problemas_encontrados:
            self.stdout.write('\n❌ PROBLEMAS ENCONTRADOS:')
            self.stdout.write('=' * 50)
            
            for problema in problemas_encontrados:
                self.stdout.write(f'\n🔴 Modelo: {problema["modelo"]}')
                self.stdout.write(f'   Campo: {problema["campo"]}')
                self.stdout.write(f'   Problema: {problema["problema"]}')
                self.stdout.write(f'   Código: {problema["linha"].strip()}')
        else:
            self.stdout.write('\n✅ Nenhum problema encontrado!')
        
        # Verifica especificamente o modelo Funcao
        self.stdout.write('\n🔍 Verificando modelo Funcao especificamente...')
        try:
            from app_eventos.models import Funcao
            
            # Testa criar uma instância sem empresa_contratante
            funcao = Funcao()
            funcao.nome = "Teste"
            funcao.empresa_contratante = None
            
            # Testa o método __str__
            resultado = str(funcao)
            self.stdout.write(f'✅ Método __str__ do modelo Funcao funciona: "{resultado}"')
            
        except Exception as e:
            self.stdout.write(f'❌ Erro ao testar modelo Funcao: {str(e)}')
        
        self.stdout.write('\n✅ Verificação concluída!')
