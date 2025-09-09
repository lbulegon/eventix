# app_eventos/management/commands/criar_vagas_seguranca_cozinha.py
from django.core.management.base import BaseCommand
from app_eventos.models import Vaga, Funcao, SetorEvento, Evento, EmpresaContratante
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Cria vagas de Segurança e Auxiliar de Cozinha'

    def handle(self, *args, **options):
        # Buscar ou criar funções
        funcao_seguranca, created = Funcao.objects.get_or_create(
            nome='Segurança',
            defaults={
                'descricao': 'Função de segurança para eventos',
                'tipo_funcao_id': 1
            }
        )
        
        funcao_cozinha, created = Funcao.objects.get_or_create(
            nome='Auxiliar de Cozinha',
            defaults={
                'descricao': 'Auxiliar de cozinha para eventos',
                'tipo_funcao_id': 1
            }
        )
        
        self.stdout.write(f'✅ Função Segurança: ID {funcao_seguranca.id}')
        self.stdout.write(f'✅ Função Auxiliar de Cozinha: ID {funcao_cozinha.id}')
        
        # Buscar eventos e setores
        eventos = Evento.objects.all()
        if not eventos.exists():
            self.stdout.write(
                self.style.ERROR('❌ Nenhum evento encontrado! Crie eventos primeiro.')
            )
            return
        
        # Buscar usuário admin para criar as vagas
        try:
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                admin_user = User.objects.first()
        except:
            admin_user = None
        
        if not admin_user:
            self.stdout.write(
                self.style.ERROR('❌ Nenhum usuário encontrado para criar as vagas!')
            )
            return
        
        vagas_criadas = 0
        
        # Criar vagas para cada evento
        for evento in eventos:
            # Buscar setores do evento
            setores = SetorEvento.objects.filter(evento=evento)
            
            if not setores.exists():
                # Criar setores padrão se não existirem
                setores = [
                    SetorEvento.objects.create(
                        nome='Entrada Principal',
                        descricao='Setor de entrada principal do evento',
                        evento=evento
                    ),
                    SetorEvento.objects.create(
                        nome='Área de Alimentação',
                        descricao='Setor de alimentação e cozinha',
                        evento=evento
                    ),
                    SetorEvento.objects.create(
                        nome='Palco Principal',
                        descricao='Setor do palco principal',
                        evento=evento
                    ),
                    SetorEvento.objects.create(
                        nome='Estacionamento',
                        descricao='Setor de estacionamento',
                        evento=evento
                    )
                ]
            
            # Criar vagas de Segurança
            for setor in setores:
                # Segurança
                vaga_seguranca = Vaga.objects.create(
                    titulo=f'Segurança - {setor.nome}',
                    descricao=f'Vaga para Segurança no setor {setor.nome} do evento {evento.nome}. Responsável por manter a segurança e ordem no local.',
                    setor=setor,
                    funcao=funcao_seguranca,
                    quantidade=2,
                    remuneracao=120.00,
                    ativa=True,
                    publicada=True,
                    criado_por=admin_user
                )
                vagas_criadas += 1
                self.stdout.write(f'✅ Vaga criada: {vaga_seguranca.titulo}')
            
            # Criar vagas de Auxiliar de Cozinha (apenas para setores de alimentação)
            setores_cozinha = setores.filter(nome__icontains='alimentação')
            if not setores_cozinha.exists():
                setores_cozinha = setores.filter(nome__icontains='cozinha')
            
            for setor in setores_cozinha:
                vaga_cozinha = Vaga.objects.create(
                    titulo=f'Auxiliar de Cozinha - {setor.nome}',
                    descricao=f'Vaga para Auxiliar de Cozinha no setor {setor.nome} do evento {evento.nome}. Auxiliar na preparação e serviço de alimentos.',
                    setor=setor,
                    funcao=funcao_cozinha,
                    quantidade=3,
                    remuneracao=100.00,
                    ativa=True,
                    publicada=True,
                    criado_por=admin_user
                )
                vagas_criadas += 1
                self.stdout.write(f'✅ Vaga criada: {vaga_cozinha.titulo}')
        
        self.stdout.write(
            self.style.SUCCESS(f'\n🎯 Total de {vagas_criadas} vagas criadas!')
        )
        self.stdout.write(
            self.style.SUCCESS('✅ Vagas de Segurança e Auxiliar de Cozinha criadas com sucesso!')
        )
