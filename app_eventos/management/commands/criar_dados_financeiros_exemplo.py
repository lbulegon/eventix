from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from app_eventos.models import Evento, CategoriaFinanceira, DespesaEvento, ReceitaEvento


class Command(BaseCommand):
    help = 'Cria dados financeiros de exemplo para eventos existentes'

    def handle(self, *args, **options):
        eventos = Evento.objects.filter(ativo=True)
        
        if not eventos.exists():
            self.stdout.write(
                self.style.WARNING('Nenhum evento ativo encontrado. Crie eventos primeiro.')
            )
            return
        
        total_despesas = 0
        total_receitas = 0
        
        for evento in eventos:
            self.stdout.write(f'Criando dados financeiros para: {evento.nome}')
            
            # Obter categorias da empresa do evento
            empresa = evento.empresa_contratante
            categorias_despesas = CategoriaFinanceira.objects.filter(
                empresa_contratante=empresa,
                tipo__in=['despesa', 'ambos'],
                ativo=True
            )
            categorias_receitas = CategoriaFinanceira.objects.filter(
                empresa_contratante=empresa,
                tipo__in=['receita', 'ambos'],
                ativo=True
            )
            
            # Criar despesas de exemplo
            despesas_exemplo = [
                {
                    'descricao': 'Aluguel de Equipamentos de Som',
                    'valor': Decimal('2500.00'),
                    'categoria_nome': 'Locação de Equipamentos',
                    'fornecedor': 'Sound Pro Ltda',
                    'data_vencimento': evento.data_inicio - timedelta(days=7),
                    'status': 'pago'
                },
                {
                    'descricao': 'Decoração e Ambientação',
                    'valor': Decimal('1800.00'),
                    'categoria_nome': 'Decoração',
                    'fornecedor': 'Decorações Eventos',
                    'data_vencimento': evento.data_inicio - timedelta(days=3),
                    'status': 'pendente'
                },
                {
                    'descricao': 'Segurança e Vigilância',
                    'valor': Decimal('1200.00'),
                    'categoria_nome': 'Segurança',
                    'fornecedor': 'Segurança Total',
                    'data_vencimento': evento.data_inicio - timedelta(days=1),
                    'status': 'pendente'
                },
                {
                    'descricao': 'Marketing e Publicidade',
                    'valor': Decimal('800.00'),
                    'categoria_nome': 'Marketing e Publicidade',
                    'fornecedor': 'Agência Digital',
                    'data_vencimento': evento.data_inicio - timedelta(days=10),
                    'status': 'pago'
                }
            ]
            
            # Criar receitas de exemplo
            receitas_exemplo = [
                {
                    'descricao': 'Venda de Ingressos',
                    'valor': Decimal('5000.00'),
                    'categoria_nome': 'Venda de Ingressos',
                    'cliente': 'Vendas Online',
                    'data_vencimento': evento.data_inicio - timedelta(days=5),
                    'status': 'recebido'
                },
                {
                    'descricao': 'Patrocínio Principal',
                    'valor': Decimal('3000.00'),
                    'categoria_nome': 'Patrocínios',
                    'cliente': 'Empresa Patrocinadora',
                    'data_vencimento': evento.data_inicio - timedelta(days=15),
                    'status': 'recebido'
                },
                {
                    'descricao': 'Venda de Produtos',
                    'valor': Decimal('800.00'),
                    'categoria_nome': 'Venda de Produtos',
                    'cliente': 'Vendas no Local',
                    'data_vencimento': evento.data_inicio + timedelta(days=1),
                    'status': 'pendente'
                }
            ]
            
            # Criar despesas
            for despesa_data in despesas_exemplo:
                categoria = categorias_despesas.filter(nome=despesa_data['categoria_nome']).first()
                if categoria:
                    despesa, created = DespesaEvento.objects.get_or_create(
                        evento=evento,
                        descricao=despesa_data['descricao'],
                        defaults={
                            'categoria': categoria,
                            'valor': despesa_data['valor'],
                            'data_vencimento': despesa_data['data_vencimento'],
                            'fornecedor': despesa_data['fornecedor'],
                            'status': despesa_data['status'],
                            'data_pagamento': despesa_data['data_vencimento'] if despesa_data['status'] == 'pago' else None
                        }
                    )
                    if created:
                        total_despesas += 1
                        self.stdout.write(f'  ✓ Despesa criada: {despesa.descricao}')
            
            # Criar receitas
            for receita_data in receitas_exemplo:
                categoria = categorias_receitas.filter(nome=receita_data['categoria_nome']).first()
                if categoria:
                    receita, created = ReceitaEvento.objects.get_or_create(
                        evento=evento,
                        descricao=receita_data['descricao'],
                        defaults={
                            'categoria': categoria,
                            'valor': receita_data['valor'],
                            'data_vencimento': receita_data['data_vencimento'],
                            'cliente': receita_data['cliente'],
                            'status': receita_data['status'],
                            'data_recebimento': receita_data['data_vencimento'] if receita_data['status'] == 'recebido' else None
                        }
                    )
                    if created:
                        total_receitas += 1
                        self.stdout.write(f'  ✓ Receita criada: {receita.descricao}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Processo concluído! {total_despesas} despesas e {total_receitas} receitas criadas.')
        )
