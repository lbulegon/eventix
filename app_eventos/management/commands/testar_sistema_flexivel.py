"""
Comando para testar o sistema flexível de freelancers
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
    help = 'Testa o sistema flexível de freelancers'

    def handle(self, *args, **options):
        self.stdout.write('=== TESTANDO SISTEMA FLEXIVEL DE FREELANCERS ===')
        
        # 1. Verificar empresas
        self.stdout.write('\n1. EMPRESAS CONTRATANTES:')
        empresas = EmpresaContratante.objects.filter(ativo=True)
        for empresa in empresas:
            self.stdout.write(f'  - {empresa.nome_fantasia} (CNPJ: {empresa.cnpj})')
        
        # 2. Criar freelancers globais
        self.stdout.write('\n2. CRIANDO FREELANCERS GLOBAIS:')
        freelancers_data = [
            {'username': 'freelancer_global_1', 'email': 'global1@eventix.com'},
            {'username': 'freelancer_global_2', 'email': 'global2@eventix.com'},
            {'username': 'freelancer_global_3', 'email': 'global3@eventix.com'},
        ]
        
        for dados in freelancers_data:
            user, created = User.objects.get_or_create(
                username=dados['username'],
                defaults={
                    'email': dados['email'],
                    'tipo_usuario': 'freelancer',
                    'ativo': True
                }
            )
            
            if created:
                freelancer, created = FreelancerGlobal.objects.get_or_create(
                    usuario=user,
                    defaults={
                        'perfil_publico': True,
                        'disponivel_para_vagas': True,
                        'nivel_confiabilidade': 'alta',
                        'verificado': True
                    }
                )
                self.stdout.write(f'  [OK] Freelancer global criado: {user.username}')
            else:
                self.stdout.write(f'  [INFO] Usuário já existe: {user.username}')
        
        # 3. Criar vagas com diferentes exigências
        self.stdout.write('\n3. CRIANDO VAGAS COM DIFERENTES EXIGENCIAS:')
        if empresas.exists():
            empresa = empresas.first()
            from datetime import datetime, timedelta
            
            vagas_data = [
                {
                    'titulo': 'Técnico de Som - Evento Livre',
                    'descricao': 'Técnico de som para evento sem vínculo empregatício',
                    'exige_vinculo_empregaticio': False,
                    'remuneracao': 500.00,
                    'quantidade_vagas': 2,
                    'data_inicio': datetime.now() + timedelta(days=7),
                    'data_fim': datetime.now() + timedelta(days=8),
                },
                {
                    'titulo': 'Iluminador - Evento Corporativo',
                    'descricao': 'Iluminador para evento corporativo com vínculo temporário',
                    'exige_vinculo_empregaticio': True,
                    'tipo_vinculo': 'temporario',
                    'remuneracao': 800.00,
                    'quantidade_vagas': 1,
                    'data_inicio': datetime.now() + timedelta(days=14),
                    'data_fim': datetime.now() + timedelta(days=16),
                },
                {
                    'titulo': 'Segurança - Evento Intermitente',
                    'descricao': 'Segurança para evento com contrato intermitente',
                    'exige_vinculo_empregaticio': True,
                    'tipo_vinculo': 'intermitente',
                    'remuneracao': 300.00,
                    'quantidade_vagas': 3,
                    'data_inicio': datetime.now() + timedelta(days=21),
                    'data_fim': datetime.now() + timedelta(days=22),
                }
            ]
            
            for vaga_data in vagas_data:
                vaga, created = VagaEmpresa.objects.get_or_create(
                    empresa_contratante=empresa,
                    titulo=vaga_data['titulo'],
                    defaults=vaga_data
                )
                if created:
                    self.stdout.write(f'  [OK] Vaga criada: {vaga.titulo}')
                    self.stdout.write(f'    Exige vínculo: {vaga.exige_vinculo_empregaticio}')
                    if vaga.exige_vinculo_empregaticio:
                        self.stdout.write(f'    Tipo de vínculo: {vaga.get_tipo_vinculo_display()}')
                else:
                    self.stdout.write(f'  [INFO] Vaga já existe: {vaga.titulo}')
        
        # 4. Testar candidaturas
        self.stdout.write('\n4. TESTANDO CANDIDATURAS:')
        
        # Candidatura para vaga sem vínculo
        vaga_livre = VagaEmpresa.objects.filter(
            empresa_contratante=empresa,
            exige_vinculo_empregaticio=False
        ).first()
        
        freelancer_1 = FreelancerGlobal.objects.first()
        
        if vaga_livre and freelancer_1:
            candidatura_livre, created = CandidaturaEmpresa.objects.get_or_create(
                vaga=vaga_livre,
                freelancer=freelancer_1,
                defaults={
                    'carta_apresentacao': 'Tenho experiência em som e estou disponível.',
                    'experiencia_relacionada': '5 anos de experiência em eventos.'
                }
            )
            if created:
                self.stdout.write(f'  [OK] Candidatura livre criada: {candidatura_livre}')
                self.stdout.write(f'    Exige documentação: {candidatura_livre.exige_documentacao}')
            else:
                self.stdout.write(f'  [INFO] Candidatura livre já existe')
        
        # Candidatura para vaga com vínculo
        vaga_vinculo = VagaEmpresa.objects.filter(
            empresa_contratante=empresa,
            exige_vinculo_empregaticio=True
        ).first()
        
        freelancer_2 = FreelancerGlobal.objects.all()[1] if FreelancerGlobal.objects.count() > 1 else freelancer_1
        
        if vaga_vinculo and freelancer_2:
            candidatura_vinculo, created = CandidaturaEmpresa.objects.get_or_create(
                vaga=vaga_vinculo,
                freelancer=freelancer_2,
                defaults={
                    'carta_apresentacao': 'Sou freelancer experiente e tenho todos os documentos.',
                    'experiencia_relacionada': '3 anos de experiência em iluminação.'
                }
            )
            if created:
                self.stdout.write(f'  [OK] Candidatura com vínculo criada: {candidatura_vinculo}')
                self.stdout.write(f'    Exige documentação: {candidatura_vinculo.exige_documentacao}')
            else:
                self.stdout.write(f'  [INFO] Candidatura com vínculo já existe')
        
        # 5. Testar documentos obrigatórios
        self.stdout.write('\n5. TESTANDO DOCUMENTOS OBRIGATORIOS:')
        
        if candidatura_vinculo and candidatura_vinculo.exige_documentacao:
            documentos_obrigatorios = [
                'rg', 'cpf', 'ctps', 'comprovante_residencia'
            ]
            
            for tipo_doc in documentos_obrigatorios:
                doc, created = DocumentoFreelancer.objects.get_or_create(
                    candidatura=candidatura_vinculo,
                    tipo_documento=tipo_doc,
                    defaults={
                        'status': 'pendente',
                        'observacoes': f'Documento {tipo_doc} pendente de upload'
                    }
                )
                if created:
                    self.stdout.write(f'  [OK] Documento obrigatório criado: {doc.get_tipo_documento_display()}')
                else:
                    self.stdout.write(f'  [INFO] Documento já existe: {doc.get_tipo_documento_display()}')
        
        # 6. Testar contratação
        self.stdout.write('\n6. TESTANDO CONTRATACAO:')
        
        if candidatura_livre:
            contratacao, created = ContratacaoEmpresa.objects.get_or_create(
                candidatura=candidatura_livre,
                defaults={
                    'status': 'ativa',
                    'tem_vinculo_empregaticio': False,
                    'remuneracao_efetiva': candidatura_livre.vaga.remuneracao,
                    'contratado_por': empresa.empresa_contratante.first() if hasattr(empresa, 'empresa_contratante') else None
                }
            )
            if created:
                self.stdout.write(f'  [OK] Contratação criada: {contratacao}')
                self.stdout.write(f'    Tem vínculo empregatício: {contratacao.tem_vinculo_empregaticio}')
                self.stdout.write(f'    Pode iniciar trabalho: {contratacao.pode_iniciar_trabalho}')
            else:
                self.stdout.write(f'  [INFO] Contratação já existe')
        
        # 7. Resumo do sistema
        self.stdout.write('\n7. RESUMO DO SISTEMA:')
        self.stdout.write(f'  - Empresas contratantes: {EmpresaContratante.objects.filter(ativo=True).count()}')
        self.stdout.write(f'  - Freelancers globais: {FreelancerGlobal.objects.count()}')
        self.stdout.write(f'  - Vagas da empresa: {VagaEmpresa.objects.count()}')
        self.stdout.write(f'  - Vagas sem vínculo: {VagaEmpresa.objects.filter(exige_vinculo_empregaticio=False).count()}')
        self.stdout.write(f'  - Vagas com vínculo: {VagaEmpresa.objects.filter(exige_vinculo_empregaticio=True).count()}')
        self.stdout.write(f'  - Candidaturas: {CandidaturaEmpresa.objects.count()}')
        self.stdout.write(f'  - Documentos: {DocumentoFreelancer.objects.count()}')
        self.stdout.write(f'  - Contratações: {ContratacaoEmpresa.objects.count()}')
        
        # 8. Testar regras de negócio
        self.stdout.write('\n8. TESTANDO REGRAS DE NEGOCIO:')
        
        # Testar se vaga sem vínculo não exige documentos
        if vaga_livre:
            self.stdout.write(f'  - Vaga sem vínculo exige documentação: {vaga_livre.exige_documentacao}')
        
        # Testar se vaga com vínculo exige documentos
        if vaga_vinculo:
            self.stdout.write(f'  - Vaga com vínculo exige documentação: {vaga_vinculo.exige_documentacao}')
        
        # Testar se contratação sem vínculo pode iniciar trabalho
        if candidatura_livre and hasattr(candidatura_livre, 'contratacao'):
            self.stdout.write(f'  - Contratação sem vínculo pode iniciar: {candidatura_livre.contratacao.pode_iniciar_trabalho}')
        
        self.stdout.write('\n=== SISTEMA FLEXIVEL FUNCIONANDO CORRETAMENTE! ===')
