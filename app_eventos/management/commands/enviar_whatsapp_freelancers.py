"""
Comando para enviar WhatsApp/SMS para todos os freelancers cadastrados
"""
from django.core.management.base import BaseCommand
from app_eventos.models import Freelance, EmpresaContratante
from app_eventos.services.twilio_service import TwilioService


class Command(BaseCommand):
    help = 'Envia mensagem WhatsApp/SMS para todos os freelancers cadastrados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--mensagem',
            type=str,
            required=True,
            help='Mensagem a ser enviada'
        )
        parser.add_argument(
            '--canal',
            type=str,
            default='whatsapp',
            choices=['whatsapp', 'sms'],
            help='Canal: whatsapp ou sms (padrão: whatsapp)'
        )
        parser.add_argument(
            '--apenas-completos',
            action='store_true',
            help='Enviar apenas para freelancers com cadastro completo'
        )
        parser.add_argument(
            '--apenas-verificados',
            action='store_true',
            help='Enviar apenas para freelancers com telefone verificado'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Apenas simula, não envia realmente'
        )
        parser.add_argument(
            '--funcao',
            type=str,
            help='Filtrar por função específica (nome da função)'
        )

    def handle(self, *args, **options):
        mensagem = options['mensagem']
        canal = options['canal']
        apenas_completos = options['apenas_completos']
        apenas_verificados = options['apenas_verificados']
        dry_run = options['dry_run']
        funcao_nome = options.get('funcao')

        self.stdout.write('\n' + '=' * 70)
        self.stdout.write('📱 ENVIO DE MENSAGENS PARA FREELANCERS')
        self.stdout.write('=' * 70 + '\n')

        # Buscar freelancers
        freelancers = Freelance.objects.filter(
            telefone__isnull=False
        ).exclude(telefone='')

        # Filtros
        if apenas_completos:
            freelancers = freelancers.filter(cadastro_completo=True)
            self.stdout.write('🔍 Filtro: Apenas cadastros completos')

        if apenas_verificados:
            freelancers = freelancers.filter(notificacoes_ativas=True)
            self.stdout.write('🔍 Filtro: Apenas com notificações ativas')

        if funcao_nome:
            freelancers = freelancers.filter(funcoes__funcao__nome__icontains=funcao_nome).distinct()
            self.stdout.write(f'🔍 Filtro: Função contém "{funcao_nome}"')

        total_freelancers = freelancers.count()

        if total_freelancers == 0:
            self.stdout.write(
                self.style.WARNING('\n⚠️  Nenhum freelancer encontrado com os filtros especificados.')
            )
            return

        self.stdout.write(f'\n📊 Freelancers encontrados: {total_freelancers}')
        self.stdout.write(f'📨 Canal: {canal.upper()}')
        self.stdout.write(f'💬 Mensagem:\n{"-" * 70}')
        self.stdout.write(mensagem)
        self.stdout.write('-' * 70)

        # Modo dry-run
        if dry_run:
            self.stdout.write('\n🧪 MODO DRY-RUN (simulação)\n')
            self.stdout.write('Destinatários:')
            for i, freelancer in enumerate(freelancers[:10], 1):
                self.stdout.write(f'  {i}. {freelancer.nome_completo} - {freelancer.telefone}')
            if total_freelancers > 10:
                self.stdout.write(f'  ... e mais {total_freelancers - 10} freelancers')
            self.stdout.write('\n' + self.style.SUCCESS('✅ Simulação concluída. Use sem --dry-run para enviar.'))
            return

        # Confirmação
        self.stdout.write('\n' + self.style.WARNING('⚠️  ATENÇÃO: Esta operação enviará mensagens reais!'))
        confirmacao = input('\nDeseja continuar? (digite SIM em maiúsculas): ')

        if confirmacao != 'SIM':
            self.stdout.write(self.style.ERROR('\n❌ Operação cancelada pelo usuário.'))
            return

        # Inicializar Twilio
        twilio = TwilioService()

        if not twilio.is_configured():
            self.stdout.write(
                self.style.ERROR('\n❌ Twilio não configurado! Configure as variáveis de ambiente:')
            )
            self.stdout.write('   - TWILIO_ACCOUNT_SID')
            self.stdout.write('   - TWILIO_AUTH_TOKEN')
            self.stdout.write('   - TWILIO_MESSAGING_SERVICE_SID')
            return

        # Enviar mensagens
        self.stdout.write('\n📤 Enviando mensagens...\n')

        stats = {
            'total': 0,
            'enviados': 0,
            'erros': 0,
            'invalidos': 0
        }

        for freelancer in freelancers:
            stats['total'] += 1

            # Formatar telefone para E.164
            try:
                phone_e164 = twilio.format_phone_e164(freelancer.telefone)

                # Validar formato
                if not twilio.validate_phone_e164(phone_e164):
                    self.stdout.write(
                        self.style.WARNING(f'  ⚠️  {freelancer.nome_completo}: Telefone inválido ({freelancer.telefone})')
                    )
                    stats['invalidos'] += 1
                    continue

                # Enviar mensagem
                result = twilio.send_with_fallback(phone_e164, mensagem, canal)

                if result['success']:
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✓ {freelancer.nome_completo}: {phone_e164} ({result["channel_used"]})')
                    )
                    stats['enviados'] += 1
                else:
                    self.stdout.write(
                        self.style.ERROR(f'  ✗ {freelancer.nome_completo}: Erro - {result["error"]}')
                    )
                    stats['erros'] += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  ✗ {freelancer.nome_completo}: Exceção - {str(e)}')
                )
                stats['erros'] += 1

        # Resumo final
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write('📊 RESUMO DO ENVIO')
        self.stdout.write('=' * 70)
        self.stdout.write(f'Total de freelancers: {stats["total"]}')
        self.stdout.write(
            self.style.SUCCESS(f'✓ Enviados com sucesso: {stats["enviados"]}')
        )
        if stats['erros'] > 0:
            self.stdout.write(
                self.style.ERROR(f'✗ Erros: {stats["erros"]}')
            )
        if stats['invalidos'] > 0:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Telefones inválidos: {stats["invalidos"]}')
            )

        taxa_sucesso = (stats['enviados'] / stats['total'] * 100) if stats['total'] > 0 else 0
        self.stdout.write(f'\n📈 Taxa de sucesso: {taxa_sucesso:.1f}%')
        self.stdout.write('=' * 70 + '\n')

        if stats['enviados'] > 0:
            self.stdout.write(
                self.style.SUCCESS('🎉 Envio concluído!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('⚠️  Nenhuma mensagem foi enviada.')
            )

