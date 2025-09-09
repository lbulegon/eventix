from django.core.management.base import BaseCommand
from app_eventos.models import Vaga, Funcao

class Command(BaseCommand):
    help = 'Altera todas as vagas para Segurança'

    def handle(self, *args, **options):
        # Buscar ou criar função Segurança
        funcao, created = Funcao.objects.get_or_create(
            nome='Segurança',
            defaults={'descricao': 'Segurança', 'tipo_funcao_id': 1}
        )
        
        # Alterar todas as vagas
        vagas = Vaga.objects.all()
        for vaga in vagas:
            vaga.funcao = funcao
            vaga.titulo = f'Segurança - {vaga.setor.nome if vaga.setor else "Setor"}'
            vaga.save()
        
        self.stdout.write(f'✅ {vagas.count()} vagas alteradas para Segurança!')
