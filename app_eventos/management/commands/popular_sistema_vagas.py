# app_eventos/management/commands/popular_sistema_vagas.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from app_eventos.models import (
    EmpresaContratante, Empresa, Evento, LocalEvento, SetorEvento, 
    Funcao, Vaga, Freelance, User, TipoFuncao
)


class Command(BaseCommand):
    help = 'Popula o sistema com dados de teste para vagas e candidaturas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--empresa',
            type=str,
            help='Nome da empresa contratante (padrão: primeira empresa ativa)',
        )
        parser.add_argument(
            '--limpar',
            action='store_true',
            help='Limpa dados existentes antes de popular',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Iniciando popularização do sistema de vagas...')
        )

        # Limpar dados se solicitado
        if options['limpar']:
            self.limpar_dados()

        # Buscar ou criar empresa contratante
        empresa = self.obter_empresa_contratante(options.get('empresa'))
        
        # Criar dados básicos
        self.criar_tipos_funcoes()
        self.criar_funcoes()
        self.criar_local_evento(empresa)
        
        # Criar eventos
        eventos = self.criar_eventos(empresa)
        
        # Criar setores para cada evento
        setores = self.criar_setores(eventos)
        
        # Criar vagas
        vagas = self.criar_vagas(setores)
        
        # Criar freelancers de teste
        freelancers = self.criar_freelancers_teste()
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Sistema populado com sucesso!')
        )
        self.stdout.write(f'📊 Estatísticas:')
        self.stdout.write(f'   - Empresas: 1')
        self.stdout.write(f'   - Eventos: {len(eventos)}')
        self.stdout.write(f'   - Setores: {len(setores)}')
        self.stdout.write(f'   - Vagas: {len(vagas)}')
        self.stdout.write(f'   - Freelancers: {len(freelancers)}')

    def limpar_dados(self):
        """Limpa dados existentes"""
        self.stdout.write('🧹 Limpando dados existentes...')
        
        Vaga.objects.all().delete()
        SetorEvento.objects.all().delete()
        Evento.objects.all().delete()
        LocalEvento.objects.all().delete()
        Funcao.objects.all().delete()
        TipoFuncao.objects.all().delete()
        
        # Manter usuários e empresas existentes
        self.stdout.write('✅ Dados limpos com sucesso!')

    def obter_empresa_contratante(self, nome_empresa=None):
        """Obtém ou cria empresa contratante"""
        if nome_empresa:
            empresa, created = EmpresaContratante.objects.get_or_create(
                nome=nome_empresa,
                defaults={
                    'cnpj': '12345678000199',
                    'email': f'{nome_empresa.lower().replace(" ", "")}@exemplo.com',
                    'telefone': '(11) 99999-9999',
                    'ativo': True
                }
            )
        else:
            empresa = EmpresaContratante.objects.filter(ativo=True).first()
            if not empresa:
                empresa = EmpresaContratante.objects.create(
                    nome='Eventos Premium',
                    cnpj='12345678000199',
                    email='contato@eventospremium.com',
                    telefone='(11) 99999-9999',
                    ativo=True
                )
        
        self.stdout.write(f'🏢 Empresa: {empresa.nome}')
        return empresa

    def criar_tipos_funcoes(self):
        """Cria tipos de funções"""
        tipos = [
            'Produção',
            'Operacional',
            'Técnico',
            'Comercial',
            'Administrativo',
            'Segurança',
            'Limpeza',
            'Alimentação'
        ]
        
        for tipo in tipos:
            TipoFuncao.objects.get_or_create(nome=tipo)
        
        self.stdout.write(f'📋 Tipos de funções criados: {len(tipos)}')

    def criar_funcoes(self):
        """Cria funções específicas"""
        funcoes_data = [
            ('Produção', 'Coordenador de Produção', 'Coordena toda a produção do evento'),
            ('Produção', 'Assistente de Produção', 'Auxilia na produção do evento'),
            ('Operacional', 'Operador de Som', 'Opera equipamentos de áudio'),
            ('Operacional', 'Operador de Luz', 'Opera equipamentos de iluminação'),
            ('Operacional', 'Operador de Vídeo', 'Opera equipamentos de vídeo'),
            ('Técnico', 'Técnico de Palco', 'Monta e desmonta estruturas de palco'),
            ('Técnico', 'Técnico de Eletricidade', 'Responsável pela parte elétrica'),
            ('Comercial', 'Promotor de Vendas', 'Promove vendas no evento'),
            ('Comercial', 'Atendente', 'Atende o público'),
            ('Administrativo', 'Recepcionista', 'Recebe e orienta visitantes'),
            ('Administrativo', 'Controlador de Acesso', 'Controla entrada e saída'),
            ('Segurança', 'Segurança', 'Garante a segurança do evento'),
            ('Limpeza', 'Limpeza', 'Mantém limpeza durante o evento'),
            ('Alimentação', 'Garçom', 'Atende mesas e serve alimentos'),
            ('Alimentação', 'Cozinheiro', 'Prepara alimentos'),
        ]
        
        for tipo_nome, funcao_nome, descricao in funcoes_data:
            tipo = TipoFuncao.objects.get(nome=tipo_nome)
            Funcao.objects.get_or_create(
                nome=funcao_nome,
                defaults={
                    'tipo_funcao': tipo,
                    'descricao': descricao,
                    'ativo': True
                }
            )
        
        self.stdout.write(f'👥 Funções criadas: {len(funcoes_data)}')

    def criar_local_evento(self, empresa):
        """Cria local de evento"""
        # Primeiro criar uma empresa proprietária
        empresa_proprietaria, _ = Empresa.objects.get_or_create(
            nome='Centro de Convenções São Paulo LTDA',
            defaults={
                'cnpj': '98765432000199',
                'email': 'contato@centroconvencoes.com',
                'telefone': '(11) 3333-4444',
                'ativo': True
            }
        )
        
        local, created = LocalEvento.objects.get_or_create(
            nome='Centro de Convenções São Paulo',
            defaults={
                'endereco': 'Av. Paulista, 1000 - São Paulo/SP',
                'capacidade': 5000,
                'descricao': 'Centro de convenções moderno no centro de São Paulo',
                'empresa_contratante': empresa,
                'empresa_proprietaria': empresa_proprietaria,
                'ativo': True
            }
        )
        
        self.stdout.write(f'📍 Local: {local.nome}')
        return local

    def criar_eventos(self, empresa):
        """Cria eventos de teste"""
        local = LocalEvento.objects.first()
        # Buscar empresa proprietária do local
        empresa_proprietaria = local.empresa_proprietaria
        
        eventos_data = [
            {
                'nome': 'Festival de Música 2024',
                'descricao': 'Grande festival de música com artistas nacionais e internacionais',
                'data_inicio': timezone.now() + timedelta(days=30),
                'data_fim': timezone.now() + timedelta(days=32),
                'local': local,
                'empresa_contratante': empresa,
                'empresa_contratante_recursos': empresa_proprietaria
            },
            {
                'nome': 'Feira de Tecnologia',
                'descricao': 'Feira de tecnologia e inovação',
                'data_inicio': timezone.now() + timedelta(days=45),
                'data_fim': timezone.now() + timedelta(days=47),
                'local': local,
                'empresa_contratante': empresa,
                'empresa_contratante_recursos': empresa_proprietaria
            },
            {
                'nome': 'Conferência de Marketing Digital',
                'descricao': 'Conferência sobre tendências em marketing digital',
                'data_inicio': timezone.now() + timedelta(days=60),
                'data_fim': timezone.now() + timedelta(days=61),
                'local': local,
                'empresa_contratante': empresa,
                'empresa_contratante_recursos': empresa_proprietaria
            }
        ]
        
        eventos = []
        for evento_data in eventos_data:
            evento, created = Evento.objects.get_or_create(
                nome=evento_data['nome'],
                defaults=evento_data
            )
            eventos.append(evento)
        
        self.stdout.write(f'🎪 Eventos criados: {len(eventos)}')
        return eventos

    def criar_setores(self, eventos):
        """Cria setores para os eventos"""
        setores_data = [
            ('Palco Principal', 'Setor principal do evento'),
            ('Palco Secundário', 'Setor secundário para apresentações'),
            ('Área de Alimentação', 'Setor de food trucks e restaurantes'),
            ('Área Comercial', 'Setor de stands e vendas'),
            ('Área VIP', 'Setor exclusivo para convidados especiais'),
            ('Backstage', 'Área técnica e de apoio'),
        ]
        
        setores = []
        for evento in eventos:
            for nome_setor, descricao in setores_data:
                setor, created = SetorEvento.objects.get_or_create(
                    evento=evento,
                    nome=nome_setor,
                    defaults={
                        'descricao': descricao,
                        'ativo': True
                    }
                )
                setores.append(setor)
        
        self.stdout.write(f'🏗️ Setores criados: {len(setores)}')
        return setores

    def criar_vagas(self, setores):
        """Cria vagas para os setores"""
        funcoes = Funcao.objects.all()
        vagas = []
        
        for setor in setores:
            # Criar 2-4 vagas por setor
            num_vagas = 3 if 'Palco' in setor.nome else 2
            
            for i in range(num_vagas):
                funcao = funcoes[i % len(funcoes)]
                
                vaga_data = {
                    'setor': setor,
                    'titulo': f'{funcao.nome} - {setor.nome}',
                    'funcao': funcao,
                    'quantidade': 2 + (i % 3),  # 2-4 vagas
                    'remuneracao': Decimal('150.00') + (i * Decimal('25.00')),
                    'tipo_remuneracao': 'por_dia',
                    'descricao': f'Vaga para {funcao.nome} no setor {setor.nome} do evento {setor.evento.nome}.',
                    'requisitos': f'Experiência em {funcao.tipo_funcao.nome.lower()} desejável.',
                    'responsabilidades': f'Executar atividades de {funcao.nome.lower()} conforme orientações.',
                    'beneficios': 'Vale refeição, transporte e seguro de acidentes.',
                    'nivel_experiencia': ['iniciante', 'intermediario', 'avancado'][i % 3],
                    'experiencia_minima': i * 6,  # 0, 6, 12 meses
                    'data_limite_candidatura': timezone.now() + timedelta(days=15),
                    'data_inicio_trabalho': setor.evento.data_inicio - timedelta(days=1),
                    'data_fim_trabalho': setor.evento.data_fim + timedelta(days=1),
                    'ativa': True,
                    'publicada': True,
                    'urgente': i == 0,  # Primeira vaga de cada setor é urgente
                }
                
                vaga, created = Vaga.objects.get_or_create(
                    setor=vaga_data['setor'],
                    titulo=vaga_data['titulo'],
                    defaults=vaga_data
                )
                vagas.append(vaga)
        
        self.stdout.write(f'💼 Vagas criadas: {len(vagas)}')
        return vagas

    def criar_freelancers_teste(self):
        """Cria freelancers de teste"""
        freelancers_data = [
            {
                'username': 'joao.silva',
                'email': 'joao.silva@email.com',
                'first_name': 'João',
                'last_name': 'Silva',
                'nome_completo': 'João Silva',
                'telefone': '(11) 99999-0001',
                'cpf': '12345678901',
                'cidade': 'São Paulo',
                'uf': 'SP',
                'tipo_usuario': 'freelancer'
            },
            {
                'username': 'maria.santos',
                'email': 'maria.santos@email.com',
                'first_name': 'Maria',
                'last_name': 'Santos',
                'nome_completo': 'Maria Santos',
                'telefone': '(11) 99999-0002',
                'cpf': '12345678902',
                'cidade': 'São Paulo',
                'uf': 'SP',
                'tipo_usuario': 'freelancer'
            },
            {
                'username': 'pedro.oliveira',
                'email': 'pedro.oliveira@email.com',
                'first_name': 'Pedro',
                'last_name': 'Oliveira',
                'nome_completo': 'Pedro Oliveira',
                'telefone': '(11) 99999-0003',
                'cpf': '12345678903',
                'cidade': 'São Paulo',
                'uf': 'SP',
                'tipo_usuario': 'freelancer'
            },
            {
                'username': 'ana.costa',
                'email': 'ana.costa@email.com',
                'first_name': 'Ana',
                'last_name': 'Costa',
                'nome_completo': 'Ana Costa',
                'telefone': '(11) 99999-0004',
                'cpf': '12345678904',
                'cidade': 'São Paulo',
                'uf': 'SP',
                'tipo_usuario': 'freelancer'
            },
            {
                'username': 'carlos.ferreira',
                'email': 'carlos.ferreira@email.com',
                'first_name': 'Carlos',
                'last_name': 'Ferreira',
                'nome_completo': 'Carlos Ferreira',
                'telefone': '(11) 99999-0005',
                'cpf': '12345678905',
                'cidade': 'São Paulo',
                'uf': 'SP',
                'tipo_usuario': 'freelancer'
            }
        ]
        
        freelancers = []
        for data in freelancers_data:
            # Criar usuário
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'tipo_usuario': data['tipo_usuario'],
                    'is_active': True
                }
            )
            
            if created:
                user.set_password('123456')  # Senha padrão
                user.save()
            
            # Criar perfil freelancer
            freelance, created = Freelance.objects.get_or_create(
                usuario=user,
                defaults={
                    'nome_completo': data['nome_completo'],
                    'telefone': data['telefone'],
                    'cpf': data['cpf'],
                    'cidade': data['cidade'],
                    'uf': data['uf'],
                    'cadastro_completo': True
                }
            )
            freelancers.append(freelance)
        
        self.stdout.write(f'👤 Freelancers criados: {len(freelancers)}')
        return freelancers
