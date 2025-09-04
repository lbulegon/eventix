#!/usr/bin/env python
"""
Script para popular dados de exemplo dos novos modelos do Eventix
Inclui dados para Analytics, Qualidade, Automação, Mobilidade, Riscos, IA, Marketplace e Crescimento
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
    EmpresaContratante, Evento, SetorEvento, Equipamento, Freelance, User,
    CategoriaFinanceira, Fornecedor, Empresa, LocalEvento,
    
    # Analytics e Business Intelligence
    MetricaEvento, RelatorioAnalytics, DashboardPersonalizado, ComparativoEventos,
    
    # Gestão de Qualidade e Satisfação
    AvaliacaoEvento, IndicadorQualidade, PesquisaSatisfacao, FeedbackFreelancer,
    
    # Automação e Workflows
    WorkflowEvento, RegraNegocio, NotificacaoAutomatica, IntegracaoERP,
    
    # Mobilidade e Field Management
    ChecklistMobile, ItemChecklistMobile, GeolocalizacaoEquipamento, QRCodeEquipamento, ScanQRCode, AppFieldWorker,
    
    # Gestão de Riscos e Compliance
    RiscoEvento, PlanoContingencia, ComplianceEvento, SeguroEvento,
    
    # Inteligência Artificial e Predição
    PrevisaoDemanda, OtimizacaoRecursos, DeteccaoAnomalias, RecomendacaoInteligente,
    
    # Marketplace e Networking
    MarketplaceFreelancer, RedeFornecedores, AvaliacaoFornecedor, ContratoInteligente,
    
    # Gestão de Crescimento e Expansão
    FranchiseEvento, Licenciamento, ExpansaoMercado, ParceriaEstrategica
)

def criar_metricas_evento():
    """Criar métricas de exemplo para eventos"""
    print("Criando métricas de evento...")
    
    eventos = Evento.objects.all()[:3]  # Pegar os primeiros 3 eventos
    users = User.objects.all()[:1]  # Pegar um usuário para ser responsável
    
    if not users:
        print("Nenhum usuário encontrado. Criando métricas sem responsável.")
        return
    
    responsavel = users[0]
    
    metricas_data = [
        {
            'nome': 'Participantes Confirmados',
            'descricao': 'Número de participantes confirmados até ontem',
            'tipo': 'operacional',
            'valor_objetivo': Decimal('200.00'),
            'valor_real': Decimal('150.00'),
            'unidade_medida': 'pessoas',
            'responsavel': responsavel
        },
        {
            'nome': 'Taxa de Ocupação',
            'descricao': 'Taxa de ocupação dos setores do evento',
            'tipo': 'operacional',
            'valor_objetivo': Decimal('90.00'),
            'valor_real': Decimal('85.50'),
            'unidade_medida': 'percentual',
            'responsavel': responsavel
        },
        {
            'nome': 'Satisfação Geral',
            'descricao': 'Avaliação média de satisfação dos participantes',
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
            'nome': 'Relatório de Performance do Evento',
            'descricao': 'Análise completa de performance do evento',
            'tipo': 'operacional',
            'periodicidade': 'mensal',
            'template_relatorio': 'Template para relatório de performance com métricas principais',
            'parametros': {'incluir_metricas': True, 'incluir_financeiro': True},
            'ultima_execucao': datetime.now() - timedelta(days=1),
            'proxima_execucao': datetime.now() + timedelta(days=30)
        },
        {
            'nome': 'Análise de Satisfação dos Participantes',
            'descricao': 'Relatório de satisfação em processamento',
            'tipo': 'qualidade',
            'periodicidade': 'semanal',
            'template_relatorio': 'Template para análise de satisfação com gráficos e comentários',
            'parametros': {'tipo_pesquisa': 'satisfacao', 'incluir_comentarios': True},
            'ultima_execucao': None,
            'proxima_execucao': datetime.now() + timedelta(days=7)
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

def criar_dashboards_personalizados():
    """Criar dashboards personalizados"""
    print("Criando dashboards personalizados...")
    
    empresas = EmpresaContratante.objects.all()[:2]
    
    dashboards_data = [
        {
            'nome': 'Dashboard Executivo',
            'tipo_dashboard': 'executivo',
            'configuracao': {
                'widgets': ['metricas_principais', 'grafico_participacao', 'indicadores_financeiros'],
                'layout': 'grid_3x2',
                'atualizacao_automatica': True
            },
            'ativo': True,
            'observacoes': 'Dashboard para visão executiva dos eventos'
        },
        {
            'nome': 'Dashboard Operacional',
            'tipo_dashboard': 'operacional',
            'configuracao': {
                'widgets': ['checklist_tarefas', 'status_equipamentos', 'alocacao_pessoal'],
                'layout': 'grid_2x3',
                'atualizacao_automatica': False
            },
            'ativo': True,
            'observacoes': 'Dashboard para acompanhamento operacional'
        }
    ]
    
    for empresa in empresas:
        for dashboard_data in dashboards_data:
            dashboard_data['empresa'] = empresa
            DashboardPersonalizado.objects.get_or_create(
                empresa=empresa,
                nome=dashboard_data['nome'],
                defaults=dashboard_data
            )

def criar_avaliacoes_evento():
    """Criar avaliações de eventos"""
    print("Criando avaliações de eventos...")
    
    eventos = Evento.objects.all()[:3]
    
    avaliacoes_data = [
        {
            'tipo_avaliacao': 'participante',
            'nota_geral': 4.5,
            'criterios': {
                'organizacao': 4.8,
                'local': 4.2,
                'conteudo': 4.6,
                'atendimento': 4.4
            },
            'comentarios': 'Evento muito bem organizado, local excelente e conteúdo de qualidade.',
            'data_avaliacao': datetime.now() - timedelta(days=1),
            'anonima': False
        },
        {
            'tipo_avaliacao': 'organizador',
            'nota_geral': 4.2,
            'criterios': {
                'participacao': 4.0,
                'infraestrutura': 4.5,
                'apoio_tecnico': 4.1,
                'retorno_investimento': 4.0
            },
            'comentarios': 'Boa participação, infraestrutura adequada. Próximo evento com mais tempo de preparação.',
            'data_avaliacao': datetime.now() - timedelta(days=2),
            'anonima': True
        }
    ]
    
    for evento in eventos:
        for avaliacao_data in avaliacoes_data:
            avaliacao_data['evento'] = evento
            AvaliacaoEvento.objects.get_or_create(
                evento=evento,
                tipo_avaliacao=avaliacao_data['tipo_avaliacao'],
                defaults=avaliacao_data
            )

def criar_indicadores_qualidade():
    """Criar indicadores de qualidade"""
    print("Criando indicadores de qualidade...")
    
    eventos = Evento.objects.all()[:2]
    
    indicadores_data = [
        {
            'nome': 'Tempo de Resposta',
            'tipo_indicador': 'tempo',
            'valor_meta': 5.0,
            'valor_atual': 3.2,
            'unidade_medida': 'minutos',
            'data_medicao': datetime.now() - timedelta(days=1),
            'status': 'dentro_meta',
            'observacoes': 'Tempo médio de resposta às solicitações dos participantes'
        },
        {
            'nome': 'Taxa de Satisfação',
            'tipo_indicador': 'percentual',
            'valor_meta': 90.0,
            'valor_atual': 87.5,
            'unidade_medida': 'percentual',
            'data_medicao': datetime.now() - timedelta(days=2),
            'status': 'abaixo_meta',
            'observacoes': 'Taxa de satisfação dos participantes'
        }
    ]
    
    for evento in eventos:
        for indicador_data in indicadores_data:
            indicador_data['evento'] = evento
            IndicadorQualidade.objects.get_or_create(
                evento=evento,
                nome=indicador_data['nome'],
                defaults=indicador_data
            )

def criar_pesquisas_satisfacao():
    """Criar pesquisas de satisfação"""
    print("Criando pesquisas de satisfação...")
    
    eventos = Evento.objects.all()[:2]
    
    pesquisas_data = [
        {
            'titulo': 'Pesquisa de Satisfação - Evento Principal',
            'tipo_pesquisa': 'satisfacao',
            'perguntas': [
                'Como você avalia a organização do evento?',
                'O local atendeu suas expectativas?',
                'O conteúdo foi relevante?',
                'Você recomendaria este evento?'
            ],
            'data_inicio': datetime.now() - timedelta(days=7),
            'data_fim': datetime.now() + timedelta(days=7),
            'status': 'ativa',
            'respostas_recebidas': 45,
            'total_esperado': 100
        }
    ]
    
    for evento in eventos:
        for pesquisa_data in pesquisas_data:
            pesquisa_data['evento'] = evento
            PesquisaSatisfacao.objects.get_or_create(
                evento=evento,
                titulo=pesquisa_data['titulo'],
                defaults=pesquisa_data
            )

def criar_workflows_evento():
    """Criar workflows de eventos"""
    print("Criando workflows de eventos...")
    
    eventos = Evento.objects.all()[:2]
    
    workflows_data = [
        {
            'nome': 'Workflow de Aprovação de Fornecedores',
            'tipo_workflow': 'aprovacao',
            'etapas': [
                {'nome': 'Solicitação', 'responsavel': 'coordenador', 'prazo': 1},
                {'nome': 'Análise', 'responsavel': 'gerente', 'prazo': 2},
                {'nome': 'Aprovação', 'responsavel': 'diretor', 'prazo': 1}
            ],
            'ativo': True,
            'observacoes': 'Workflow para aprovação de novos fornecedores'
        },
        {
            'nome': 'Workflow de Contratação de Freelancers',
            'tipo_workflow': 'contratacao',
            'etapas': [
                {'nome': 'Seleção', 'responsavel': 'rh', 'prazo': 3},
                {'nome': 'Entrevista', 'responsavel': 'supervisor', 'prazo': 2},
                {'nome': 'Contratação', 'responsavel': 'gerente', 'prazo': 1}
            ],
            'ativo': True,
            'observacoes': 'Workflow para contratação de freelancers'
        }
    ]
    
    for evento in eventos:
        for workflow_data in workflows_data:
            workflow_data['evento'] = evento
            WorkflowEvento.objects.get_or_create(
                evento=evento,
                nome=workflow_data['nome'],
                defaults=workflow_data
            )

def criar_checklists_mobile():
    """Criar checklists mobile"""
    print("Criando checklists mobile...")
    
    eventos = Evento.objects.all()[:2]
    
    checklists_data = [
        {
            'nome': 'Checklist de Montagem',
            'tipo_checklist': 'montagem',
            'descricao': 'Checklist para montagem do evento',
            'ativo': True,
            'observacoes': 'Lista de verificação para montagem'
        },
        {
            'nome': 'Checklist de Segurança',
            'tipo_checklist': 'seguranca',
            'descricao': 'Checklist de segurança do evento',
            'ativo': True,
            'observacoes': 'Verificações de segurança obrigatórias'
        }
    ]
    
    for evento in eventos:
        for checklist_data in checklists_data:
            checklist_data['evento'] = evento
            checklist, created = ChecklistMobile.objects.get_or_create(
                evento=evento,
                nome=checklist_data['nome'],
                defaults=checklist_data
            )
            
            if created:
                # Criar itens do checklist
                itens_data = [
                    {'descricao': 'Verificar equipamentos de som', 'obrigatorio': True, 'ordem': 1},
                    {'descricao': 'Testar iluminação', 'obrigatorio': True, 'ordem': 2},
                    {'descricao': 'Verificar extintores', 'obrigatorio': True, 'ordem': 3},
                    {'descricao': 'Confirmar saídas de emergência', 'obrigatorio': True, 'ordem': 4}
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
    
    riscos_data = [
        {
            'nome': 'Risco de Chuva',
            'tipo_risco': 'climatico',
            'probabilidade': 'media',
            'impacto': 'alto',
            'nivel_risco': 'alto',
            'descricao': 'Possibilidade de chuva durante o evento externo',
            'medidas_prevencao': 'Contratar tendas de emergência, monitorar previsão do tempo',
            'plano_contingencia': 'Transferir atividades para área coberta',
            'responsavel': 'Coordenador de Logística',
            'data_identificacao': datetime.now() - timedelta(days=10),
            'status': 'ativo'
        },
        {
            'nome': 'Risco de Falta de Energia',
            'tipo_risco': 'tecnico',
            'probabilidade': 'baixa',
            'impacto': 'critico',
            'nivel_risco': 'medio',
            'descricao': 'Possibilidade de queda de energia elétrica',
            'medidas_prevencao': 'Contratar gerador de emergência, verificar instalações',
            'plano_contingencia': 'Ativar gerador, reduzir consumo de energia',
            'responsavel': 'Técnico de Infraestrutura',
            'data_identificacao': datetime.now() - timedelta(days=8),
            'status': 'ativo'
        }
    ]
    
    for evento in eventos:
        for risco_data in riscos_data:
            risco_data['evento'] = evento
            RiscoEvento.objects.get_or_create(
                evento=evento,
                nome=risco_data['nome'],
                defaults=risco_data
            )

def criar_previsoes_demanda():
    """Criar previsões de demanda"""
    print("Criando previsões de demanda...")
    
    eventos = Evento.objects.all()[:2]
    
    previsoes_data = [
        {
            'tipo_demanda': 'participantes',
            'periodo_previsao': datetime.now() + timedelta(days=30),
            'valor_previsto': 200,
            'confianca': 85.0,
            'metodo_previsao': 'historico',
            'fatores_considerados': ['eventos_similares', 'sazonalidade', 'marketing'],
            'observacoes': 'Previsão baseada em eventos similares do ano passado'
        },
        {
            'tipo_demanda': 'equipamentos',
            'periodo_previsao': datetime.now() + timedelta(days=15),
            'valor_previsto': 50,
            'confianca': 90.0,
            'metodo_previsao': 'capacidade',
            'fatores_considerados': ['capacidade_local', 'tipo_evento', 'duracoes'],
            'observacoes': 'Previsão baseada na capacidade do local e tipo de evento'
        }
    ]
    
    for evento in eventos:
        for previsao_data in previsoes_data:
            previsao_data['evento'] = evento
            PrevisaoDemanda.objects.get_or_create(
                evento=evento,
                tipo_demanda=previsao_data['tipo_demanda'],
                defaults=previsao_data
            )

def criar_marketplace_freelancers():
    """Criar marketplace de freelancers"""
    print("Criando marketplace de freelancers...")
    
    freelancers = Freelance.objects.all()[:5]
    
    for freelancer in freelancers:
        marketplace_data = {
            'freelancer': freelancer,
            'perfil_publico': True,
            'avaliacao_media': round(random.uniform(3.5, 5.0), 1),
            'total_avaliacoes': random.randint(5, 50),
            'portfolio': f'Portfolio do {freelancer.nome} com experiência em eventos',
            'disponibilidade': 'disponivel',
            'taxa_hora': Decimal(str(round(random.uniform(50.0, 200.0), 2))),
            'especialidades': ['Organização de Eventos', 'Coordenação', 'Atendimento'],
            'observacoes': f'Freelancer experiente disponível para eventos'
        }
        
        MarketplaceFreelancer.objects.get_or_create(
            freelancer=freelancer,
            defaults=marketplace_data
        )

def criar_avaliacoes_fornecedores():
    """Criar avaliações de fornecedores"""
    print("Criando avaliações de fornecedores...")
    
    fornecedores = Fornecedor.objects.all()[:3]
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

def criar_franchises_evento():
    """Criar franchises de eventos"""
    print("Criando franchises de eventos...")
    
    empresas = EmpresaContratante.objects.all()[:2]
    
    franchises_data = [
        {
            'empresa_franqueadora': empresas[0],
            'nome_franquia': 'Eventix Premium',
            'tipo_franquia': 'master',
            'investimento_inicial': Decimal('50000.00'),
            'taxa_franquia': Decimal('5000.00'),
            'royalty_mensal': Decimal('2000.00'),
            'territorio': 'Região Metropolitana',
            'status': 'ativa',
            'data_inicio': datetime.now() - timedelta(days=365),
            'observacoes': 'Franquia master para região metropolitana'
        }
    ]
    
    for franchise_data in franchises_data:
        FranchiseEvento.objects.get_or_create(
            empresa_franqueadora=franchise_data['empresa_franqueadora'],
            nome_franquia=franchise_data['nome_franquia'],
            defaults=franchise_data
        )

def main():
    """Função principal para executar todos os scripts de população"""
    print("=== POPULANDO DADOS DOS NOVOS MODELOS ===")
    print()
    
    try:
        # Analytics e Business Intelligence
        criar_metricas_evento()
        criar_relatorios_analytics()
        criar_dashboards_personalizados()
        
        # Gestão de Qualidade e Satisfação
        criar_avaliacoes_evento()
        criar_indicadores_qualidade()
        criar_pesquisas_satisfacao()
        
        # Automação e Workflows
        criar_workflows_evento()
        
        # Mobilidade e Field Management
        criar_checklists_mobile()
        
        # Gestão de Riscos
        criar_riscos_evento()
        
        # Inteligência Artificial
        criar_previsoes_demanda()
        
        # Marketplace e Networking
        criar_marketplace_freelancers()
        criar_avaliacoes_fornecedores()
        
        # Gestão de Crescimento
        criar_franchises_evento()
        
        print()
        print("=== POPULAÇÃO CONCLUÍDA COM SUCESSO! ===")
        print("Dados de exemplo criados para todos os novos modelos.")
        
    except Exception as e:
        print(f"Erro durante a população: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
