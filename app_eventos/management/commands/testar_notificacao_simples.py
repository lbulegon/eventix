"""
Comando simples para testar notificações sem travamento
"""
from django.core.management.base import BaseCommand
from app_eventos.models import Vaga, Freelance
from app_eventos.services.notificacao_vagas_mock import NotificacaoVagasServiceMock


class Command(BaseCommand):
    help = 'Testa notificação simples sem travamento'

    def handle(self, *args, **options):
        self.stdout.write('🧪 TESTE SIMPLES DE NOTIFICAÇÃO')
        self.stdout.write('=' * 50)
        
        # Buscar primeira vaga ativa
        vaga = Vaga.objects.filter(ativa=True).first()
        
        if not vaga:
            self.stdout.write('❌ Nenhuma vaga ativa encontrada')
            return
        
        self.stdout.write(f'📋 Vaga: {vaga.funcao.nome if vaga.funcao else "Sem função"}')
        
        # Usar serviço mock
        notificacao_service = NotificacaoVagasServiceMock()
        
        # Testar notificação
        resultado = notificacao_service.notificar_nova_vaga(vaga)
        
        if 'erro' in resultado:
            self.stdout.write(f'❌ Erro: {resultado["erro"]}')
        else:
            self.stdout.write(f'✅ Sucesso: {resultado.get("enviados", 0)} notificações simuladas')
            self.stdout.write(f'📊 Total freelancers: {resultado.get("total_freelancers", 0)}')
        
        self.stdout.write('✅ Teste concluído sem travamento!')
