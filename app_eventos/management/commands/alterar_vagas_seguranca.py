# app_eventos/management/commands/alterar_vagas_seguranca.py
from django.core.management.base import BaseCommand
from app_eventos.models import Vaga, Funcao

class Command(BaseCommand):
    help = 'Altera todas as vagas para a função de Segurança'

    def handle(self, *args, **options):
        # Buscar ou criar a função de Segurança
        funcao_seguranca, created = Funcao.objects.get_or_create(
            nome='Segurança',
            defaults={
                'descricao': 'Função de segurança para eventos',
                'tipo_funcao_id': 1  # Assumindo que existe um tipo_funcao com ID 1
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Função "Segurança" criada com ID: {funcao_seguranca.id}')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Função "Segurança" encontrada com ID: {funcao_seguranca.id}')
            )
        
        # Buscar todas as vagas
        vagas = Vaga.objects.all()
        total_vagas = vagas.count()
        
        self.stdout.write(f'📊 Total de vagas encontradas: {total_vagas}')
        
        if total_vagas == 0:
            self.stdout.write(
                self.style.WARNING('⚠️ Nenhuma vaga encontrada no sistema!')
            )
            return
        
        # Alterar todas as vagas para a função de Segurança
        vagas_atualizadas = 0
        for vaga in vagas:
            vaga.funcao = funcao_seguranca
            vaga.titulo = f'Segurança - {vaga.setor.nome if vaga.setor else "Setor"}'
            vaga.descricao = f'Vaga para Segurança no setor {vaga.setor.nome if vaga.setor else "Setor"} do evento {vaga.setor.evento.nome if vaga.setor and vaga.setor.evento else "Evento"}.'
            vaga.save()
            vagas_atualizadas += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ {vagas_atualizadas} vagas alteradas para a função de Segurança!')
        )
        
        # Mostrar algumas vagas como exemplo
        self.stdout.write('\n📋 Exemplos de vagas alteradas:')
        for vaga in vagas[:5]:
            self.stdout.write(f'   - {vaga.titulo} (ID: {vaga.id})')
        
        if total_vagas > 5:
            self.stdout.write(f'   ... e mais {total_vagas - 5} vagas')
        
        self.stdout.write(
            self.style.SUCCESS(f'\n🎯 Todas as vagas agora são para a função de Segurança!')
        )
