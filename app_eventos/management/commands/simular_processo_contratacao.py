"""
Comando para simular o processo completo de candidatura e contratação
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from app_eventos.models import EmpresaContratante
from app_eventos.models_freelancers import (
    FreelancerGlobal, VagaEmpresa, CandidaturaEmpresa,
    DocumentoFreelancer, ContratacaoEmpresa
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Simula o processo completo de candidatura e contratação'

    def handle(self, *args, **options):
        self.stdout.write('=== SIMULANDO PROCESSO COMPLETO DE CONTRATACAO ===')
        
        # 1. Buscar empresa e vagas
        empresa = EmpresaContratante.objects.filter(ativo=True).first()
        if not empresa:
            self.stdout.write('Nenhuma empresa ativa encontrada!')
            return
        
        self.stdout.write(f'Empresa: {empresa.nome_fantasia}')
        
        # 2. Buscar vagas existentes
        vagas = VagaEmpresa.objects.filter(empresa_contratante=empresa, ativa=True)
        if not vagas.exists():
            self.stdout.write('Nenhuma vaga encontrada! Execute primeiro: python manage.py criar_vaga_com_documentacao')
            return
        
        vaga_livre = vagas.filter(exige_vinculo_empregaticio=False).first()
        vaga_vinculo = vagas.filter(exige_vinculo_empregaticio=True).first()
        
        # 3. Criar freelancer global
        self.stdout.write('\n1. CRIANDO FREELANCER GLOBAL:')
        user, created = User.objects.get_or_create(
            username='freelancer_teste',
            defaults={
                'email': 'freelancer@teste.com',
                'tipo_usuario': 'freelancer',
                'ativo': True,
                'first_name': 'João',
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
        
        # 4. Simular candidatura para vaga SEM vínculo
        if vaga_livre:
            self.stdout.write('\n2. CANDIDATURA PARA VAGA SEM VINCULO:')
            candidatura_livre, created = CandidaturaEmpresa.objects.get_or_create(
                vaga=vaga_livre,
                freelancer=freelancer,
                defaults={
                    'carta_apresentacao': 'Tenho experiência em som e estou disponível para o evento.',
                    'experiencia_relacionada': '5 anos de experiência em eventos de som.'
                }
            )
            
            if created:
                self.stdout.write(f'  [OK] Candidatura criada: {candidatura_livre}')
                self.stdout.write(f'    Vaga: {candidatura_livre.vaga.titulo}')
                self.stdout.write(f'    Exige documentação: {candidatura_livre.exige_documentacao}')
                self.stdout.write(f'    Status: {candidatura_livre.get_status_display()}')
            else:
                self.stdout.write(f'  [INFO] Candidatura já existe')
        
        # 5. Simular candidatura para vaga COM vínculo
        if vaga_vinculo:
            self.stdout.write('\n3. CANDIDATURA PARA VAGA COM VINCULO:')
            candidatura_vinculo, created = CandidaturaEmpresa.objects.get_or_create(
                vaga=vaga_vinculo,
                freelancer=freelancer,
                defaults={
                    'carta_apresentacao': 'Tenho experiência em iluminação e todos os documentos necessários.',
                    'experiencia_relacionada': '3 anos de experiência em iluminação de eventos.'
                }
            )
            
            if created:
                self.stdout.write(f'  [OK] Candidatura criada: {candidatura_vinculo}')
                self.stdout.write(f'    Vaga: {candidatura_vinculo.vaga.titulo}')
                self.stdout.write(f'    Exige documentação: {candidatura_vinculo.exige_documentacao}')
                self.stdout.write(f'    Status: {candidatura_vinculo.get_status_display()}')
            else:
                self.stdout.write(f'  [INFO] Candidatura já existe')
        
        # 6. Simular upload de documentos (apenas para vaga com vínculo)
        if vaga_vinculo and candidatura_vinculo:
            self.stdout.write('\n4. UPLOAD DE DOCUMENTOS OBRIGATORIOS:')
            documentos_obrigatorios = [
                ('rg', 'RG'),
                ('cpf', 'CPF'),
                ('ctps', 'Carteira de Trabalho'),
                ('comprovante_residencia', 'Comprovante de Residência')
            ]
            
            for tipo_doc, nome_doc in documentos_obrigatorios:
                doc, created = DocumentoFreelancer.objects.get_or_create(
                    candidatura=candidatura_vinculo,
                    tipo_documento=tipo_doc,
                    defaults={
                        'status': 'pendente',
                        'observacoes': f'Documento {nome_doc} pendente de upload'
                    }
                )
                
                if created:
                    self.stdout.write(f'  [OK] Documento obrigatório criado: {nome_doc}')
                else:
                    self.stdout.write(f'  [INFO] Documento já existe: {nome_doc}')
            
            # Simular aprovação de documentos
            self.stdout.write('\n5. APROVACAO DE DOCUMENTOS:')
            documentos = candidatura_vinculo.documentos.all()
            for doc in documentos:
                doc.status = 'aprovado'
                doc.data_validacao = candidatura_vinculo.data_candidatura
                doc.observacoes = 'Documento aprovado pela empresa'
                doc.save()
                self.stdout.write(f'  [OK] Documento aprovado: {doc.get_tipo_documento_display()}')
        
        # 7. Simular contratação
        self.stdout.write('\n6. PROCESSO DE CONTRATACAO:')
        
        # Contratação para vaga sem vínculo
        if vaga_livre and candidatura_livre:
            contratacao_livre, created = ContratacaoEmpresa.objects.get_or_create(
                candidatura=candidatura_livre,
                defaults={
                    'status': 'ativa',
                    'tem_vinculo_empregaticio': False,
                    'remuneracao_efetiva': candidatura_livre.vaga.remuneracao,
                    'observacoes': 'Contratação sem vínculo empregatício'
                }
            )
            
            if created:
                self.stdout.write(f'  [OK] Contratação sem vínculo criada: {contratacao_livre}')
                self.stdout.write(f'    Tem vínculo empregatício: {contratacao_livre.tem_vinculo_empregaticio}')
                self.stdout.write(f'    Pode iniciar trabalho: {contratacao_livre.pode_iniciar_trabalho}')
            else:
                self.stdout.write(f'  [INFO] Contratação sem vínculo já existe')
        
        # Contratação para vaga com vínculo
        if vaga_vinculo and candidatura_vinculo:
            contratacao_vinculo, created = ContratacaoEmpresa.objects.get_or_create(
                candidatura=candidatura_vinculo,
                defaults={
                    'status': 'ativa',
                    'tem_vinculo_empregaticio': True,
                    'numero_contrato': f'CT-{candidatura_vinculo.id}-2024',
                    'data_inicio_contrato': candidatura_vinculo.vaga.data_inicio.date(),
                    'data_fim_contrato': candidatura_vinculo.vaga.data_fim.date(),
                    'remuneracao_efetiva': candidatura_vinculo.vaga.remuneracao,
                    'observacoes': 'Contratação com vínculo empregatício temporário'
                }
            )
            
            if created:
                self.stdout.write(f'  [OK] Contratação com vínculo criada: {contratacao_vinculo}')
                self.stdout.write(f'    Tem vínculo empregatício: {contratacao_vinculo.tem_vinculo_empregaticio}')
                self.stdout.write(f'    Número do contrato: {contratacao_vinculo.numero_contrato}')
                self.stdout.write(f'    Documentos aprovados: {contratacao_vinculo.documentos_obrigatorios_aprovados}')
                self.stdout.write(f'    Pode iniciar trabalho: {contratacao_vinculo.pode_iniciar_trabalho}')
            else:
                self.stdout.write(f'  [INFO] Contratação com vínculo já existe')
        
        # 8. Resumo final
        self.stdout.write('\n7. RESUMO FINAL:')
        self.stdout.write(f'  - Freelancer: {freelancer.usuario.username}')
        self.stdout.write(f'  - Candidaturas: {CandidaturaEmpresa.objects.filter(freelancer=freelancer).count()}')
        self.stdout.write(f'  - Documentos: {DocumentoFreelancer.objects.filter(candidatura__freelancer=freelancer).count()}')
        self.stdout.write(f'  - Contratações: {ContratacaoEmpresa.objects.filter(candidatura__freelancer=freelancer).count()}')
        
        # Estatísticas por tipo de vaga
        candidaturas = CandidaturaEmpresa.objects.filter(freelancer=freelancer)
        for candidatura in candidaturas:
            self.stdout.write(f'\n  Candidatura: {candidatura.vaga.titulo}')
            self.stdout.write(f'    Exige documentação: {candidatura.exige_documentacao}')
            if candidatura.exige_documentacao:
                docs_aprovados = candidatura.documentos.filter(status='aprovado').count()
                docs_total = candidatura.documentos.count()
                self.stdout.write(f'    Documentos aprovados: {docs_aprovados}/{docs_total}')
            
            if hasattr(candidatura, 'contratacao'):
                self.stdout.write(f'    Contratado: Sim')
                self.stdout.write(f'    Pode iniciar: {candidatura.contratacao.pode_iniciar_trabalho}')
            else:
                self.stdout.write(f'    Contratado: Não')
        
        self.stdout.write('\n=== PROCESSO COMPLETO SIMULADO COM SUCESSO! ===')
        self.stdout.write('O sistema agora suporta:')
        self.stdout.write('1. Vagas sem exigência de documentação (trabalho livre)')
        self.stdout.write('2. Vagas com exigência de documentação (vínculo empregatício)')
        self.stdout.write('3. Controle de documentos obrigatórios por vaga')
        self.stdout.write('4. Validação de documentos antes da contratação')
        self.stdout.write('5. Contratos temporários e intermitentes')
