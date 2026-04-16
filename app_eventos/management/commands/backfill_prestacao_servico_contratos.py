"""
Garante FreelancerPrestacaoServico para pares (empresa, freelancer) derivados de
ContratoFreelance ativo ou finalizado — útil após introdução da lista restrita ou
para dados criados antes dos signals.

Não inclui apenas candidaturas (regra de negócio: vínculo por serviço ou cadastro explícito).

Uso:
  python manage.py backfill_prestacao_servico_contratos
  python manage.py backfill_prestacao_servico_contratos --empresa-id 1
  python manage.py backfill_prestacao_servico_contratos --dry-run
"""
from django.core.management.base import BaseCommand

from app_eventos.models import ContratoFreelance
from app_eventos.models_freelancer_empresa import FreelancerPrestacaoServico


OBS_BACKFILL = (
    'Backfill a partir de histórico de ContratoFreelance (ativo ou finalizado).'
)


class Command(BaseCommand):
    help = (
        'Cria registos FreelancerPrestacaoServico a partir de contratos '
        'ativos ou finalizados (não cancelados).'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--empresa-id',
            type=int,
            default=None,
            help='Limitar à EmpresaContratante (via vaga.empresa_contratante).',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Apenas estimar quantos pares novos existiriam, sem gravar.',
        )

    def handle(self, *args, **options):
        empresa_id = options['empresa_id']
        dry_run = options['dry_run']

        qs = (
            ContratoFreelance.objects.filter(status__in=('ativo', 'finalizado'))
            .select_related('vaga')
            .order_by('id')
        )
        if empresa_id is not None:
            qs = qs.filter(vaga__empresa_contratante_id=empresa_id)

        pares_unicos = {}
        ignorados = 0
        for c in qs.iterator(chunk_size=500):
            if not c.vaga_id:
                ignorados += 1
                continue
            eid = getattr(c.vaga, 'empresa_contratante_id', None)
            if not eid:
                ignorados += 1
                continue
            key = (eid, c.freelance_id)
            if key not in pares_unicos:
                pares_unicos[key] = c.id

        criados = 0
        ja_existia = 0

        for (eid, fid), contrato_id in pares_unicos.items():
            if dry_run:
                if FreelancerPrestacaoServico.objects.filter(
                    empresa_contratante_id=eid,
                    freelance_id=fid,
                ).exists():
                    ja_existia += 1
                else:
                    criados += 1
                    self.stdout.write(
                        f'[dry-run] criaria: empresa={eid} freelance={fid} (ex.: contrato={contrato_id})'
                    )
                continue

            _obj, created = FreelancerPrestacaoServico.objects.get_or_create(
                empresa_contratante_id=eid,
                freelance_id=fid,
                defaults={'ativo': True, 'observacoes': OBS_BACKFILL},
            )
            if created:
                criados += 1
            else:
                ja_existia += 1

        prefix = '[dry-run] ' if dry_run else ''
        self.stdout.write(
            self.style.SUCCESS(
                f'{prefix}Pares únicos a partir de contratos: {len(pares_unicos)}. '
                f'Novos: {criados}. Já existentes: {ja_existia}. '
                f'Contratos ignorados (sem vaga/empresa): {ignorados}.'
            )
        )
