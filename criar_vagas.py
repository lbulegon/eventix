import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from app_eventos.models import Vaga, Funcao, SetorEvento, Evento
from django.contrib.auth import get_user_model

User = get_user_model()

print("🔧 Criando vagas de Segurança e Auxiliar de Cozinha...")

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

print(f'✅ Função Segurança: ID {funcao_seguranca.id}')
print(f'✅ Função Auxiliar de Cozinha: ID {funcao_cozinha.id}')

# Buscar eventos
eventos = Evento.objects.all()
print(f'📊 Eventos encontrados: {eventos.count()}')

if not eventos.exists():
    print('❌ Nenhum evento encontrado!')
    exit()

# Buscar usuário admin
admin_user = User.objects.filter(is_superuser=True).first()
if not admin_user:
    admin_user = User.objects.first()

if not admin_user:
    print('❌ Nenhum usuário encontrado!')
    exit()

vagas_criadas = 0

# Criar vagas para cada evento
for evento in eventos:
    print(f'\n📅 Processando evento: {evento.nome}')
    
    # Buscar setores do evento
    setores = SetorEvento.objects.filter(evento=evento)
    
    if not setores.exists():
        # Criar setores padrão
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
        print(f'✅ {len(setores)} setores criados para o evento')
    
    # Criar vagas de Segurança
    for setor in setores:
        vaga_seguranca = Vaga.objects.create(
            titulo=f'Segurança - {setor.nome}',
            descricao=f'Vaga para Segurança no setor {setor.nome} do evento {evento.nome}.',
            setor=setor,
            funcao=funcao_seguranca,
            quantidade=2,
            remuneracao=120.00,
            ativa=True,
            publicada=True,
            criado_por=admin_user
        )
        vagas_criadas += 1
        print(f'✅ Vaga criada: {vaga_seguranca.titulo}')
    
    # Criar vagas de Auxiliar de Cozinha (apenas para setores de alimentação)
    setores_cozinha = setores.filter(nome__icontains='alimentação')
    if not setores_cozinha.exists():
        setores_cozinha = setores.filter(nome__icontains='cozinha')
    
    for setor in setores_cozinha:
        vaga_cozinha = Vaga.objects.create(
            titulo=f'Auxiliar de Cozinha - {setor.nome}',
            descricao=f'Vaga para Auxiliar de Cozinha no setor {setor.nome} do evento {evento.nome}.',
            setor=setor,
            funcao=funcao_cozinha,
            quantidade=3,
            remuneracao=100.00,
            ativa=True,
            publicada=True,
            criado_por=admin_user
        )
        vagas_criadas += 1
        print(f'✅ Vaga criada: {vaga_cozinha.titulo}')

print(f'\n🎯 Total de {vagas_criadas} vagas criadas!')
print('✅ Vagas de Segurança e Auxiliar de Cozinha criadas com sucesso!')
