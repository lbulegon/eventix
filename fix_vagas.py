import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from app_eventos.models import Vaga, Funcao

# Buscar ou criar função Segurança
funcao_seguranca, created = Funcao.objects.get_or_create(
    nome='Segurança',
    defaults={
        'descricao': 'Função de segurança para eventos',
        'tipo_funcao_id': 1
    }
)

print(f'Função Segurança: ID {funcao_seguranca.id}')

# Buscar todas as vagas
vagas = Vaga.objects.all()
print(f'Total de vagas: {vagas.count()}')

# Alterar todas as vagas
for vaga in vagas:
    vaga.funcao = funcao_seguranca
    vaga.titulo = f'Segurança - {vaga.setor.nome if vaga.setor else "Setor"}'
    vaga.descricao = f'Vaga para Segurança no setor {vaga.setor.nome if vaga.setor else "Setor"}.'
    vaga.save()

print(f'✅ {vagas.count()} vagas alteradas para Segurança!')
