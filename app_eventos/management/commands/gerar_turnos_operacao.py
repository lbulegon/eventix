"""
Materializa turnos e vagas por turno a partir das regras de recorrência (janela rolante).

Uso:
  python manage.py gerar_turnos_operacao --unidade-id 1
  python manage.py gerar_turnos_operacao --unidade-id 1 --dias 14
  python manage.py gerar_turnos_operacao --todas-unidades --dias 7
"""
from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from app_eventos.models_operacao_continua import UnidadeOperacional
from app_eventos.services.motor_recorrencia_turnos import gerar_turnos_janela


class Command(BaseCommand):
    help = 'Gera turnos operacionais na janela [hoje, hoje+dias) conforme regras de recorrência.'

    def add_arguments(self, parser):
        parser.add_argument('--unidade-id', type=int, default=None)
        parser.add_argument('--todas-unidades', action='store_true')
        parser.add_argument('--dias', type=int, default=7)
        parser.add_argument(
            '--data-inicio',
            type=str,
            default=None,
            help='Data inicial YYYY-MM-DD (opcional; padrão=hoje no fuso atual).',
        )

    def handle(self, *args, **options):
        dias = max(1, options['dias'])
        data_ref = None
        if options['data_inicio']:
            data_ref = datetime.strptime(options['data_inicio'], '%Y-%m-%d').date()

        ids = []
        if options['todas_unidades']:
            ids = list(
                UnidadeOperacional.objects.filter(ativo=True).values_list('id', flat=True)
            )
        elif options['unidade_id']:
            ids = [options['unidade_id']]
        else:
            self.stderr.write(self.style.ERROR('Use --unidade-id N ou --todas-unidades.'))
            return

        total_turnos = 0
        total_vagas = 0
        for uid in ids:
            try:
                u = UnidadeOperacional.objects.get(pk=uid)
            except UnidadeOperacional.DoesNotExist:
                self.stderr.write(self.style.ERROR(f'Unidade id={uid} não encontrada.'))
                continue
            r = gerar_turnos_janela(u, dias_a_frente=dias, data_referencia=data_ref)
            if r.get('erro'):
                self.stdout.write(self.style.WARNING(f'Unidade {uid}: {r["erro"]}'))
                continue
            total_turnos += r['turnos_criados']
            total_vagas += r['vagas_turno_criadas']
            self.stdout.write(
                self.style.SUCCESS(
                    f'Unidade {uid} ({u.nome}): turnos_criados={r["turnos_criados"]}, '
                    f'vagas_turno={r["vagas_turno_criadas"]}, já_existiam={r["turnos_existentes_ignorados"]}'
                )
            )

        self.stdout.write(
            self.style.SUCCESS(f'\nTotal: turnos criados={total_turnos}, vagas de turno criadas={total_vagas}')
        )
        self.stdout.write(f'Referência: {data_ref or timezone.now().date()} | janela={dias} dias')
