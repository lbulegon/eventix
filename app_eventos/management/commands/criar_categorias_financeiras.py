from django.core.management.base import BaseCommand
from app_eventos.models import CategoriaFinanceira, EmpresaContratante


class Command(BaseCommand):
    help = 'Cria categorias financeiras padrão para todas as empresas'

    def handle(self, *args, **options):
        # Categorias padrão para despesas
        categorias_despesas = [
            {
                'nome': 'Alimentação',
                'descricao': 'Despesas com alimentação e bebidas',
                'tipo': 'despesa',
                'cor': '#dc3545'
            },
            {
                'nome': 'Locação de Equipamentos',
                'descricao': 'Aluguel de equipamentos para o evento',
                'tipo': 'despesa',
                'cor': '#fd7e14'
            },
            {
                'nome': 'Recursos Humanos',
                'descricao': 'Pagamentos de freelancers e funcionários',
                'tipo': 'despesa',
                'cor': '#e83e8c'
            },
            {
                'nome': 'Marketing e Publicidade',
                'descricao': 'Despesas com marketing e publicidade',
                'tipo': 'despesa',
                'cor': '#6f42c1'
            },
            {
                'nome': 'Transporte',
                'descricao': 'Despesas com transporte e logística',
                'tipo': 'despesa',
                'cor': '#20c997'
            },
            {
                'nome': 'Segurança',
                'descricao': 'Despesas com segurança e vigilância',
                'tipo': 'despesa',
                'cor': '#6c757d'
            },
            {
                'nome': 'Decoração',
                'descricao': 'Despesas com decoração e ambientação',
                'tipo': 'despesa',
                'cor': '#ffc107'
            },
            {
                'nome': 'Infraestrutura',
                'descricao': 'Despesas com infraestrutura e montagem',
                'tipo': 'despesa',
                'cor': '#17a2b8'
            },
            {
                'nome': 'Impostos e Taxas',
                'descricao': 'Impostos, taxas e encargos',
                'tipo': 'despesa',
                'cor': '#495057'
            },
            {
                'nome': 'Outros',
                'descricao': 'Outras despesas não categorizadas',
                'tipo': 'despesa',
                'cor': '#6c757d'
            }
        ]

        # Categorias padrão para receitas
        categorias_receitas = [
            {
                'nome': 'Venda de Ingressos',
                'descricao': 'Receitas com venda de ingressos',
                'tipo': 'receita',
                'cor': '#28a745'
            },
            {
                'nome': 'Patrocínios',
                'descricao': 'Receitas com patrocínios',
                'tipo': 'receita',
                'cor': '#007bff'
            },
            {
                'nome': 'Venda de Produtos',
                'descricao': 'Receitas com venda de produtos',
                'tipo': 'receita',
                'cor': '#20c997'
            },
            {
                'nome': 'Serviços Adicionais',
                'descricao': 'Receitas com serviços adicionais',
                'tipo': 'receita',
                'cor': '#fd7e14'
            },
            {
                'nome': 'Aluguel de Espaços',
                'descricao': 'Receitas com aluguel de espaços',
                'tipo': 'receita',
                'cor': '#6f42c1'
            },
            {
                'nome': 'Outros',
                'descricao': 'Outras receitas não categorizadas',
                'tipo': 'receita',
                'cor': '#6c757d'
            }
        ]

        empresas = EmpresaContratante.objects.filter(ativo=True)
        
        if not empresas.exists():
            self.stdout.write(
                self.style.WARNING('Nenhuma empresa ativa encontrada. Criando categorias globais.')
            )
            empresas = [None]  # Para criar categorias globais

        total_criadas = 0
        
        for empresa in empresas:
            self.stdout.write(f'Criando categorias para: {empresa.nome_fantasia if empresa else "Global"}')
            
            # Criar categorias de despesas
            for cat_data in categorias_despesas:
                categoria, created = CategoriaFinanceira.objects.get_or_create(
                    empresa_contratante=empresa,
                    nome=cat_data['nome'],
                    defaults=cat_data
                )
                if created:
                    total_criadas += 1
                    self.stdout.write(f'  ✓ Criada: {categoria.nome}')
            
            # Criar categorias de receitas
            for cat_data in categorias_receitas:
                categoria, created = CategoriaFinanceira.objects.get_or_create(
                    empresa_contratante=empresa,
                    nome=cat_data['nome'],
                    defaults=cat_data
                )
                if created:
                    total_criadas += 1
                    self.stdout.write(f'  ✓ Criada: {categoria.nome}')

        self.stdout.write(
            self.style.SUCCESS(f'Processo concluído! {total_criadas} categorias criadas.')
        )
