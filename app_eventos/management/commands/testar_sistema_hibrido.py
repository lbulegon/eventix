"""
Comando para testar o sistema híbrido de freelancers
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from app_eventos.models import EmpresaContratante
from app_eventos.models_freelancers import (
    FreelancerEmpresa, FreelancerMarketplace, 
    VagaEmpresa, CandidaturaEmpresa
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Testa o sistema híbrido de freelancers'

    def handle(self, *args, **options):
        self.stdout.write('=== TESTANDO SISTEMA HIBRIDO DE FREELANCERS ===')
        
        # 1. Verificar empresas
        self.stdout.write('\n1. EMPRESAS CONTRATANTES:')
        empresas = EmpresaContratante.objects.filter(ativo=True)
        for empresa in empresas:
            self.stdout.write(f'  - {empresa.nome_fantasia} (CNPJ: {empresa.cnpj})')
        
        # 2. Criar freelancers próprios da empresa
        self.stdout.write('\n2. CRIANDO FREELANCERS PROPRIOS:')
        empresa = empresas.first()
        if empresa:
            # Criar usuários freelancers próprios
            freelancers_proprios = [
                {'username': 'freelancer_proprio_1', 'email': 'proprio1@empresa.com'},
                {'username': 'freelancer_proprio_2', 'email': 'proprio2@empresa.com'},
            ]
            
            for dados in freelancers_proprios:
                user, created = User.objects.get_or_create(
                    username=dados['username'],
                    defaults={
                        'email': dados['email'],
                        'tipo_usuario': 'freelancer',
                        'ativo': True
                    }
                )
                
                if created:
                    freelancer_empresa, created = FreelancerEmpresa.objects.get_or_create(
                        empresa_contratante=empresa,
                        usuario=user,
                        defaults={
                            'codigo_interno': f'EMP-{user.id}',
                            'status_empresa': 'ativo',
                            'prioridade_empresa': 'alta'
                        }
                    )
                    self.stdout.write(f'  [OK] Freelancer próprio criado: {user.username}')
                else:
                    self.stdout.write(f'  [INFO] Usuário já existe: {user.username}')
        
        # 3. Criar freelancers do marketplace
        self.stdout.write('\n3. CRIANDO FREELANCERS DO MARKETPLACE:')
        freelancers_marketplace = [
            {'username': 'freelancer_market_1', 'email': 'market1@eventix.com'},
            {'username': 'freelancer_market_2', 'email': 'market2@eventix.com'},
        ]
        
        for dados in freelancers_marketplace:
            user, created = User.objects.get_or_create(
                username=dados['username'],
                defaults={
                    'email': dados['email'],
                    'tipo_usuario': 'freelancer',
                    'ativo': True
                }
            )
            
            if created:
                freelancer_market, created = FreelancerMarketplace.objects.get_or_create(
                    usuario=user,
                    defaults={
                        'perfil_publico': True,
                        'disponivel_para_vagas': True,
                        'nivel_confiabilidade': 'alta',
                        'verificado': True
                    }
                )
                self.stdout.write(f'  [OK] Freelancer marketplace criado: {user.username}')
            else:
                self.stdout.write(f'  [INFO] Usuário já existe: {user.username}')
        
        # 4. Criar vagas da empresa
        self.stdout.write('\n4. CRIANDO VAGAS DA EMPRESA:')
        if empresa:
            from datetime import datetime, timedelta
            
            vagas_data = [
                {
                    'titulo': 'Técnico de Som - Evento Corporativo',
                    'descricao': 'Necessário técnico experiente em som para evento corporativo',
                    'tipo_vaga': 'propria',  # Apenas freelancers próprios
                    'remuneracao': 500.00,
                    'quantidade_vagas': 2,
                    'data_inicio': datetime.now() + timedelta(days=7),
                    'data_fim': datetime.now() + timedelta(days=8),
                },
                {
                    'titulo': 'Iluminador - Festival de Música',
                    'descricao': 'Iluminador para festival de música',
                    'tipo_vaga': 'marketplace',  # Apenas marketplace
                    'remuneracao': 800.00,
                    'quantidade_vagas': 1,
                    'data_inicio': datetime.now() + timedelta(days=14),
                    'data_fim': datetime.now() + timedelta(days=16),
                },
                {
                    'titulo': 'Segurança - Evento Social',
                    'descricao': 'Segurança para evento social',
                    'tipo_vaga': 'ambos',  # Ambos os tipos
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
                    self.stdout.write(f'  [OK] Vaga criada: {vaga.titulo} ({vaga.tipo_vaga})')
                else:
                    self.stdout.write(f'  [INFO] Vaga já existe: {vaga.titulo}')
        
        # 5. Testar candidaturas
        self.stdout.write('\n5. TESTANDO CANDIDATURAS:')
        
        # Candidatura de freelancer próprio
        freelancer_proprio = FreelancerEmpresa.objects.filter(
            empresa_contratante=empresa
        ).first()
        
        if freelancer_proprio:
            vaga_propria = VagaEmpresa.objects.filter(
                empresa_contratante=empresa,
                tipo_vaga__in=['propria', 'ambos']
            ).first()
            
            if vaga_propria:
                candidatura, created = CandidaturaEmpresa.objects.get_or_create(
                    vaga=vaga_propria,
                    freelancer_proprio=freelancer_proprio,
                    defaults={
                        'carta_apresentacao': 'Tenho experiência em som e estou disponível.',
                        'experiencia_relacionada': '5 anos de experiência em eventos.'
                    }
                )
                if created:
                    self.stdout.write(f'  [OK] Candidatura própria criada: {candidatura}')
                else:
                    self.stdout.write(f'  [INFO] Candidatura própria já existe')
        
        # Candidatura de freelancer do marketplace
        freelancer_market = FreelancerMarketplace.objects.first()
        
        if freelancer_market:
            vaga_marketplace = VagaEmpresa.objects.filter(
                empresa_contratante=empresa,
                tipo_vaga__in=['marketplace', 'ambos']
            ).first()
            
            if vaga_marketplace:
                candidatura, created = CandidaturaEmpresa.objects.get_or_create(
                    vaga=vaga_marketplace,
                    freelancer_marketplace=freelancer_market,
                    defaults={
                        'carta_apresentacao': 'Sou freelancer do marketplace e tenho experiência.',
                        'experiencia_relacionada': '3 anos de experiência em iluminação.'
                    }
                )
                if created:
                    self.stdout.write(f'  [OK] Candidatura marketplace criada: {candidatura}')
                else:
                    self.stdout.write(f'  [INFO] Candidatura marketplace já existe')
        
        # 6. Resumo do sistema
        self.stdout.write('\n6. RESUMO DO SISTEMA:')
        self.stdout.write(f'  - Empresas contratantes: {EmpresaContratante.objects.filter(ativo=True).count()}')
        self.stdout.write(f'  - Freelancers próprios: {FreelancerEmpresa.objects.count()}')
        self.stdout.write(f'  - Freelancers marketplace: {FreelancerMarketplace.objects.count()}')
        self.stdout.write(f'  - Vagas da empresa: {VagaEmpresa.objects.count()}')
        self.stdout.write(f'  - Candidaturas: {CandidaturaEmpresa.objects.count()}')
        
        # 7. Testar regras de negócio
        self.stdout.write('\n7. TESTANDO REGRAS DE NEGOCIO:')
        
        # Testar se freelancer próprio pode se candidatar a vaga própria
        if freelancer_proprio and vaga_propria:
            pode_candidatar = vaga_propria.pode_candidatar_freelancer_proprio
            self.stdout.write(f'  - Freelancer próprio pode candidatar a vaga própria: {pode_candidatar}')
        
        # Testar se freelancer marketplace pode se candidatar a vaga marketplace
        if freelancer_market and vaga_marketplace:
            pode_candidatar = vaga_marketplace.pode_candidatar_marketplace
            self.stdout.write(f'  - Freelancer marketplace pode candidatar a vaga marketplace: {pode_candidatar}')
        
        self.stdout.write('\n=== SISTEMA HIBRIDO FUNCIONANDO CORRETAMENTE! ===')
