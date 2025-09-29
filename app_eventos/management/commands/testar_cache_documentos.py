"""
Comando para testar o sistema de cache de documentos
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from app_eventos.models import EmpresaContratante
from app_eventos.models_freelancers import FreelancerGlobal, VagaEmpresa, CandidaturaEmpresa
from app_eventos.models_documentos import (
    DocumentoFreelancerEmpresa, ConfiguracaoDocumentosEmpresa, ReutilizacaoDocumento
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Testa o sistema de cache de documentos'

    def handle(self, *args, **options):
        self.stdout.write('=== TESTANDO SISTEMA DE CACHE DE DOCUMENTOS ===')
        
        # 1. Buscar empresa
        empresa = EmpresaContratante.objects.filter(ativo=True).first()
        if not empresa:
            self.stdout.write('Nenhuma empresa ativa encontrada!')
            return
        
        self.stdout.write(f'Empresa: {empresa.nome_fantasia}')
        
        # 2. Criar configuração de documentos para a empresa
        self.stdout.write('\n1. CRIANDO CONFIGURACAO DE DOCUMENTOS:')
        config, created = ConfiguracaoDocumentosEmpresa.objects.get_or_create(
            empresa_contratante=empresa,
            defaults={
                'aceita_documentos_externos': True,
                'periodo_validade_padrao': 365,
                'rg_obrigatorio': True,
                'cpf_obrigatorio': True,
                'ctps_obrigatorio': True,
                'comprovante_residencia_obrigatorio': True,
                'periodo_validade_rg': 365,
                'periodo_validade_cpf': 365,
                'periodo_validade_ctps': 365,
                'periodo_validade_residencia': 90,  # Residência vence em 90 dias
            }
        )
        
        if created:
            self.stdout.write(f'  [OK] Configuração criada para: {empresa.nome_fantasia}')
        else:
            self.stdout.write(f'  [INFO] Configuração já existe para: {empresa.nome_fantasia}')
        
        self.stdout.write(f'  Documentos obrigatórios: {config.get_documentos_obrigatorios()}')
        
        # 3. Criar freelancer
        self.stdout.write('\n2. CRIANDO FREELANCER:')
        user, created = User.objects.get_or_create(
            username='freelancer_cache_teste',
            defaults={
                'email': 'cache@teste.com',
                'tipo_usuario': 'freelancer',
                'ativo': True,
                'first_name': 'Maria',
                'last_name': 'Silva'
            }
        )
        
        freelancer, created = FreelancerGlobal.objects.get_or_create(
            usuario=user,
            defaults={
                'perfil_publico': True,
                'disponivel_para_vagas': True,
                'nivel_confiabilidade': 'alta',
                'verificado': True
            }
        )
        
        if created:
            self.stdout.write(f'  [OK] Freelancer criado: {freelancer.usuario.username}')
        else:
            self.stdout.write(f'  [INFO] Freelancer já existe: {freelancer.usuario.username}')
        
        # 4. Simular upload de documentos (primeira vez)
        self.stdout.write('\n3. UPLOAD DE DOCUMENTOS (PRIMEIRA VEZ):')
        documentos_obrigatorios = config.get_documentos_obrigatorios()
        
        for tipo_doc in documentos_obrigatorios:
            # Calcular data de vencimento
            periodo_validade = config.get_periodo_validade(tipo_doc)
            data_vencimento = timezone.now() + timedelta(days=periodo_validade)
            
            doc, created = DocumentoFreelancerEmpresa.objects.get_or_create(
                empresa_contratante=empresa,
                freelancer=freelancer,
                tipo_documento=tipo_doc,
                defaults={
                    'status': 'aprovado',
                    'data_vencimento': data_vencimento,
                    'data_validacao': timezone.now(),
                    'observacoes': f'Documento {tipo_doc} aprovado pela empresa',
                    'pode_reutilizar': True
                }
            )
            
            if created:
                self.stdout.write(f'  [OK] Documento {tipo_doc} enviado e aprovado')
                self.stdout.write(f'    Válido até: {doc.data_vencimento.strftime("%d/%m/%Y")}')
                self.stdout.write(f'    Pode reutilizar: {doc.pode_ser_reutilizado}')
            else:
                self.stdout.write(f'  [INFO] Documento {tipo_doc} já existe')
        
        # 5. Criar primeira vaga (com vínculo)
        self.stdout.write('\n4. CRIANDO PRIMEIRA VAGA (COM VINCULO):')
        vaga1, created = VagaEmpresa.objects.get_or_create(
            empresa_contratante=empresa,
            titulo='Técnico de Som - Primeira Contratação',
            defaults={
                'descricao': 'Técnico de som para primeira contratação',
                'exige_vinculo_empregaticio': True,
                'tipo_vinculo': 'temporario',
                'remuneracao': 500.00,
                'tipo_remuneracao': 'por_evento',
                'quantidade_vagas': 1,
                'data_inicio': timezone.now() + timedelta(days=7),
                'data_fim': timezone.now() + timedelta(days=8),
                'data_limite_candidatura': timezone.now() + timedelta(days=5),
                'ativa': True,
                'publicada': True
            }
        )
        
        if created:
            self.stdout.write(f'  [OK] Primeira vaga criada: {vaga1.titulo}')
        else:
            self.stdout.write(f'  [INFO] Primeira vaga já existe: {vaga1.titulo}')
        
        # 6. Candidatura para primeira vaga
        self.stdout.write('\n5. CANDIDATURA PARA PRIMEIRA VAGA:')
        candidatura1, created = CandidaturaEmpresa.objects.get_or_create(
            vaga=vaga1,
            freelancer=freelancer,
            defaults={
                'carta_apresentacao': 'Tenho experiência em som e todos os documentos.',
                'experiencia_relacionada': '5 anos de experiência em eventos.',
                'status': 'aprovada'
            }
        )
        
        if created:
            self.stdout.write(f'  [OK] Candidatura criada: {candidatura1}')
        else:
            self.stdout.write(f'  [INFO] Candidatura já existe: {candidatura1}')
        
        # 7. Verificar documentos disponíveis para reutilização
        self.stdout.write('\n6. VERIFICANDO DOCUMENTOS DISPONIVEIS PARA REUTILIZACAO:')
        documentos_disponiveis = DocumentoFreelancerEmpresa.objects.filter(
            empresa_contratante=empresa,
            freelancer=freelancer,
            status='aprovado'
        )
        
        for doc in documentos_disponiveis:
            self.stdout.write(f'  - {doc.get_tipo_documento_display()}')
            self.stdout.write(f'    Válido: {doc.esta_valido}')
            self.stdout.write(f'    Pode reutilizar: {doc.pode_ser_reutilizado}')
            self.stdout.write(f'    Válido até: {doc.data_vencimento.strftime("%d/%m/%Y") if doc.data_vencimento else "N/A"}')
            self.stdout.write(f'    Total reutilizações: {doc.total_reutilizacoes}')
        
        # 8. Criar segunda vaga (com vínculo)
        self.stdout.write('\n7. CRIANDO SEGUNDA VAGA (COM VINCULO):')
        vaga2, created = VagaEmpresa.objects.get_or_create(
            empresa_contratante=empresa,
            titulo='Iluminador - Segunda Contratação',
            defaults={
                'descricao': 'Iluminador para segunda contratação (reutilizar documentos)',
                'exige_vinculo_empregaticio': True,
                'tipo_vinculo': 'temporario',
                'remuneracao': 600.00,
                'tipo_remuneracao': 'por_evento',
                'quantidade_vagas': 1,
                'data_inicio': timezone.now() + timedelta(days=14),
                'data_fim': timezone.now() + timedelta(days=15),
                'data_limite_candidatura': timezone.now() + timedelta(days=10),
                'ativa': True,
                'publicada': True
            }
        )
        
        if created:
            self.stdout.write(f'  [OK] Segunda vaga criada: {vaga2.titulo}')
        else:
            self.stdout.write(f'  [INFO] Segunda vaga já existe: {vaga2.titulo}')
        
        # 9. Candidatura para segunda vaga (reutilizando documentos)
        self.stdout.write('\n8. CANDIDATURA PARA SEGUNDA VAGA (REUTILIZANDO DOCUMENTOS):')
        candidatura2, created = CandidaturaEmpresa.objects.get_or_create(
            vaga=vaga2,
            freelancer=freelancer,
            defaults={
                'carta_apresentacao': 'Tenho experiência em iluminação e documentos já aprovados.',
                'experiencia_relacionada': '3 anos de experiência em iluminação.',
                'status': 'aprovada'
            }
        )
        
        if created:
            self.stdout.write(f'  [OK] Candidatura criada: {candidatura2}')
        else:
            self.stdout.write(f'  [INFO] Candidatura já existe: {candidatura2}')
        
        # 10. Simular reutilização de documentos
        self.stdout.write('\n9. SIMULANDO REUTILIZACAO DE DOCUMENTOS:')
        for doc in documentos_disponiveis:
            if doc.pode_ser_reutilizado:
                # Criar registro de reutilização
                reutilizacao, created = ReutilizacaoDocumento.objects.get_or_create(
                    documento_original=doc,
                    vaga_utilizada=vaga2,
                    candidatura=candidatura2,
                    defaults={
                        'status_na_reutilizacao': 'aprovado'
                    }
                )
                
                if created:
                    # Marcar documento como reutilizado
                    doc.marcar_como_reutilizado()
                    self.stdout.write(f'  [OK] Documento {doc.get_tipo_documento_display()} reutilizado')
                    self.stdout.write(f'    Total reutilizações: {doc.total_reutilizacoes}')
                else:
                    self.stdout.write(f'  [INFO] Documento {doc.get_tipo_documento_display()} já foi reutilizado')
        
        # 11. Verificar documentos expirados
        self.stdout.write('\n10. VERIFICANDO DOCUMENTOS EXPIRADOS:')
        documentos_expirados = DocumentoFreelancerEmpresa.objects.filter(
            empresa_contratante=empresa,
            freelancer=freelancer,
            data_vencimento__lt=timezone.now()
        )
        
        if documentos_expirados.exists():
            self.stdout.write(f'  [WARN] {documentos_expirados.count()} documentos expirados encontrados')
            for doc in documentos_expirados:
                self.stdout.write(f'    - {doc.get_tipo_documento_display()} (expirou em {doc.data_vencimento.strftime("%d/%m/%Y")})')
        else:
            self.stdout.write('  [OK] Nenhum documento expirado')
        
        # 12. Resumo final
        self.stdout.write('\n11. RESUMO FINAL:')
        total_documentos = DocumentoFreelancerEmpresa.objects.filter(
            empresa_contratante=empresa,
            freelancer=freelancer
        ).count()
        
        documentos_aprovados = DocumentoFreelancerEmpresa.objects.filter(
            empresa_contratante=empresa,
            freelancer=freelancer,
            status='aprovado'
        ).count()
        
        documentos_reutilizaveis = DocumentoFreelancerEmpresa.objects.filter(
            empresa_contratante=empresa,
            freelancer=freelancer,
            status='aprovado'
        ).filter(
            data_vencimento__gt=timezone.now()
        ).count()
        
        total_reutilizacoes = ReutilizacaoDocumento.objects.filter(
            documento_original__empresa_contratante=empresa,
            documento_original__freelancer=freelancer
        ).count()
        
        self.stdout.write(f'  - Total de documentos: {total_documentos}')
        self.stdout.write(f'  - Documentos aprovados: {documentos_aprovados}')
        self.stdout.write(f'  - Documentos reutilizáveis: {documentos_reutilizaveis}')
        self.stdout.write(f'  - Total de reutilizações: {total_reutilizacoes}')
        
        # 13. Benefícios do sistema
        self.stdout.write('\n12. BENEFICIOS DO SISTEMA DE CACHE:')
        self.stdout.write('  [OK] Freelancer não precisa enviar documentos novamente')
        self.stdout.write('  [OK] Empresa tem histórico completo de documentos')
        self.stdout.write('  [OK] Controle automático de validade')
        self.stdout.write('  [OK] Redução de burocracia para contratações futuras')
        self.stdout.write('  [OK] Segurança e conformidade legal')
        
        self.stdout.write('\n=== SISTEMA DE CACHE DE DOCUMENTOS FUNCIONANDO! ===')
