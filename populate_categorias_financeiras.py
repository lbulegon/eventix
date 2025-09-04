#!/usr/bin/env python
"""
Script para popular categorias financeiras específicas para controle de custos de eventos
"""
import os
import sys
import django
from datetime import date, timedelta

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from app_eventos.models import CategoriaFinanceira, EmpresaContratante

def criar_categorias_financeiras():
    """Cria categorias financeiras específicas para controle de custos"""
    print("💰 Criando categorias financeiras...")
    
    # Buscar a empresa contratante
    empresa = EmpresaContratante.objects.first()
    if not empresa:
        print("❌ Nenhuma empresa contratante encontrada. Execute primeiro o script de população completa.")
        return
    
    categorias_data = [
        # DESPESAS - MÃO DE OBRA
        {
            'nome': 'Pagamento de Funcionários',
            'descricao': 'Salários, comissões e benefícios dos funcionários da empresa',
            'tipo': 'despesa',
            'cor': '#dc3545'
        },
        {
            'nome': 'Pagamento de Freelancers',
            'descricao': 'Cachês e pagamentos para freelancers contratados para eventos',
            'tipo': 'despesa',
            'cor': '#fd7e14'
        },
        {
            'nome': 'Encargos Trabalhistas',
            'descricao': 'INSS, FGTS, férias, 13º salário e outros encargos',
            'tipo': 'despesa',
            'cor': '#e83e8c'
        },
        
        # DESPESAS - EQUIPAMENTOS E INFRAESTRUTURA
        {
            'nome': 'Locação de Equipamentos',
            'descricao': 'Aluguel de equipamentos de som, iluminação, estrutura, etc.',
            'tipo': 'despesa',
            'cor': '#6f42c1'
        },
        {
            'nome': 'Compra de Equipamentos',
            'descricao': 'Aquisição de equipamentos permanentes para a empresa',
            'tipo': 'despesa',
            'cor': '#6610f2'
        },
        {
            'nome': 'Manutenção de Equipamentos',
            'descricao': 'Reparos, calibração e manutenção preventiva/corretiva',
            'tipo': 'despesa',
            'cor': '#d63384'
        },
        
        # DESPESAS - LOCAIS E ESPAÇOS
        {
            'nome': 'Locação de Espaços',
            'descricao': 'Aluguel de locais para realização de eventos',
            'tipo': 'despesa',
            'cor': '#20c997'
        },
        {
            'nome': 'Infraestrutura do Local',
            'descricao': 'Montagem, desmontagem, limpeza e preparação do local',
            'tipo': 'despesa',
            'cor': '#198754'
        },
        
        # DESPESAS - INSUMOS E MATERIAIS
        {
            'nome': 'Insumos de Alimentação',
            'descricao': 'Comida, bebidas, ingredientes para cozinha e bar',
            'tipo': 'despesa',
            'cor': '#ffc107'
        },
        {
            'nome': 'Material de Limpeza',
            'descricao': 'Produtos de limpeza, papel higiênico, sabonetes, etc.',
            'tipo': 'despesa',
            'cor': '#fd7e14'
        },
        {
            'nome': 'Material de Escritório',
            'descricao': 'Papel, canetas, impressões, material de escritório',
            'tipo': 'despesa',
            'cor': '#6c757d'
        },
        {
            'nome': 'Decoração e Sinalização',
            'descricao': 'Banners, placas, decoração, material gráfico',
            'tipo': 'despesa',
            'cor': '#0dcaf0'
        },
        
        # DESPESAS - TRANSPORTE E LOGÍSTICA
        {
            'nome': 'Transporte de Equipamentos',
            'descricao': 'Frete, combustível, pedágios para transporte de equipamentos',
            'tipo': 'despesa',
            'cor': '#0d6efd'
        },
        {
            'nome': 'Transporte de Pessoal',
            'descricao': 'Passagens, combustível, hospedagem para equipe',
            'tipo': 'despesa',
            'cor': '#6610f2'
        },
        
        # DESPESAS - MARKETING E COMUNICAÇÃO
        {
            'nome': 'Marketing e Publicidade',
            'descricao': 'Anúncios, redes sociais, material promocional',
            'tipo': 'despesa',
            'cor': '#e83e8c'
        },
        {
            'nome': 'Comunicação',
            'descricao': 'Telefone, internet, rádios, sistemas de comunicação',
            'tipo': 'despesa',
            'cor': '#6f42c1'
        },
        
        # DESPESAS - SEGURANÇA E SEGUROS
        {
            'nome': 'Segurança',
            'descricao': 'Contratação de seguranças, equipamentos de segurança',
            'tipo': 'despesa',
            'cor': '#dc3545'
        },
        {
            'nome': 'Seguros',
            'descricao': 'Seguros de equipamentos, responsabilidade civil, etc.',
            'tipo': 'despesa',
            'cor': '#fd7e14'
        },
        
        # DESPESAS - ADMINISTRATIVAS
        {
            'nome': 'Taxas e Impostos',
            'descricao': 'Taxas governamentais, impostos, licenças',
            'tipo': 'despesa',
            'cor': '#6c757d'
        },
        {
            'nome': 'Serviços Contábeis',
            'descricao': 'Contador, auditoria, serviços contábeis',
            'tipo': 'despesa',
            'cor': '#198754'
        },
        {
            'nome': 'Serviços Jurídicos',
            'descricao': 'Advogados, consultoria jurídica, contratos',
            'tipo': 'despesa',
            'cor': '#0dcaf0'
        },
        
        # DESPESAS - OUTRAS
        {
            'nome': 'Energia Elétrica',
            'descricao': 'Consumo de energia elétrica em eventos e escritório',
            'tipo': 'despesa',
            'cor': '#ffc107'
        },
        {
            'nome': 'Água e Saneamento',
            'descricao': 'Consumo de água, esgoto, saneamento',
            'tipo': 'despesa',
            'cor': '#0d6efd'
        },
        {
            'nome': 'Outras Despesas',
            'descricao': 'Despesas diversas não categorizadas',
            'tipo': 'despesa',
            'cor': '#6c757d'
        },
        
        # RECEITAS
        {
            'nome': 'Venda de Ingressos',
            'descricao': 'Receita com venda de ingressos para eventos',
            'tipo': 'receita',
            'cor': '#198754'
        },
        {
            'nome': 'Venda de Alimentos e Bebidas',
            'descricao': 'Receita com venda de comida e bebidas no evento',
            'tipo': 'receita',
            'cor': '#20c997'
        },
        {
            'nome': 'Patrocínios',
            'descricao': 'Receita com patrocínios e apoios comerciais',
            'tipo': 'receita',
            'cor': '#0dcaf0'
        },
        {
            'nome': 'Venda de Produtos',
            'descricao': 'Receita com venda de produtos e merchandising',
            'tipo': 'receita',
            'cor': '#6f42c1'
        },
        {
            'nome': 'Serviços Terceirizados',
            'descricao': 'Receita com prestação de serviços para terceiros',
            'tipo': 'receita',
            'cor': '#fd7e14'
        },
        {
            'nome': 'Outras Receitas',
            'descricao': 'Outras receitas não categorizadas',
            'tipo': 'receita',
            'cor': '#ffc107'
        }
    ]
    
    categorias_criadas = []
    for categoria_data in categorias_data:
        categoria_data['empresa_contratante'] = empresa
        categoria, created = CategoriaFinanceira.objects.get_or_create(
            nome=categoria_data['nome'],
            empresa_contratante=empresa,
            defaults=categoria_data
        )
        
        if created:
            print(f"✅ Categoria criada: {categoria.nome} ({categoria.get_tipo_display()})")
            categorias_criadas.append(categoria)
        else:
            print(f"ℹ️  Categoria já existe: {categoria.nome}")
    
    return categorias_criadas

def main():
    """Função principal"""
    print("🚀 Iniciando população de categorias financeiras...")
    print("=" * 60)
    
    categorias = criar_categorias_financeiras()
    
    print("=" * 60)
    print("📊 RESUMO:")
    print(f"• Total de categorias financeiras: {len(categorias)}")
    print("• Categorias de despesas: Pagamento de funcionários, equipamentos, locais, insumos, etc.")
    print("• Categorias de receitas: Ingressos, alimentos, patrocínios, etc.")
    print("=" * 60)
    print("✅ Categorias financeiras criadas com sucesso!")

if __name__ == "__main__":
    main()
