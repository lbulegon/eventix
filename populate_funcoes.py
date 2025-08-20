#!/usr/bin/env python
"""
Script para popular as tabelas TipoFuncao e Funcao com dados comuns para eventos
"""
import os
import sys
import django

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from app_eventos.models import TipoFuncao, Funcao

def criar_tipos_funcao():
    """Cria os tipos de função comuns para eventos"""
    
    tipos_funcao_data = [
        {
            'nome': 'Produção',
            'descricao': 'Funções relacionadas à produção e execução do evento'
        },
        {
            'nome': 'Técnica',
            'descricao': 'Funções técnicas e de equipamentos'
        },
        {
            'nome': 'Operacional',
            'descricao': 'Funções operacionais e logísticas'
        },
        {
            'nome': 'Atendimento',
            'descricao': 'Funções de atendimento ao público'
        },
        {
            'nome': 'Segurança',
            'descricao': 'Funções de segurança e controle de acesso'
        },
        {
            'nome': 'Administrativa',
            'descricao': 'Funções administrativas e de suporte'
        },
        {
            'nome': 'Criativa',
            'descricao': 'Funções criativas e artísticas'
        },
        {
            'nome': 'Especializada',
            'descricao': 'Funções que requerem especialização específica'
        },
        {
            'nome': 'Alimentação',
            'descricao': 'Funções relacionadas à preparação e serviço de alimentos e bebidas'
        }
    ]
    
    tipos_criados = []
    for tipo_data in tipos_funcao_data:
        tipo, created = TipoFuncao.objects.get_or_create(
            nome=tipo_data['nome'],
            defaults=tipo_data
        )
        if created:
            print(f"✅ Tipo de função criado: {tipo.nome}")
        else:
            print(f"ℹ️  Tipo de função já existe: {tipo.nome}")
        tipos_criados.append(tipo)
    
    return tipos_criados

