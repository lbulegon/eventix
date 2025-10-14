"""
Comando para verificar documentos próximos ao vencimento e expirados
Execute diariamente via cron
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from app_eventos.signals_documentos import (
    verificar_documentos_proximos_vencimento,
    marcar_documentos_expirados
)


class Command(BaseCommand):
    help = 'Verifica documentos próximos ao vencimento e marca expirados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--apenas-vencimento',
            action='store_true',
            help='Apenas verifica vencimentos, não marca como expirado',
        )
        parser.add_argument(
            '--apenas-expirados',
            action='store_true',
            help='Apenas marca expirados, não notifica vencimentos',
        )

    def handle(self, *args, **options):
        self.stdout.write(f'\n🔍 Verificando documentos... ({timezone.now()})\n')
        
        apenas_vencimento = options['apenas_vencimento']
        apenas_expirados = options['apenas_expirados']
        
        total_notificacoes = 0
        total_expirados = 0
        
        # Verificar documentos próximos ao vencimento
        if not apenas_expirados:
            self.stdout.write('📅 Verificando documentos próximos ao vencimento...')
            try:
                total_notificacoes = verificar_documentos_proximos_vencimento()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ {total_notificacoes} notificação(ões) de vencimento criada(s)'
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Erro ao verificar vencimentos: {e}')
                )
        
        # Marcar documentos expirados
        if not apenas_vencimento:
            self.stdout.write('\n⏰ Marcando documentos expirados...')
            try:
                total_expirados = marcar_documentos_expirados()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ {total_expirados} documento(s) marcado(s) como expirado(s)'
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Erro ao marcar expirados: {e}')
                )
        
        # Resumo
        self.stdout.write(f'\n📊 Resumo:')
        self.stdout.write(f'   - Notificações de vencimento: {total_notificacoes}')
        self.stdout.write(f'   - Documentos marcados como expirados: {total_expirados}')
        self.stdout.write(f'\n✅ Verificação concluída!\n')

