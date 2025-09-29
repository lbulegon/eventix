"""
Comando para popular modelos globais com dados iniciais
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
    help = 'Popula modelos globais com dados iniciais'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando população dos modelos globais...')
        
        # Buscar ou criar admin do sistema
        admin_sistema = User.objects.filter(tipo_usuario='admin_sistema').first()
        if not admin_sistema:
            self.stdout.write(
                self.style.WARNING('Nenhum administrador do sistema encontrado. Criando um...')
            )
            admin_sistema = User.objects.create_user(
                username='admin_sistema',
                email='admin@sistema.com',
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
            
            # Recursos Humanos
            {'categoria': 'Recursos Humanos', 'nome': 'Produção', 'descricao': 'Profissionais de produção', 'codigo': 'PROD', 'ordem': 1},
            {'categoria': 'Recursos Humanos', 'nome': 'Técnico', 'descricao': 'Profissionais técnicos', 'codigo': 'TEC', 'ordem': 2},
            {'categoria': 'Recursos Humanos', 'nome': 'Operacional', 'descricao': 'Profissionais operacionais', 'codigo': 'OP', 'ordem': 3},
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
            
            # Status
            {'tipo': 'status', 'nome': 'Ativo', 'descricao': 'Status ativo', 'valor': 1, 'cor': '#96CEB4'},
            {'tipo': 'status', 'nome': 'Inativo', 'descricao': 'Status inativo', 'valor': 0, 'cor': '#FF6B6B'},
            {'tipo': 'status', 'nome': 'Pendente', 'descricao': 'Status pendente', 'valor': 2, 'cor': '#FECA57'},
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
            {'chave': 'BACKUP_AUTOMATICO', 'valor': 'true', 'tipo': 'boolean', 'categoria': 'Backup', 'descricao': 'Backup automático ativo'},
            {'chave': 'NOTIFICACOES_EMAIL', 'valor': 'true', 'tipo': 'boolean', 'categoria': 'Notificações', 'descricao': 'Notificações por email ativas'},
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
        
        # Parâmetros do Sistema
        parametros_data = [
            {'nome': 'TIMEOUT_API', 'valor_padrao': '30', 'valor_atual': '30', 'tipo': 'integer', 'categoria': 'API', 'descricao': 'Timeout para chamadas de API (segundos)'},
            {'nome': 'TAMANHO_MAX_UPLOAD', 'valor_padrao': '10485760', 'valor_atual': '10485760', 'tipo': 'integer', 'categoria': 'Upload', 'descricao': 'Tamanho máximo para upload (bytes)'},
            {'nome': 'DIAS_RETENCAO_LOG', 'valor_padrao': '90', 'valor_atual': '90', 'tipo': 'integer', 'categoria': 'Logs', 'descricao': 'Dias de retenção de logs'},
        ]
        
        for param_data in parametros_data:
            param, created = ParametroSistema.objects.get_or_create(
                nome=param_data['nome'],
                defaults={
                    'valor_padrao': param_data['valor_padrao'],
                    'valor_atual': param_data['valor_atual'],
                    'tipo': param_data['tipo'],
                    'categoria': param_data['categoria'],
                    'descricao': param_data['descricao'],
                    'criado_por': admin_sistema
                }
            )
            if created:
                self.stdout.write(f'✓ Parâmetro criado: {param.nome}')
        
        # ============================================================================
        # INTEGRAÇÕES
        # ============================================================================
        
        # Integrações Globais
        integracoes_data = [
            {'nome': 'Mercado Pago', 'descricao': 'Integração com Mercado Pago para pagamentos', 'tipo': 'payment', 'url_base': 'https://api.mercadopago.com', 'documentacao': 'https://developers.mercadopago.com'},
            {'nome': 'SendGrid', 'descricao': 'Integração com SendGrid para envio de emails', 'tipo': 'email', 'url_base': 'https://api.sendgrid.com', 'documentacao': 'https://docs.sendgrid.com'},
            {'nome': 'Twilio', 'descricao': 'Integração com Twilio para envio de SMS', 'tipo': 'sms', 'url_base': 'https://api.twilio.com', 'documentacao': 'https://www.twilio.com/docs'},
            {'nome': 'Google Maps', 'descricao': 'Integração com Google Maps para geolocalização', 'tipo': 'api', 'url_base': 'https://maps.googleapis.com', 'documentacao': 'https://developers.google.com/maps'},
        ]
        
        for integ_data in integracoes_data:
            integracao, created = IntegracaoGlobal.objects.get_or_create(
                nome=integ_data['nome'],
                defaults={
                    'descricao': integ_data['descricao'],
                    'tipo': integ_data['tipo'],
                    'url_base': integ_data['url_base'],
                    'documentacao': integ_data['documentacao'],
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
            {'nome': 'Contrato Freelancer', 'tipo': 'contrato', 'assunto': None, 'conteudo': 'CONTRATO DE PRESTAÇÃO DE SERVIÇOS\n\nContratante: {{empresa}}\nContratado: {{freelancer}}\n\nServiços: {{servicos}}\nValor: {{valor}}\n\nData: {{data}}'},
        ]
        
        for template_data in templates_data:
            template, created = TemplateGlobal.objects.get_or_create(
                nome=template_data['nome'],
                tipo=template_data['tipo'],
                defaults={
                    'assunto': template_data['assunto'],
                    'conteudo': template_data['conteudo'],
                    'variaveis': ['nome', 'empresa', 'vaga', 'candidato', 'freelancer', 'servicos', 'valor', 'data'],
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
            {'nome': 'Segurança', 'descricao': 'Profissionais de segurança', 'icone': '🛡️', 'cor': '#96CEB4'},
            {'nome': 'Recepção', 'descricao': 'Profissionais de recepção e atendimento', 'icone': '👋', 'cor': '#FECA57'},
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
            {'categoria': 'Produção de Eventos', 'nome': 'Planejamento', 'descricao': 'Planejamento de eventos', 'nivel_minimo': 'intermediario'},
            
            # Técnico de Som
            {'categoria': 'Técnico de Som', 'nome': 'Mixagem', 'descricao': 'Mixagem de áudio', 'nivel_minimo': 'avancado'},
            {'categoria': 'Técnico de Som', 'nome': 'Gravação', 'descricao': 'Gravação de áudio', 'nivel_minimo': 'intermediario'},
            {'categoria': 'Técnico de Som', 'nome': 'Configuração de Equipamentos', 'descricao': 'Configuração de equipamentos de som', 'nivel_minimo': 'intermediario'},
            
            # Técnico de Iluminação
            {'categoria': 'Técnico de Iluminação', 'nome': 'Design de Iluminação', 'descricao': 'Design de iluminação para eventos', 'nivel_minimo': 'avancado'},
            {'categoria': 'Técnico de Iluminação', 'nome': 'Operação de Consoles', 'descricao': 'Operação de consoles de iluminação', 'nivel_minimo': 'intermediario'},
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
            {'nome': 'Estruturas Eventos', 'descricao': 'Fornecedor de estruturas e palcos', 'website': 'https://estruturaseventos.com', 'email': 'orcamento@estruturaseventos.com', 'categoria': 'Estruturas', 'avaliacao_media': 4.2, 'total_avaliacoes': 78},
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
