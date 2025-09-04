#!/usr/bin/env python
"""
Script simplificado para popular dados de exemplo dos novos modelos do Eventix
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from app_eventos.models import (
    # Modelos existentes
    EmpresaContratante, Evento, Freelance, User, Fornecedor, SetorEvento,
    
    # Novos modelos principais
    MetricaEvento, RelatorioAnalytics, AvaliacaoEvento, 
    ChecklistMobile, ItemChecklistMobile, RiscoEvento,
    MarketplaceFreelancer, AvaliacaoFornecedor
)

def criar_metricas_evento():
    """Criar métricas de exemplo para eventos"""
    print("Criando métricas de evento...")
    
    eventos = Evento.objects.all()[:2]
    users = User.objects.all()[:1]
    
    if not users:
        print("Nenhum usuário encontrado. Pulando métricas.")
        return
    
    responsavel = users[0]
    
    metricas_data = [
        {
            'nome': 'Participantes Confirmados',
            'descricao': 'Número de participantes confirmados',
            'tipo': 'operacional',
            'valor_objetivo': Decimal('200.00'),
            'valor_real': Decimal('150.00'),
            'unidade_medida': 'pessoas',
            'responsavel': responsavel
        },
        {
            'nome': 'Satisfação Geral',
            'descricao': 'Avaliação média de satisfação',
            'tipo': 'satisfacao',
            'valor_objetivo': Decimal('4.50'),
            'valor_real': Decimal('4.20'),
            'unidade_medida': 'escala_5',
            'responsavel': responsavel
        }
    ]
    
    for evento in eventos:
        for metrica_data in metricas_data:
            metrica_data['evento'] = evento
            MetricaEvento.objects.get_or_create(
                evento=evento,
                nome=metrica_data['nome'],
                defaults=metrica_data
            )

def criar_relatorios_analytics():
    """Criar relatórios de analytics"""
    print("Criando relatórios de analytics...")
    
    empresas = EmpresaContratante.objects.all()[:2]
    
    relatorios_data = [
        {
            'nome': 'Relatório de Performance',
            'descricao': 'Análise de performance do evento',
            'tipo': 'operacional',
            'periodicidade': 'mensal',
            'template_relatorio': 'Template básico para relatório de performance',
            'parametros': {'incluir_metricas': True}
        },
        {
            'nome': 'Análise de Satisfação',
            'descricao': 'Relatório de satisfação dos participantes',
            'tipo': 'qualidade',
            'periodicidade': 'semanal',
            'template_relatorio': 'Template para análise de satisfação',
            'parametros': {'tipo_pesquisa': 'satisfacao'}
        }
    ]
    
    for empresa in empresas:
        for relatorio_data in relatorios_data:
            relatorio_data['empresa_contratante'] = empresa
            RelatorioAnalytics.objects.get_or_create(
                empresa_contratante=empresa,
                nome=relatorio_data['nome'],
                defaults=relatorio_data
            )

def criar_avaliacoes_evento():
    """Criar avaliações de eventos"""
    print("Criando avaliações de eventos...")
    
    eventos = Evento.objects.all()[:2]
    empresas = EmpresaContratante.objects.all()[:2]
    
    avaliacoes_data = [
        {
            'tipo_avaliador': 'participante',
            'nome_avaliador': 'João Silva',
            'email_avaliador': 'joao.silva@email.com',
            'nota_geral': 9,
            'comentarios': 'Evento muito bem organizado e conteúdo de qualidade.',
            'aspectos_positivos': 'Organização excelente, palestrantes qualificados, local adequado',
            'aspectos_melhorar': 'Poderia ter mais tempo para networking',
            'recomendaria': True,
            'anonima': False
        },
        {
            'tipo_avaliador': 'cliente',
            'nome_avaliador': 'Maria Santos',
            'email_avaliador': 'maria.santos@empresa.com',
            'nota_geral': 8,
            'comentarios': 'Evento atendeu às expectativas da empresa.',
            'aspectos_positivos': 'Boa estrutura, equipe atenciosa',
            'aspectos_melhorar': 'Melhorar comunicação pré-evento',
            'recomendaria': True,
            'anonima': False
        }
    ]
    
    for evento in eventos:
        for empresa in empresas:
            for avaliacao_data in avaliacoes_data:
                avaliacao_data['evento'] = evento
                avaliacao_data['empresa_contratante'] = empresa
                AvaliacaoEvento.objects.get_or_create(
                    evento=evento,
                    empresa_contratante=empresa,
                    nome_avaliador=avaliacao_data['nome_avaliador'],
                    defaults=avaliacao_data
                )

def criar_checklists_mobile():
    """Criar checklists mobile"""
    print("Criando checklists mobile...")
    
    eventos = Evento.objects.all()[:2]
    users = User.objects.all()[:1]
    setores = SetorEvento.objects.all()[:1]
    
    if not users:
        print("Nenhum usuário encontrado. Pulando checklists.")
        return
    
    responsavel = users[0]
    setor = setores[0] if setores else None
    
    checklists_data = [
        {
            'titulo': 'Checklist de Montagem',
            'descricao': 'Checklist para montagem do evento',
            'status': 'pendente',
            'responsavel': responsavel,
            'setor': setor,
            'data_limite': datetime.now() + timedelta(days=7)
        },
        {
            'titulo': 'Checklist de Segurança',
            'descricao': 'Checklist de segurança do evento',
            'status': 'pendente',
            'responsavel': responsavel,
            'setor': setor,
            'data_limite': datetime.now() + timedelta(days=5)
        }
    ]
    
    for evento in eventos:
        for checklist_data in checklists_data:
            checklist_data['evento'] = evento
            checklist, created = ChecklistMobile.objects.get_or_create(
                evento=evento,
                titulo=checklist_data['titulo'],
                defaults=checklist_data
            )
            
            if created:
                # Criar itens do checklist
                itens_data = [
                    {'descricao': 'Verificar equipamentos de som', 'obrigatorio': True, 'ordem': 1},
                    {'descricao': 'Testar iluminação', 'obrigatorio': True, 'ordem': 2},
                    {'descricao': 'Verificar extintores', 'obrigatorio': True, 'ordem': 3}
                ]
                
                for item_data in itens_data:
                    item_data['checklist'] = checklist
                    ItemChecklistMobile.objects.get_or_create(
                        checklist=checklist,
                        descricao=item_data['descricao'],
                        defaults=item_data
                    )

def criar_riscos_evento():
    """Criar riscos de eventos"""
    print("Criando riscos de eventos...")
    
    eventos = Evento.objects.all()[:2]
    users = User.objects.all()[:1]
    
    if not users:
        print("Nenhum usuário encontrado. Pulando riscos.")
        return
    
    responsavel = users[0]
    
    riscos_data = [
        {
            'titulo': 'Risco de Chuva',
            'tipo': 'ambiental',
            'probabilidade': 3,
            'impacto': 4,
            'nivel': 'alto',
            'descricao': 'Possibilidade de chuva durante o evento externo',
            'acoes_mitigacao': 'Contratar tendas de emergência',
            'plano_contingencia': 'Transferir atividades para área coberta',
            'responsavel': responsavel,
            'status': 'identificado'
        }
    ]
    
    for evento in eventos:
        for risco_data in riscos_data:
            risco_data['evento'] = evento
            RiscoEvento.objects.get_or_create(
                evento=evento,
                titulo=risco_data['titulo'],
                defaults=risco_data
            )

def criar_marketplace_freelancers():
    """Criar marketplace de freelancers"""
    print("Criando marketplace de freelancers...")
    
    freelancers = Freelance.objects.all()[:3]
    
    for freelancer in freelancers:
        marketplace_data = {
            'freelancer': freelancer,
            'status': 'ativo',
            'perfil_publico': {'bio': f'Freelancer experiente em eventos', 'foto': None},
            'avaliacao_media': Decimal(str(round(random.uniform(3.5, 5.0), 1))),
            'total_avaliacoes': random.randint(5, 50),
            'portfolio': [{'titulo': 'Evento Corporativo', 'descricao': 'Organização de evento corporativo'}],
            'disponibilidade': {'status': 'disponivel', 'horarios': 'flexivel'},
            'especialidades': ['Organização de Eventos', 'Coordenação'],
            'projetos_concluidos': random.randint(5, 20),
            'taxa_sucesso': Decimal(str(round(random.uniform(85.0, 100.0), 1)))
        }
        
        MarketplaceFreelancer.objects.get_or_create(
            freelancer=freelancer,
            defaults=marketplace_data
        )

def criar_avaliacoes_fornecedores():
    """Criar avaliações de fornecedores"""
    print("Criando avaliações de fornecedores...")
    
    fornecedores = Fornecedor.objects.all()[:2]
    empresas = EmpresaContratante.objects.all()[:2]
    
    for fornecedor in fornecedores:
        for empresa in empresas:
            avaliacao_data = {
                'fornecedor': fornecedor,
                'empresa_avaliadora': empresa,
                'nota_qualidade': random.randint(3, 5),
                'nota_prazo': random.randint(3, 5),
                'nota_preco': random.randint(3, 5),
                'nota_atendimento': random.randint(3, 5),
                'comentarios': f'Avaliação da {empresa.nome_fantasia} para {fornecedor.nome}',
                'data_avaliacao': datetime.now() - timedelta(days=random.randint(1, 30)),
                'anonima': False
            }
            
            AvaliacaoFornecedor.objects.get_or_create(
                fornecedor=fornecedor,
                empresa_avaliadora=empresa,
                defaults=avaliacao_data
            )

def main():
    """Função principal para executar todos os scripts de população"""
    print("=== POPULANDO DADOS DOS NOVOS MODELOS (VERSÃO SIMPLIFICADA) ===")
    print()
    
    try:
        # Verificar se existem dados básicos
        if not Evento.objects.exists():
            print("Nenhum evento encontrado. Execute primeiro o script populate_sistema_completo.py")
            return
        
        if not User.objects.exists():
            print("Nenhum usuário encontrado. Execute primeiro o script populate_sistema_completo.py")
            return
        
        # Executar funções de população
        criar_metricas_evento()
        criar_relatorios_analytics()
        criar_avaliacoes_evento()
        criar_checklists_mobile()
        criar_riscos_evento()
        criar_marketplace_freelancers()
        criar_avaliacoes_fornecedores()
        
        print()
        print("=== POPULAÇÃO CONCLUÍDA COM SUCESSO! ===")
        print("Dados de exemplo criados para os principais novos modelos.")
        
    except Exception as e:
        print(f"Erro durante a população: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
