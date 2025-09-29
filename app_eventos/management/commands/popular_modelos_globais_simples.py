"""
Comando simplificado para popular modelos globais
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from app_eventos.models_globais import (
    CategoriaGlobal, TipoGlobal, ClassificacaoGlobal,
    ConfiguracaoSistema, ParametroSistema,
    IntegracaoGlobal, WebhookGlobal,
    TemplateGlobal,
    CategoriaFreelancerGlobal, HabilidadeGlobal, FornecedorGlobal
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Popula modelos globais com dados iniciais (versão simplificada)'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando população dos modelos globais...')
        
        # Buscar qualquer usuário existente ou criar um temporário
        admin_sistema = User.objects.first()
        if not admin_sistema:
            self.stdout.write('Criando usuário temporário...')
            admin_sistema = User.objects.create_user(
                username='admin_temp',
                email='admin@temp.com',
                password='admin123',
                tipo_usuario='admin_sistema',
                is_staff=True,
                is_superuser=True
            )
        
        # ============================================================================
        # CATÁLOGOS GERAIS
        # ============================================================================
        
        # Categorias Globais
        categorias_data = [
            {'nome': 'Eventos', 'descricao': 'Categorias relacionadas a eventos', 'icone': '🎉', 'cor': '#FF6B6B', 'ordem': 1},
            {'nome': 'Equipamentos', 'descricao': 'Categorias de equipamentos', 'icone': '🔧', 'cor': '#4ECDC4', 'ordem': 2},
            {'nome': 'Recursos Humanos', 'descricao': 'Categorias de RH', 'icone': '👥', 'cor': '#45B7D1', 'ordem': 3},
            {'nome': 'Financeiro', 'descricao': 'Categorias financeiras', 'icone': '💰', 'cor': '#96CEB4', 'ordem': 4},
            {'nome': 'Tecnologia', 'descricao': 'Categorias tecnológicas', 'icone': '💻', 'cor': '#FECA57', 'ordem': 5},
        ]
        
        for cat_data in categorias_data:
            categoria, created = CategoriaGlobal.objects.get_or_create(
                nome=cat_data['nome'],
                defaults={
                    'descricao': cat_data['descricao'],
                    'icone': cat_data['icone'],
                    'cor': cat_data['cor'],
                    'ordem': cat_data['ordem'],
                    'criado_por': admin_sistema
                }
            )
            if created:
                self.stdout.write(f'✓ Categoria criada: {categoria.nome}')
        
        # Tipos Globais
        tipos_data = [
            # Eventos
            {'categoria': 'Eventos', 'nome': 'Corporativo', 'descricao': 'Eventos corporativos', 'codigo': 'CORP', 'ordem': 1},
            {'categoria': 'Eventos', 'nome': 'Social', 'descricao': 'Eventos sociais', 'codigo': 'SOC', 'ordem': 2},
            {'categoria': 'Eventos', 'nome': 'Cultural', 'descricao': 'Eventos culturais', 'codigo': 'CULT', 'ordem': 3},
            {'categoria': 'Eventos', 'nome': 'Esportivo', 'descricao': 'Eventos esportivos', 'codigo': 'ESP', 'ordem': 4},
            
            # Equipamentos
            {'categoria': 'Equipamentos', 'nome': 'Som', 'descricao': 'Equipamentos de som', 'codigo': 'SOM', 'ordem': 1},
            {'categoria': 'Equipamentos', 'nome': 'Iluminação', 'descricao': 'Equipamentos de iluminação', 'codigo': 'ILUM', 'ordem': 2},
            {'categoria': 'Equipamentos', 'nome': 'Estrutura', 'descricao': 'Estruturas e palcos', 'codigo': 'ESTR', 'ordem': 3},
        ]
        
        for tipo_data in tipos_data:
            categoria = CategoriaGlobal.objects.get(nome=tipo_data['categoria'])
            tipo, created = TipoGlobal.objects.get_or_create(
                categoria=categoria,
                nome=tipo_data['nome'],
                defaults={
                    'descricao': tipo_data['descricao'],
                    'codigo': tipo_data['codigo'],
                    'ordem': tipo_data['ordem'],
                    'criado_por': admin_sistema
                }
            )
            if created:
                self.stdout.write(f'✓ Tipo criado: {tipo.nome} ({categoria.nome})')
        
        # Classificações Globais
        classificacoes_data = [
            # Níveis de Experiência
            {'tipo': 'experiencia', 'nome': 'Iniciante', 'descricao': '0-2 anos de experiência', 'valor': 1, 'cor': '#FF6B6B'},
            {'tipo': 'experiencia', 'nome': 'Intermediário', 'descricao': '2-5 anos de experiência', 'valor': 2, 'cor': '#4ECDC4'},
            {'tipo': 'experiencia', 'nome': 'Avançado', 'descricao': '5-10 anos de experiência', 'valor': 3, 'cor': '#45B7D1'},
            {'tipo': 'experiencia', 'nome': 'Especialista', 'descricao': '10+ anos de experiência', 'valor': 4, 'cor': '#96CEB4'},
            
            # Prioridades
            {'tipo': 'prioridade', 'nome': 'Baixa', 'descricao': 'Prioridade baixa', 'valor': 1, 'cor': '#96CEB4'},
            {'tipo': 'prioridade', 'nome': 'Média', 'descricao': 'Prioridade média', 'valor': 2, 'cor': '#FECA57'},
            {'tipo': 'prioridade', 'nome': 'Alta', 'descricao': 'Prioridade alta', 'valor': 3, 'cor': '#FF6B6B'},
            {'tipo': 'prioridade', 'nome': 'Crítica', 'descricao': 'Prioridade crítica', 'valor': 4, 'cor': '#FF0000'},
        ]
        
        for class_data in classificacoes_data:
            classificacao, created = ClassificacaoGlobal.objects.get_or_create(
                tipo=class_data['tipo'],
                nome=class_data['nome'],
                defaults={
                    'descricao': class_data['descricao'],
                    'valor': class_data['valor'],
                    'cor': class_data['cor'],
                    'criado_por': admin_sistema
                }
            )
            if created:
                self.stdout.write(f'✓ Classificação criada: {classificacao.nome} ({classificacao.tipo})')
        
        # ============================================================================
        # CONFIGURAÇÕES SISTEMA
        # ============================================================================
        
        # Configurações do Sistema
        configuracoes_data = [
            {'chave': 'SISTEMA_NOME', 'valor': 'Eventix', 'tipo': 'string', 'categoria': 'Sistema', 'descricao': 'Nome do sistema'},
            {'chave': 'SISTEMA_VERSAO', 'valor': '1.0.0', 'tipo': 'string', 'categoria': 'Sistema', 'descricao': 'Versão do sistema'},
            {'chave': 'MAX_EVENTOS_POR_EMPRESA', 'valor': '100', 'tipo': 'integer', 'categoria': 'Limites', 'descricao': 'Máximo de eventos por empresa'},
            {'chave': 'MAX_USUARIOS_POR_EMPRESA', 'valor': '50', 'tipo': 'integer', 'categoria': 'Limites', 'descricao': 'Máximo de usuários por empresa'},
        ]
        
        for config_data in configuracoes_data:
            config, created = ConfiguracaoSistema.objects.get_or_create(
                chave=config_data['chave'],
                defaults={
                    'valor': config_data['valor'],
                    'tipo': config_data['tipo'],
                    'categoria': config_data['categoria'],
                    'descricao': config_data['descricao'],
                    'criado_por': admin_sistema
                }
            )
            if created:
                self.stdout.write(f'✓ Configuração criada: {config.chave}')
        
        # ============================================================================
        # INTEGRAÇÕES
        # ============================================================================
        
        # Integrações Globais
        integracoes_data = [
            {'nome': 'Mercado Pago', 'descricao': 'Integração com Mercado Pago para pagamentos', 'tipo': 'payment', 'url_base': 'https://api.mercadopago.com'},
            {'nome': 'SendGrid', 'descricao': 'Integração com SendGrid para envio de emails', 'tipo': 'email', 'url_base': 'https://api.sendgrid.com'},
            {'nome': 'Twilio', 'descricao': 'Integração com Twilio para envio de SMS', 'tipo': 'sms', 'url_base': 'https://api.twilio.com'},
        ]
        
        for integ_data in integracoes_data:
            integracao, created = IntegracaoGlobal.objects.get_or_create(
                nome=integ_data['nome'],
                defaults={
                    'descricao': integ_data['descricao'],
                    'tipo': integ_data['tipo'],
                    'url_base': integ_data['url_base'],
                    'criado_por': admin_sistema
                }
            )
            if created:
                self.stdout.write(f'✓ Integração criada: {integracao.nome}')
        
        # ============================================================================
        # TEMPLATES
        # ============================================================================
        
        # Templates Globais
        templates_data = [
            {'nome': 'Email Boas-vindas', 'tipo': 'email', 'assunto': 'Bem-vindo ao Eventix!', 'conteudo': 'Olá {{nome}},\n\nBem-vindo ao Eventix! Sua conta foi criada com sucesso.\n\nAtenciosamente,\nEquipe Eventix'},
            {'nome': 'Email Candidatura', 'tipo': 'email', 'assunto': 'Nova candidatura recebida', 'conteudo': 'Olá {{empresa}},\n\nVocê recebeu uma nova candidatura para a vaga: {{vaga}}\n\nCandidato: {{candidato}}\n\nAcesse o sistema para mais detalhes.'},
        ]
        
        for template_data in templates_data:
            template, created = TemplateGlobal.objects.get_or_create(
                nome=template_data['nome'],
                tipo=template_data['tipo'],
                defaults={
                    'assunto': template_data['assunto'],
                    'conteudo': template_data['conteudo'],
                    'variaveis': ['nome', 'empresa', 'vaga', 'candidato'],
                    'criado_por': admin_sistema
                }
            )
            if created:
                self.stdout.write(f'✓ Template criado: {template.nome}')
        
        # ============================================================================
        # MARKETPLACE
        # ============================================================================
        
        # Categorias de Freelancer Globais
        categorias_freelancer_data = [
            {'nome': 'Produção de Eventos', 'descricao': 'Profissionais de produção de eventos', 'icone': '🎬', 'cor': '#FF6B6B'},
            {'nome': 'Técnico de Som', 'descricao': 'Técnicos especializados em som', 'icone': '🎵', 'cor': '#4ECDC4'},
            {'nome': 'Técnico de Iluminação', 'descricao': 'Técnicos especializados em iluminação', 'icone': '💡', 'cor': '#45B7D1'},
        ]
        
        for cat_data in categorias_freelancer_data:
            categoria, created = CategoriaFreelancerGlobal.objects.get_or_create(
                nome=cat_data['nome'],
                defaults={
                    'descricao': cat_data['descricao'],
                    'icone': cat_data['icone'],
                    'cor': cat_data['cor'],
                    'criado_por': admin_sistema
                }
            )
            if created:
                self.stdout.write(f'✓ Categoria de freelancer criada: {categoria.nome}')
        
        # Habilidades Globais
        habilidades_data = [
            # Produção de Eventos
            {'categoria': 'Produção de Eventos', 'nome': 'Coordenação Geral', 'descricao': 'Coordenação geral de eventos', 'nivel_minimo': 'intermediario'},
            {'categoria': 'Produção de Eventos', 'nome': 'Gestão de Equipe', 'descricao': 'Gestão de equipes de produção', 'nivel_minimo': 'avancado'},
            
            # Técnico de Som
            {'categoria': 'Técnico de Som', 'nome': 'Mixagem', 'descricao': 'Mixagem de áudio', 'nivel_minimo': 'avancado'},
            {'categoria': 'Técnico de Som', 'nome': 'Gravação', 'descricao': 'Gravação de áudio', 'nivel_minimo': 'intermediario'},
        ]
        
        for hab_data in habilidades_data:
            categoria = CategoriaFreelancerGlobal.objects.get(nome=hab_data['categoria'])
            habilidade, created = HabilidadeGlobal.objects.get_or_create(
                categoria=categoria,
                nome=hab_data['nome'],
                defaults={
                    'descricao': hab_data['descricao'],
                    'nivel_minimo': hab_data['nivel_minimo'],
                    'criado_por': admin_sistema
                }
            )
            if created:
                self.stdout.write(f'✓ Habilidade criada: {habilidade.nome} ({categoria.nome})')
        
        # Fornecedores Globais
        fornecedores_data = [
            {'nome': 'Equipamentos Pro', 'descricao': 'Fornecedor de equipamentos profissionais', 'website': 'https://equipamentospro.com', 'email': 'contato@equipamentospro.com', 'categoria': 'Equipamentos', 'avaliacao_media': 4.5, 'total_avaliacoes': 120},
            {'nome': 'Som & Luz Ltda', 'descricao': 'Especialista em equipamentos de som e iluminação', 'website': 'https://somaluz.com', 'email': 'vendas@somaluz.com', 'categoria': 'Equipamentos', 'avaliacao_media': 4.8, 'total_avaliacoes': 95},
        ]
        
        for forn_data in fornecedores_data:
            fornecedor, created = FornecedorGlobal.objects.get_or_create(
                nome=forn_data['nome'],
                defaults={
                    'descricao': forn_data['descricao'],
                    'website': forn_data['website'],
                    'email': forn_data['email'],
                    'categoria': forn_data['categoria'],
                    'avaliacao_media': forn_data['avaliacao_media'],
                    'total_avaliacoes': forn_data['total_avaliacoes'],
                    'criado_por': admin_sistema
                }
            )
            if created:
                self.stdout.write(f'✓ Fornecedor criado: {fornecedor.nome}')
        
        self.stdout.write(
            self.style.SUCCESS('✓ Modelos globais populados com sucesso!')
        )
