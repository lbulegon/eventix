"""
Atribui um freelancer a uma vaga de estabelecimento (ponto de operação) sem candidatura.

Uso:
  python manage.py atribuir_freelancer_vaga --vaga-id 10 --freelance-id 5
  python manage.py atribuir_freelancer_vaga --vaga-id 10 --freelance-id 5 --sem-checar-historico
"""
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand

from app_eventos.models import Freelance, Vaga
from app_eventos.services.atribuicao_vaga_direta import atribuir_freelancer_a_vaga_direto


class Command(BaseCommand):
    help = 'Atribui freelancer a vaga de ponto de operação sem candidatura (ContratoFreelance).'

    def add_arguments(self, parser):
        parser.add_argument('--vaga-id', type=int, required=True)
        parser.add_argument('--freelance-id', type=int, required=True)
        parser.add_argument(
            '--sem-checar-historico',
            action='store_true',
            help='Não exige FreelancerPrestacaoServico para o tenant da vaga.',
        )
        parser.add_argument(
            '--ignorar-limite-vagas',
            action='store_true',
            help='Permite atribuir mesmo com vagas_disponiveis = 0.',
        )

    def handle(self, *args, **options):
        vid = options['vaga_id']
        fid = options['freelance_id']
        try:
            vaga = Vaga.objects.select_related('ponto_operacao', 'empresa_contratante').get(pk=vid)
        except Vaga.DoesNotExist:
            self.stderr.write(self.style.ERROR(f'Vaga id={vid} não encontrada.'))
            return
        try:
            fl = Freelance.objects.get(pk=fid)
        except Freelance.DoesNotExist:
            self.stderr.write(self.style.ERROR(f'Freelance id={fid} não encontrado.'))
            return

        try:
            contrato, meta = atribuir_freelancer_a_vaga_direto(
                fl,
                vaga,
                exigir_prestacao_servico=not options['sem_checar_historico'],
                ignorar_limite_vagas=options['ignorar_limite_vagas'],
            )
        except ValidationError as e:
            for m in getattr(e, 'messages', [str(e)]):
                self.stderr.write(self.style.ERROR(m))
            return

        self.stdout.write(self.style.SUCCESS(meta.get('mensagem', 'OK')))
        self.stdout.write(f'Contrato id={contrato.pk} | criado={meta.get("criado")}')
