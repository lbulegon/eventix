from django.core.management.base import BaseCommand
from app_eventos.models import DespesaEvento, Fornecedor


class Command(BaseCommand):
    help = 'Atualiza dados financeiros para usar os fornecedores criados'

    def handle(self, *args, **options):
        self.stdout.write('Atualizando dados financeiros com fornecedores...')
        
        # Mapeamento de fornecedores antigos para novos
        mapeamento_fornecedores = {
            'Sound Pro Ltda': 'Sound Pro Ltda',
            'Decorações Eventos': 'Decorações Eventos',
            'Segurança Total': 'Segurança Total',
            'Agência Digital': 'Agência Digital',
            'Transporte Express': 'Transporte Express',
            'Catering Gourmet': 'Catering Gourmet',
            'Infraestrutura Eventos': 'Infraestrutura Eventos'
        }
        
        total_atualizadas = 0
        
        # Obter todas as despesas que não têm fornecedor
        despesas = DespesaEvento.objects.filter(fornecedor__isnull=True)
        
        for despesa in despesas:
            # Tentar encontrar fornecedor baseado na descrição
            fornecedor_encontrado = None
            
            for nome_antigo, nome_novo in mapeamento_fornecedores.items():
                if nome_antigo.lower() in despesa.descricao.lower():
                    # Buscar fornecedor da empresa do evento
                    fornecedor_encontrado = Fornecedor.objects.filter(
                        empresa_contratante=despesa.evento.empresa_contratante,
                        nome_fantasia=nome_novo,
                        ativo=True
                    ).first()
                    break
            
            # Se não encontrou por descrição, tentar por categoria
            if not fornecedor_encontrado:
                categoria_nome = despesa.categoria.nome.lower()
                
                if 'equipamento' in categoria_nome:
                    fornecedor_encontrado = Fornecedor.objects.filter(
                        empresa_contratante=despesa.evento.empresa_contratante,
                        tipo_fornecedor='equipamentos',
                        ativo=True
                    ).first()
                elif 'decoração' in categoria_nome:
                    fornecedor_encontrado = Fornecedor.objects.filter(
                        empresa_contratante=despesa.evento.empresa_contratante,
                        tipo_fornecedor='decoracao',
                        ativo=True
                    ).first()
                elif 'segurança' in categoria_nome:
                    fornecedor_encontrado = Fornecedor.objects.filter(
                        empresa_contratante=despesa.evento.empresa_contratante,
                        tipo_fornecedor='seguranca',
                        ativo=True
                    ).first()
                elif 'marketing' in categoria_nome:
                    fornecedor_encontrado = Fornecedor.objects.filter(
                        empresa_contratante=despesa.evento.empresa_contratante,
                        tipo_fornecedor='marketing',
                        ativo=True
                    ).first()
                elif 'alimentação' in categoria_nome:
                    fornecedor_encontrado = Fornecedor.objects.filter(
                        empresa_contratante=despesa.evento.empresa_contratante,
                        tipo_fornecedor='alimentacao',
                        ativo=True
                    ).first()
            
            # Atualizar despesa com o fornecedor encontrado
            if fornecedor_encontrado:
                despesa.fornecedor = fornecedor_encontrado
                despesa.save()
                total_atualizadas += 1
                self.stdout.write(f'  ✓ Atualizada: {despesa.descricao} -> {fornecedor_encontrado.nome_fantasia}')
            else:
                self.stdout.write(f'  ⚠ Não encontrado fornecedor para: {despesa.descricao}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Processo concluído! {total_atualizadas} despesas atualizadas.')
        )
