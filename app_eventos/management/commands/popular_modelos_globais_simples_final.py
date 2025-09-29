"""
Comando final para popular modelos globais
"""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Popula modelos globais - versão final'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando populacao dos modelos globais...')
        
        with connection.cursor() as cursor:
            # Verificar quais tabelas existem
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE 'app_eventos_%global%'
                ORDER BY table_name
            """)
            tabelas_existentes = [row[0] for row in cursor.fetchall()]
            
            self.stdout.write(f'Tabelas globais encontradas: {len(tabelas_existentes)}')
            
            # ============================================================================
            # CATÁLOGOS GERAIS
            # ============================================================================
            
            if 'app_eventos_categoriaglobal' in tabelas_existentes:
                cursor.execute("SELECT COUNT(*) FROM app_eventos_categoriaglobal")
                categorias_count = cursor.fetchone()[0]
                
                if categorias_count == 0:
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
                        self.stdout.write(f'[OK] Categoria criada: {nome}')
                else:
                    self.stdout.write('[OK] Categorias globais ja existem')
            
            if 'app_eventos_tipoglobal' in tabelas_existentes:
                cursor.execute("SELECT COUNT(*) FROM app_eventos_tipoglobal")
                tipos_count = cursor.fetchone()[0]
                
                if tipos_count == 0:
                    tipos_data = [
                        (1, 'Corporativo', 'Eventos corporativos', 'CORP', 1),
                        (1, 'Social', 'Eventos sociais', 'SOC', 2),
                        (1, 'Cultural', 'Eventos culturais', 'CULT', 3),
                        (1, 'Esportivo', 'Eventos esportivos', 'ESP', 4),
                        (2, 'Som', 'Equipamentos de som', 'SOM', 1),
                        (2, 'Iluminacao', 'Equipamentos de iluminacao', 'ILUM', 2),
                        (2, 'Estrutura', 'Estruturas e palcos', 'ESTR', 3),
                    ]
                    
                    for categoria_id, nome, descricao, codigo, ordem in tipos_data:
                        cursor.execute("""
                            INSERT INTO app_eventos_tipoglobal 
                            (categoria_id, nome, descricao, codigo, ordem, ativo, data_criacao, data_atualizacao, criado_por_id)
                            VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW(), 1)
                        """, [categoria_id, nome, descricao, codigo, ordem, True])
                        self.stdout.write(f'[OK] Tipo criado: {nome}')
                else:
                    self.stdout.write('[OK] Tipos globais ja existem')
            
            if 'app_eventos_classificacaoglobal' in tabelas_existentes:
                cursor.execute("SELECT COUNT(*) FROM app_eventos_classificacaoglobal")
                classificacoes_count = cursor.fetchone()[0]
                
                if classificacoes_count == 0:
                    classificacoes_data = [
                        ('experiencia', 'Iniciante', '0-2 anos de experiencia', 1, '#FF6B6B'),
                        ('experiencia', 'Intermediario', '2-5 anos de experiencia', 2, '#4ECDC4'),
                        ('experiencia', 'Avancado', '5-10 anos de experiencia', 3, '#45B7D1'),
                        ('experiencia', 'Especialista', '10+ anos de experiencia', 4, '#96CEB4'),
                        ('prioridade', 'Baixa', 'Prioridade baixa', 1, '#96CEB4'),
                        ('prioridade', 'Media', 'Prioridade media', 2, '#FECA57'),
                        ('prioridade', 'Alta', 'Prioridade alta', 3, '#FF6B6B'),
                        ('prioridade', 'Critica', 'Prioridade critica', 4, '#FF0000'),
                    ]
                    
                    for tipo, nome, descricao, valor, cor in classificacoes_data:
                        cursor.execute("""
                            INSERT INTO app_eventos_classificacaoglobal 
                            (tipo, nome, descricao, valor, cor, ativo, data_criacao, data_atualizacao, criado_por_id)
                            VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW(), 1)
                        """, [tipo, nome, descricao, valor, cor, True])
                        self.stdout.write(f'[OK] Classificacao criada: {nome} ({tipo})')
                else:
                    self.stdout.write('[OK] Classificacoes globais ja existem')
            
            # ============================================================================
            # CONFIGURAÇÕES SISTEMA
            # ============================================================================
            
            if 'app_eventos_configuracaosistema' in tabelas_existentes:
                cursor.execute("SELECT COUNT(*) FROM app_eventos_configuracaosistema")
                configs_count = cursor.fetchone()[0]
                
                if configs_count == 0:
                    configuracoes_data = [
                        ('SISTEMA_NOME', 'Eventix', 'string', 'Sistema', 'Nome do sistema'),
                        ('SISTEMA_VERSAO', '1.0.0', 'string', 'Sistema', 'Versao do sistema'),
                        ('MAX_EVENTOS_POR_EMPRESA', '100', 'integer', 'Limites', 'Maximo de eventos por empresa'),
                        ('MAX_USUARIOS_POR_EMPRESA', '50', 'integer', 'Limites', 'Maximo de usuarios por empresa'),
                    ]
                    
                    for chave, valor, tipo, categoria, descricao in configuracoes_data:
                        cursor.execute("""
                            INSERT INTO app_eventos_configuracaosistema 
                            (chave, valor, tipo, categoria, descricao, ativo, data_criacao, data_atualizacao, criado_por_id)
                            VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW(), 1)
                        """, [chave, valor, tipo, categoria, descricao, True])
                        self.stdout.write(f'[OK] Configuracao criada: {chave}')
                else:
                    self.stdout.write('[OK] Configuracoes do sistema ja existem')
            
            # ============================================================================
            # INTEGRAÇÕES
            # ============================================================================
            
            if 'app_eventos_integracaoglobal' in tabelas_existentes:
                cursor.execute("SELECT COUNT(*) FROM app_eventos_integracaoglobal")
                integracoes_count = cursor.fetchone()[0]
                
                if integracoes_count == 0:
                    integracoes_data = [
                        ('Mercado Pago', 'Integracao com Mercado Pago para pagamentos', 'payment', 'https://api.mercadopago.com'),
                        ('SendGrid', 'Integracao com SendGrid para envio de emails', 'email', 'https://api.sendgrid.com'),
                        ('Twilio', 'Integracao com Twilio para envio de SMS', 'sms', 'https://api.twilio.com'),
                    ]
                    
                    for nome, descricao, tipo, url_base in integracoes_data:
                        cursor.execute("""
                            INSERT INTO app_eventos_integracaoglobal 
                            (nome, descricao, tipo, url_base, ativo, data_criacao, data_atualizacao, criado_por_id)
                            VALUES (%s, %s, %s, %s, %s, NOW(), NOW(), 1)
                        """, [nome, descricao, tipo, url_base, True])
                        self.stdout.write(f'[OK] Integracao criada: {nome}')
                else:
                    self.stdout.write('[OK] Integracoes globais ja existem')
            
            # ============================================================================
            # TEMPLATES
            # ============================================================================
            
            if 'app_eventos_templateglobal' in tabelas_existentes:
                cursor.execute("SELECT COUNT(*) FROM app_eventos_templateglobal")
                templates_count = cursor.fetchone()[0]
                
                if templates_count == 0:
                    templates_data = [
                        ('Email Boas-vindas', 'email', 'Bem-vindo ao Eventix!', 'Ola {{nome}},\n\nBem-vindo ao Eventix! Sua conta foi criada com sucesso.\n\nAtenciosamente,\nEquipe Eventix'),
                        ('Email Candidatura', 'email', 'Nova candidatura recebida', 'Ola {{empresa}},\n\nVoce recebeu uma nova candidatura para a vaga: {{vaga}}\n\nCandidato: {{candidato}}\n\nAcesse o sistema para mais detalhes.'),
                    ]
                    
                    for nome, tipo, assunto, conteudo in templates_data:
                        cursor.execute("""
                            INSERT INTO app_eventos_templateglobal 
                            (nome, tipo, assunto, conteudo, variaveis, ativo, data_criacao, data_atualizacao, criado_por_id)
                            VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW(), 1)
                        """, [nome, tipo, assunto, conteudo, '["nome", "empresa", "vaga", "candidato"]', True])
                        self.stdout.write(f'[OK] Template criado: {nome}')
                else:
                    self.stdout.write('[OK] Templates globais ja existem')
            
            # ============================================================================
            # MARKETPLACE
            # ============================================================================
            
            if 'app_eventos_categoriafreelancerglobal' in tabelas_existentes:
                cursor.execute("SELECT COUNT(*) FROM app_eventos_categoriafreelancerglobal")
                cat_freelancer_count = cursor.fetchone()[0]
                
                if cat_freelancer_count == 0:
                    categorias_freelancer_data = [
                        ('Producao de Eventos', 'Profissionais de producao de eventos', '🎬', '#FF6B6B'),
                        ('Tecnico de Som', 'Tecnicos especializados em som', '🎵', '#4ECDC4'),
                        ('Tecnico de Iluminacao', 'Tecnicos especializados em iluminacao', '💡', '#45B7D1'),
                    ]
                    
                    for nome, descricao, icone, cor in categorias_freelancer_data:
                        cursor.execute("""
                            INSERT INTO app_eventos_categoriafreelancerglobal 
                            (nome, descricao, icone, cor, ativo, data_criacao, data_atualizacao, criado_por_id)
                            VALUES (%s, %s, %s, %s, %s, NOW(), NOW(), 1)
                        """, [nome, descricao, icone, cor, True])
                        self.stdout.write(f'[OK] Categoria de freelancer criada: {nome}')
                else:
                    self.stdout.write('[OK] Categorias de freelancer globais ja existem')
            
            if 'app_eventos_habilidadeglobal' in tabelas_existentes:
                cursor.execute("SELECT COUNT(*) FROM app_eventos_habilidadeglobal")
                habilidades_count = cursor.fetchone()[0]
                
                if habilidades_count == 0:
                    habilidades_data = [
                        (1, 'Coordenacao Geral', 'Coordenacao geral de eventos', 'intermediario'),
                        (1, 'Gestao de Equipe', 'Gestao de equipes de producao', 'avancado'),
                        (2, 'Mixagem', 'Mixagem de audio', 'avancado'),
                        (2, 'Gravacao', 'Gravacao de audio', 'intermediario'),
                    ]
                    
                    for categoria_id, nome, descricao, nivel_minimo in habilidades_data:
                        cursor.execute("""
                            INSERT INTO app_eventos_habilidadeglobal 
                            (categoria_id, nome, descricao, nivel_minimo, ativo, data_criacao, data_atualizacao, criado_por_id)
                            VALUES (%s, %s, %s, %s, %s, NOW(), NOW(), 1)
                        """, [categoria_id, nome, descricao, nivel_minimo, True])
                        self.stdout.write(f'[OK] Habilidade criada: {nome}')
                else:
                    self.stdout.write('[OK] Habilidades globais ja existem')
            
            if 'app_eventos_fornecedorglobal' in tabelas_existentes:
                cursor.execute("SELECT COUNT(*) FROM app_eventos_fornecedorglobal")
                fornecedores_count = cursor.fetchone()[0]
                
                if fornecedores_count == 0:
                    fornecedores_data = [
                        ('Equipamentos Pro', 'Fornecedor de equipamentos profissionais', 'https://equipamentospro.com', 'contato@equipamentospro.com', 'Equipamentos', 4.5, 120),
                        ('Som & Luz Ltda', 'Especialista em equipamentos de som e iluminacao', 'https://somaluz.com', 'vendas@somaluz.com', 'Equipamentos', 4.8, 95),
                    ]
                    
                    for nome, descricao, website, email, categoria, avaliacao_media, total_avaliacoes in fornecedores_data:
                        cursor.execute("""
                            INSERT INTO app_eventos_fornecedorglobal 
                            (nome, descricao, website, email, categoria, avaliacao_media, total_avaliacoes, ativo, data_criacao, data_atualizacao, criado_por_id)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), 1)
                        """, [nome, descricao, website, email, categoria, avaliacao_media, total_avaliacoes, True])
                        self.stdout.write(f'[OK] Fornecedor criado: {nome}')
                else:
                    self.stdout.write('[OK] Fornecedores globais ja existem')
        
        self.stdout.write(
            self.style.SUCCESS('[SUCCESS] Populacao dos modelos globais concluida!')
        )
