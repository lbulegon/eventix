"""
Comando para criar vagas com diferentes exigências de documentação
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from app_eventos.models import EmpresaContratante
from app_eventos.models_freelancers import VagaEmpresa
from datetime import datetime, timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Cria vagas com diferentes exigências de documentação'

    def add_arguments(self, parser):
        parser.add_argument(
            '--empresa-id',
            type=int,
            help='ID da empresa contratante'
        )

    def handle(self, *args, **options):
        self.stdout.write('=== CRIANDO VAGAS COM DIFERENTES EXIGENCIAS ===')
        
        # Buscar empresa
        empresa_id = options.get('empresa_id')
        if empresa_id:
            try:
                empresa = EmpresaContratante.objects.get(id=empresa_id)
            except EmpresaContratante.DoesNotExist:
                self.stdout.write('Empresa não encontrada!')
                return
        else:
            empresa = EmpresaContratante.objects.filter(ativo=True).first()
            if not empresa:
                self.stdout.write('Nenhuma empresa ativa encontrada!')
                return
        
        self.stdout.write(f'Empresa selecionada: {empresa.nome_fantasia}')
        
        # 1. Vaga SEM exigência de documentação (trabalho livre)
        self.stdout.write('\n1. CRIANDO VAGA SEM EXIGENCIA DE DOCUMENTACAO:')
        vaga_livre = VagaEmpresa.objects.create(
            empresa_contratante=empresa,
            titulo='Técnico de Som - Evento Livre',
            descricao='Técnico de som para evento sem vínculo empregatício. Trabalho livre, sem necessidade de documentação.',
            exige_vinculo_empregaticio=False,
            remuneracao=500.00,
            tipo_remuneracao='por_evento',
            quantidade_vagas=2,
            data_inicio=datetime.now() + timedelta(days=7),
            data_fim=datetime.now() + timedelta(days=8),
            data_limite_candidatura=datetime.now() + timedelta(days=5),
            ativa=True,
            publicada=True
        )
        self.stdout.write(f'  [OK] Vaga criada: {vaga_livre.titulo}')
        self.stdout.write(f'    Exige vínculo empregatício: {vaga_livre.exige_vinculo_empregaticio}')
        self.stdout.write(f'    Exige documentação: {vaga_livre.exige_documentacao}')
        
        # 2. Vaga COM exigência de documentação (contrato temporário)
        self.stdout.write('\n2. CRIANDO VAGA COM EXIGENCIA DE DOCUMENTACAO - CONTRATO TEMPORARIO:')
        vaga_temporario = VagaEmpresa.objects.create(
            empresa_contratante=empresa,
            titulo='Iluminador - Evento Corporativo',
            descricao='Iluminador para evento corporativo com contrato temporário. Documentação obrigatória.',
            exige_vinculo_empregaticio=True,
            tipo_vinculo='temporario',
            remuneracao=800.00,
            tipo_remuneracao='por_evento',
            quantidade_vagas=1,
            data_inicio=datetime.now() + timedelta(days=14),
            data_fim=datetime.now() + timedelta(days=16),
            data_limite_candidatura=datetime.now() + timedelta(days=10),
            ativa=True,
            publicada=True
        )
        self.stdout.write(f'  [OK] Vaga criada: {vaga_temporario.titulo}')
        self.stdout.write(f'    Exige vínculo empregatício: {vaga_temporario.exige_vinculo_empregaticio}')
        self.stdout.write(f'    Tipo de vínculo: {vaga_temporario.get_tipo_vinculo_display()}')
        self.stdout.write(f'    Exige documentação: {vaga_temporario.exige_documentacao}')
        
        # 3. Vaga COM exigência de documentação (contrato intermitente)
        self.stdout.write('\n3. CRIANDO VAGA COM EXIGENCIA DE DOCUMENTACAO - CONTRATO INTERMITENTE:')
        vaga_intermitente = VagaEmpresa.objects.create(
            empresa_contratante=empresa,
            titulo='Segurança - Evento Intermitente',
            descricao='Segurança para evento com contrato intermitente. Documentação obrigatória.',
            exige_vinculo_empregaticio=True,
            tipo_vinculo='intermitente',
            remuneracao=300.00,
            tipo_remuneracao='por_dia',
            quantidade_vagas=3,
            data_inicio=datetime.now() + timedelta(days=21),
            data_fim=datetime.now() + timedelta(days=22),
            data_limite_candidatura=datetime.now() + timedelta(days=15),
            ativa=True,
            publicada=True
        )
        self.stdout.write(f'  [OK] Vaga criada: {vaga_intermitente.titulo}')
        self.stdout.write(f'    Exige vínculo empregatício: {vaga_intermitente.exige_vinculo_empregaticio}')
        self.stdout.write(f'    Tipo de vínculo: {vaga_intermitente.get_tipo_vinculo_display()}')
        self.stdout.write(f'    Exige documentação: {vaga_intermitente.exige_documentacao}')
        
        # 4. Vaga COM exigência de documentação (terceirizado)
        self.stdout.write('\n4. CRIANDO VAGA COM EXIGENCIA DE DOCUMENTACAO - TERCEIRIZADO:')
        vaga_terceirizado = VagaEmpresa.objects.create(
            empresa_contratante=empresa,
            titulo='Operador de Câmera - Terceirizado',
            descricao='Operador de câmera terceirizado para evento. Documentação obrigatória.',
            exige_vinculo_empregaticio=True,
            tipo_vinculo='terceirizado',
            remuneracao=600.00,
            tipo_remuneracao='por_evento',
            quantidade_vagas=1,
            data_inicio=datetime.now() + timedelta(days=28),
            data_fim=datetime.now() + timedelta(days=30),
            data_limite_candidatura=datetime.now() + timedelta(days=20),
            ativa=True,
            publicada=True
        )
        self.stdout.write(f'  [OK] Vaga criada: {vaga_terceirizado.titulo}')
        self.stdout.write(f'    Exige vínculo empregatício: {vaga_terceirizado.exige_vinculo_empregaticio}')
        self.stdout.write(f'    Tipo de vínculo: {vaga_terceirizado.get_tipo_vinculo_display()}')
        self.stdout.write(f'    Exige documentação: {vaga_terceirizado.exige_documentacao}')
        
        # 5. Resumo das vagas criadas
        self.stdout.write('\n5. RESUMO DAS VAGAS CRIADAS:')
        vagas = VagaEmpresa.objects.filter(empresa_contratante=empresa)
        for vaga in vagas:
            self.stdout.write(f'  - {vaga.titulo}')
            self.stdout.write(f'    Exige vínculo: {vaga.exige_vinculo_empregaticio}')
            if vaga.exige_vinculo_empregaticio:
                self.stdout.write(f'    Tipo de vínculo: {vaga.get_tipo_vinculo_display()}')
            self.stdout.write(f'    Exige documentação: {vaga.exige_documentacao}')
            self.stdout.write(f'    Remuneração: R$ {vaga.remuneracao} ({vaga.get_tipo_remuneracao_display()})')
            self.stdout.write(f'    Vagas disponíveis: {vaga.vagas_disponiveis}')
            self.stdout.write('')
        
        # 6. Estatísticas
        self.stdout.write('6. ESTATISTICAS:')
        total_vagas = vagas.count()
        vagas_sem_vinculo = vagas.filter(exige_vinculo_empregaticio=False).count()
        vagas_com_vinculo = vagas.filter(exige_vinculo_empregaticio=True).count()
        
        self.stdout.write(f'  - Total de vagas: {total_vagas}')
        self.stdout.write(f'  - Vagas sem vínculo (livres): {vagas_sem_vinculo}')
        self.stdout.write(f'  - Vagas com vínculo (documentação obrigatória): {vagas_com_vinculo}')
        
        # Por tipo de vínculo
        temporario = vagas.filter(tipo_vinculo='temporario').count()
        intermitente = vagas.filter(tipo_vinculo='intermitente').count()
        terceirizado = vagas.filter(tipo_vinculo='terceirizado').count()
        
        self.stdout.write(f'    - Contrato temporário: {temporario}')
        self.stdout.write(f'    - Contrato intermitente: {intermitente}')
        self.stdout.write(f'    - Terceirizado: {terceirizado}')
        
        self.stdout.write('\n=== VAGAS CRIADAS COM SUCESSO! ===')
        self.stdout.write('A empresa contratante agora pode:')
        self.stdout.write('1. Publicar vagas sem exigência de documentação (trabalho livre)')
        self.stdout.write('2. Publicar vagas com exigência de documentação (contrato temporário/intermitente)')
        self.stdout.write('3. Definir o tipo de vínculo empregatício necessário')
        self.stdout.write('4. Controlar quais freelancers precisam enviar documentos')
