"""
Comando para popular modelos globais usando SQL direto
"""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Popula modelos globais com dados iniciais usando SQL direto'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando população dos modelos globais...')
        
        with connection.cursor() as cursor:
            # Verificar se já existem dados
            cursor.execute("SELECT COUNT(*) FROM app_eventos_categoriaglobal")
            categorias_count = cursor.fetchone()[0]
            
            if categorias_count > 0:
                self.stdout.write('Modelos globais já populados. Pulando...')
                return
            
            # ============================================================================
            # CATÁLOGOS GERAIS
            # ============================================================================
            
            # Categorias Globais
            categorias_data = [
                ('Eventos', 'Categorias relacionadas a eventos', '🎉', '#FF6B6B', 1),
                ('Equipamentos', 'Categorias de equipamentos', '🔧', '#4ECDC4', 2),
                ('Recursos Humanos', 'Categorias de RH', '👥', '#45B7D1', 3),
                ('Financeiro', 'Categorias financeiras', '💰', '#96CEB4', 4),
                ('Tecnologia', 'Categorias tecnológicas', '💻', '#FECA57', 5),
            ]
            
            for nome, descricao, icone, cor, ordem in categorias_data:
                cursor.execute("""
                    INSERT INTO app_eventos_categoriaglobal 
                    (nome, descricao, icone, cor, ordem, ativo, data_criacao, data_atualizacao, criado_por_id)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW(), 1)
                """, [nome, descricao, icone, cor, ordem, True])
                self.stdout.write(f'✓ Categoria criada: {nome}')
            
            # Tipos Globais
            tipos_data = [
                # Eventos
                (1, 'Corporativo', 'Eventos corporativos', 'CORP', 1),
                (1, 'Social', 'Eventos sociais', 'SOC', 2),
                (1, 'Cultural', 'Eventos culturais', 'CULT', 3),
                (1, 'Esportivo', 'Eventos esportivos', 'ESP', 4),
                
                # Equipamentos
                (2, 'Som', 'Equipamentos de som', 'SOM', 1),
                (2, 'Iluminação', 'Equipamentos de iluminação', 'ILUM', 2),
                (2, 'Estrutura', 'Estruturas e palcos', 'ESTR', 3),
            ]
            
            for categoria_id, nome, descricao, codigo, ordem in tipos_data:
                cursor.execute("""
                    INSERT INTO app_eventos_tipoglobal 
                    (categoria_id, nome, descricao, codigo, ordem, ativo, data_criacao, data_atualizacao, criado_por_id)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW(), 1)
                """, [categoria_id, nome, descricao, codigo, ordem, True])
                self.stdout.write(f'✓ Tipo criado: {nome}')
            
            # Classificações Globais
            classificacoes_data = [
                # Níveis de Experiência
                ('experiencia', 'Iniciante', '0-2 anos de experiência', 1, '#FF6B6B'),
                ('experiencia', 'Intermediário', '2-5 anos de experiência', 2, '#4ECDC4'),
                ('experiencia', 'Avançado', '5-10 anos de experiência', 3, '#45B7D1'),
                ('experiencia', 'Especialista', '10+ anos de experiência', 4, '#96CEB4'),
                
                # Prioridades
                ('prioridade', 'Baixa', 'Prioridade baixa', 1, '#96CEB4'),
                ('prioridade', 'Média', 'Prioridade média', 2, '#FECA57'),
                ('prioridade', 'Alta', 'Prioridade alta', 3, '#FF6B6B'),
                ('prioridade', 'Crítica', 'Prioridade crítica', 4, '#FF0000'),
            ]
            
            for tipo, nome, descricao, valor, cor in classificacoes_data:
                cursor.execute("""
                    INSERT INTO app_eventos_classificacaoglobal 
                    (tipo, nome, descricao, valor, cor, ativo, data_criacao, data_atualizacao, criado_por_id)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW(), 1)
                """, [tipo, nome, descricao, valor, cor, True])
                self.stdout.write(f'✓ Classificação criada: {nome} ({tipo})')
            
            # ============================================================================
            # CONFIGURAÇÕES SISTEMA
            # ============================================================================
            
            # Configurações do Sistema
            configuracoes_data = [
                ('SISTEMA_NOME', 'Eventix', 'string', 'Sistema', 'Nome do sistema'),
                ('SISTEMA_VERSAO', '1.0.0', 'string', 'Sistema', 'Versão do sistema'),
                ('MAX_EVENTOS_POR_EMPRESA', '100', 'integer', 'Limites', 'Máximo de eventos por empresa'),
                ('MAX_USUARIOS_POR_EMPRESA', '50', 'integer', 'Limites', 'Máximo de usuários por empresa'),
            ]
            
            for chave, valor, tipo, categoria, descricao in configuracoes_data:
                cursor.execute("""
                    INSERT INTO app_eventos_configuracaosistema 
                    (chave, valor, tipo, categoria, descricao, ativo, data_criacao, data_atualizacao, criado_por_id)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW(), 1)
                """, [chave, valor, tipo, categoria, descricao, True])
                self.stdout.write(f'✓ Configuração criada: {chave}')
            
            # ============================================================================
            # INTEGRAÇÕES
            # ============================================================================
            
            # Integrações Globais
            integracoes_data = [
                ('Mercado Pago', 'Integração com Mercado Pago para pagamentos', 'payment', 'https://api.mercadopago.com'),
                ('SendGrid', 'Integração com SendGrid para envio de emails', 'email', 'https://api.sendgrid.com'),
                ('Twilio', 'Integração com Twilio para envio de SMS', 'sms', 'https://api.twilio.com'),
            ]
            
            for nome, descricao, tipo, url_base in integracoes_data:
                cursor.execute("""
                    INSERT INTO app_eventos_integracoesglobal 
                    (nome, descricao, tipo, url_base, ativo, data_criacao, data_atualizacao, criado_por_id)
                    VALUES (%s, %s, %s, %s, %s, NOW(), NOW(), 1)
                """, [nome, descricao, tipo, url_base, True])
                self.stdout.write(f'✓ Integração criada: {nome}')
            
            # ============================================================================
            # TEMPLATES
            # ============================================================================
            
            # Templates Globais
            templates_data = [
                ('Email Boas-vindas', 'email', 'Bem-vindo ao Eventix!', 'Olá {{nome}},\n\nBem-vindo ao Eventix! Sua conta foi criada com sucesso.\n\nAtenciosamente,\nEquipe Eventix'),
                ('Email Candidatura', 'email', 'Nova candidatura recebida', 'Olá {{empresa}},\n\nVocê recebeu uma nova candidatura para a vaga: {{vaga}}\n\nCandidato: {{candidato}}\n\nAcesse o sistema para mais detalhes.'),
            ]
            
            for nome, tipo, assunto, conteudo in templates_data:
                cursor.execute("""
                    INSERT INTO app_eventos_templateglobal 
                    (nome, tipo, assunto, conteudo, variaveis, ativo, data_criacao, data_atualizacao, criado_por_id)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW(), 1)
                """, [nome, tipo, assunto, conteudo, '["nome", "empresa", "vaga", "candidato"]', True])
                self.stdout.write(f'✓ Template criado: {nome}')
            
            # ============================================================================
            # MARKETPLACE
            # ============================================================================
            
            # Categorias de Freelancer Globais
            categorias_freelancer_data = [
                ('Produção de Eventos', 'Profissionais de produção de eventos', '🎬', '#FF6B6B'),
                ('Técnico de Som', 'Técnicos especializados em som', '🎵', '#4ECDC4'),
                ('Técnico de Iluminação', 'Técnicos especializados em iluminação', '💡', '#45B7D1'),
            ]
            
            for nome, descricao, icone, cor in categorias_freelancer_data:
                cursor.execute("""
                    INSERT INTO app_eventos_categoriafreelancerglobal 
                    (nome, descricao, icone, cor, ativo, data_criacao, data_atualizacao, criado_por_id)
                    VALUES (%s, %s, %s, %s, %s, NOW(), NOW(), 1)
                """, [nome, descricao, icone, cor, True])
                self.stdout.write(f'✓ Categoria de freelancer criada: {nome}')
            
            # Habilidades Globais
            habilidades_data = [
                # Produção de Eventos
                (1, 'Coordenação Geral', 'Coordenação geral de eventos', 'intermediario'),
                (1, 'Gestão de Equipe', 'Gestão de equipes de produção', 'avancado'),
                
                # Técnico de Som
                (2, 'Mixagem', 'Mixagem de áudio', 'avancado'),
                (2, 'Gravação', 'Gravação de áudio', 'intermediario'),
            ]
            
            for categoria_id, nome, descricao, nivel_minimo in habilidades_data:
                cursor.execute("""
                    INSERT INTO app_eventos_habilidadeglobal 
                    (categoria_id, nome, descricao, nivel_minimo, ativo, data_criacao, data_atualizacao, criado_por_id)
                    VALUES (%s, %s, %s, %s, %s, NOW(), NOW(), 1)
                """, [categoria_id, nome, descricao, nivel_minimo, True])
                self.stdout.write(f'✓ Habilidade criada: {nome}')
            
            # Fornecedores Globais
            fornecedores_data = [
                ('Equipamentos Pro', 'Fornecedor de equipamentos profissionais', 'https://equipamentospro.com', 'contato@equipamentospro.com', 'Equipamentos', 4.5, 120),
                ('Som & Luz Ltda', 'Especialista em equipamentos de som e iluminação', 'https://somaluz.com', 'vendas@somaluz.com', 'Equipamentos', 4.8, 95),
            ]
            
            for nome, descricao, website, email, categoria, avaliacao_media, total_avaliacoes in fornecedores_data:
                cursor.execute("""
                    INSERT INTO app_eventos_fornecedorglobal 
                    (nome, descricao, website, email, categoria, avaliacao_media, total_avaliacoes, ativo, data_criacao, data_atualizacao, criado_por_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), 1)
                """, [nome, descricao, website, email, categoria, avaliacao_media, total_avaliacoes, True])
                self.stdout.write(f'✓ Fornecedor criado: {nome}')
        
        self.stdout.write(
            self.style.SUCCESS('✓ Modelos globais populados com sucesso!')
        )