def criar_funcoes(tipos_funcao):
    """Cria as funções específicas para cada tipo"""
    
    # Mapear tipos de função para suas funções específicas
    funcoes_por_tipo = {
        'Produção': [
            {'nome': 'Produtor Executivo', 'descricao': 'Responsável pela execução geral do evento'},
            {'nome': 'Produtor de Palco', 'descricao': 'Responsável pela produção no palco'},
            {'nome': 'Coordenador de Produção', 'descricao': 'Coordena as atividades de produção'},
            {'nome': 'Assistente de Produção', 'descricao': 'Auxilia nas atividades de produção'},
        ],
        'Técnica': [
            {'nome': 'Técnico de Som', 'descricao': 'Responsável pela operação de equipamentos de áudio'},
            {'nome': 'Técnico de Iluminação', 'descricao': 'Responsável pela operação de equipamentos de iluminação'},
            {'nome': 'Técnico de Vídeo', 'descricao': 'Responsável pela operação de equipamentos de vídeo'},
            {'nome': 'Técnico de Palco', 'descricao': 'Responsável pela montagem e operação do palco'},
            {'nome': 'Técnico de Backline', 'descricao': 'Responsável pelos instrumentos musicais'},
            {'nome': 'Técnico de RF', 'descricao': 'Responsável por equipamentos de rádio frequência'},
        ],
        'Operacional': [
            {'nome': 'Operador de Logística', 'descricao': 'Responsável pela logística do evento'},
            {'nome': 'Montador de Estruturas', 'descricao': 'Responsável pela montagem de estruturas'},
            {'nome': 'Operador de Elevação', 'descricao': 'Responsável por equipamentos de elevação'},
            {'nome': 'Operador de Gerador', 'descricao': 'Responsável pela operação de geradores'},
            {'nome': 'Operador de Ar Condicionado', 'descricao': 'Responsável pelos sistemas de climatização'},
        ],
        'Atendimento': [
            {'nome': 'Recepcionista', 'descricao': 'Atende o público na recepção'},
            {'nome': 'Anfitrião', 'descricao': 'Recebe e orienta os convidados'},
            {'nome': 'Atendente de Bar', 'descricao': 'Atende no bar do evento'},
            {'nome': 'Atendente de Buffet', 'descricao': 'Atende no buffet do evento'},
            {'nome': 'Hostess', 'descricao': 'Recepciona e orienta os convidados'},
        ],
        'Segurança': [
            {'nome': 'Segurança', 'descricao': 'Responsável pela segurança do evento'},
            {'nome': 'Controlador de Acesso', 'descricao': 'Controla o acesso ao evento'},
            {'nome': 'Segurança de Palco', 'descricao': 'Responsável pela segurança do palco'},
            {'nome': 'Segurança VIP', 'descricao': 'Responsável pela segurança de convidados especiais'},
        ],
        'Administrativa': [
            {'nome': 'Assistente Administrativo', 'descricao': 'Auxilia nas tarefas administrativas'},
            {'nome': 'Controlador de Credenciais', 'descricao': 'Controla e distribui credenciais'},
            {'nome': 'Operador de Caixa', 'descricao': 'Opera caixas e sistemas de pagamento'},
            {'nome': 'Assistente de RH', 'descricao': 'Auxilia nas tarefas de recursos humanos'},
        ],
        'Criativa': [
            {'nome': 'Designer Gráfico', 'descricao': 'Responsável pela identidade visual'},
            {'nome': 'Fotógrafo', 'descricao': 'Registra o evento em fotos'},
            {'nome': 'Videomaker', 'descricao': 'Registra o evento em vídeo'},
            {'nome': 'Decorador', 'descricao': 'Responsável pela decoração do evento'},
            {'nome': 'Maquiador', 'descricao': 'Responsável pela maquiagem'},
        ],
        'Especializada': [
            {'nome': 'Intérprete de Libras', 'descricao': 'Faz interpretação em Libras'},
            {'nome': 'Tradutor', 'descricao': 'Faz tradução simultânea'},
            {'nome': 'Médico', 'descricao': 'Atendimento médico de emergência'},
            {'nome': 'Enfermeiro', 'descricao': 'Auxiliar médico'},
            {'nome': 'Bombeiro Civil', 'descricao': 'Responsável pela segurança contra incêndio'},
        ],
        'Alimentação': [
            {'nome': 'Chef de Cozinha', 'descricao': 'Responsável pela preparação dos pratos principais'},
            {'nome': 'Sous Chef', 'descricao': 'Auxiliar do chef de cozinha'},
            {'nome': 'Cozinheiro', 'descricao': 'Prepara alimentos e pratos'},
            {'nome': 'Auxiliar de Cozinha', 'descricao': 'Auxilia na preparação de alimentos'},
            {'nome': 'Chapeiro', 'descricao': 'Responsável pela preparação de carnes e grelhados'},
            {'nome': 'Salgadeiro', 'descricao': 'Prepara salgados e canapés'},
            {'nome': 'Confeiteiro', 'descricao': 'Prepara sobremesas e doces'},
            {'nome': 'Padeiro', 'descricao': 'Prepara pães e massas'},
            {'nome': 'Garçom', 'descricao': 'Atende mesas e serve refeições'},
            {'nome': 'Bartender', 'descricao': 'Prepara e serve bebidas alcoólicas'},
            {'nome': 'Sommelier', 'descricao': 'Especialista em vinhos'},
            {'nome': 'Barista', 'descricao': 'Prepara e serve café e bebidas quentes'},
            {'nome': 'Atendente de Buffet', 'descricao': 'Atende no buffet self-service'},
            {'nome': 'Lavador de Louças', 'descricao': 'Responsável pela limpeza de louças e utensílios'},
            {'nome': 'Estoquista de Alimentos', 'descricao': 'Controla estoque de alimentos e bebidas'},
            {'nome': 'Auxiliar de Serviço', 'descricao': 'Auxilia no serviço de alimentação'},
        ]
    }
    
    funcoes_criadas = 0
    for tipo in tipos_funcao:
        if tipo.nome in funcoes_por_tipo:
            for funcao_data in funcoes_por_tipo[tipo.nome]:
                funcao, created = Funcao.objects.get_or_create(
                    nome=funcao_data['nome'],
                    tipo_funcao=tipo,
                    defaults=funcao_data
                )
                if created:
                    print(f"✅ Função criada: {funcao.nome} ({tipo.nome})")
                    funcoes_criadas += 1
                else:
                    print(f"ℹ️  Função já existe: {funcao.nome} ({tipo.nome})")
    
    return funcoes_criadas

def main():
    """Função principal do script"""
    print("🚀 Iniciando população das tabelas de funções...")
    print("=" * 50)
    
    # Criar tipos de função
    print("\n📋 Criando tipos de função...")
    tipos_funcao = criar_tipos_funcao()
    
    # Criar funções
    print("\n👥 Criando funções específicas...")
    total_funcoes = criar_funcoes(tipos_funcao)
    
    # Resumo final
    print("\n" + "=" * 50)
    print("📊 RESUMO:")
    print(f"• Tipos de função: {len(tipos_funcao)}")
    print(f"• Funções criadas: {total_funcoes}")
    print(f"• Total de funções no sistema: {Funcao.objects.count()}")
    print("=" * 50)
    print("✅ População concluída com sucesso!")

if __name__ == '__main__':
    main()
