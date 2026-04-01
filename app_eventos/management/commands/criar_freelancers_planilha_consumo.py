"""
Cria no banco os freelancers listados na planilha de consumo/pagamento (Março 2024).
Nomes: Sol, Duda, Matheus, Adriano, Ricardo, Patrick, Lucas (Duda em duas colunas = uma pessoa).

Uso:
  python manage.py criar_freelancers_planilha_consumo
  python manage.py criar_freelancers_planilha_consumo --senha minhaSenha
  python manage.py criar_freelancers_planilha_consumo --empresa-id 1

Com --empresa-id, cada freelancer da planilha e associado a essa EmpresaContratante na lista
"ja prestaram servico" (FreelancerPrestacaoServico), incluindo contas que ja existiam.

Credenciais padrao (se nao passar --senha): senha123
Emails fictícios: <nome>.planilha.consumo@eventix.local (apenas para login de teste)
"""
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand

from app_eventos.models import EmpresaContratante, Freelance, FreelancerPrestacaoServico, User


# Colunas da planilha "Consumo" (nomes únicos)
FREELANCERS_PLANILHA = [
    {'nome_completo': 'Sol', 'username': 'sol_planilha_consumo', 'cpf': '100.100.100-10'},
    {'nome_completo': 'Duda', 'username': 'duda_planilha_consumo', 'cpf': '100.100.100-11'},
    {'nome_completo': 'Matheus', 'username': 'matheus_planilha_consumo', 'cpf': '100.100.100-12'},
    {'nome_completo': 'Adriano', 'username': 'adriano_planilha_consumo', 'cpf': '100.100.100-13'},
    {'nome_completo': 'Ricardo', 'username': 'ricardo_planilha_consumo', 'cpf': '100.100.100-14'},
    {'nome_completo': 'Patrick', 'username': 'patrick_planilha_consumo', 'cpf': '100.100.100-15'},
    {'nome_completo': 'Lucas', 'username': 'lucas_planilha_consumo', 'cpf': '100.100.100-16'},
]


class Command(BaseCommand):
    help = 'Cria freelancers da planilha Consumo (pagamento) com usuário Django'

    def add_arguments(self, parser):
        parser.add_argument(
            '--senha',
            type=str,
            default='senha123',
            help='Senha inicial para todos os logins criados (padrão: senha123)',
        )
        parser.add_argument(
            '--empresa-id',
            type=int,
            default=None,
            help='ID da EmpresaContratante: vincula todos os freelancers da planilha à lista "já prestaram serviço".',
        )

    def handle(self, *args, **options):
        senha = options['senha']
        empresa_id = options['empresa_id']
        criados = 0
        pulados = 0
        vinculados = 0
        ja_vinculados = 0

        if empresa_id is not None:
            if not EmpresaContratante.objects.filter(pk=empresa_id).exists():
                self.stderr.write(self.style.ERROR(f'EmpresaContratante id={empresa_id} nao encontrada.'))
                return

        def vincular_empresa(freelance_obj):
            nonlocal vinculados, ja_vinculados
            if empresa_id is None or not freelance_obj:
                return
            _, created = FreelancerPrestacaoServico.objects.get_or_create(
                empresa_contratante_id=empresa_id,
                freelance=freelance_obj,
                defaults={'ativo': True},
            )
            if created:
                vinculados += 1
            else:
                ja_vinculados += 1

        for row in FREELANCERS_PLANILHA:
            username = row['username']
            email = f"{username.split('_')[0]}.planilha.consumo@eventix.local"

            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.WARNING(f'Ja existe usuario {username}, nao recria.'))
                pulados += 1
                user = User.objects.get(username=username)
                fl = Freelance.objects.filter(usuario=user).first()
                if not fl:
                    fl = Freelance.objects.filter(cpf=row['cpf']).first()
                if fl:
                    vincular_empresa(fl)
                elif empresa_id:
                    self.stdout.write(
                        self.style.WARNING(f'  Nao foi encontrado Freelance para {username}; nao vinculado.')
                    )
                continue

            if Freelance.objects.filter(cpf=row['cpf']).exists():
                self.stdout.write(self.style.WARNING(f"CPF {row['cpf']} ja usado por outro freelancer, ignorando {username}."))
                pulados += 1
                continue

            user = User.objects.create(
                username=username,
                email=email,
                first_name=row['nome_completo'][:30],
                last_name='',
                password=make_password(senha),
                tipo_usuario='freelancer',
                is_active=True,
            )

            fl = Freelance.objects.create(
                usuario=user,
                nome_completo=row['nome_completo'],
                cpf=row['cpf'],
                telefone='',
            )
            criados += 1
            self.stdout.write(self.style.SUCCESS(f'OK: {row["nome_completo"]} -> {username} ({email})'))
            vincular_empresa(fl)

        self.stdout.write(self.style.SUCCESS(f'\nCriados: {criados} | Contas ja existentes (nao recriadas): {pulados}'))
        if empresa_id is not None:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Vinculados a empresa id={empresa_id}: novos na lista={vinculados} | ja estavam na lista={ja_vinculados}'
                )
            )
        if criados:
            self.stdout.write(self.style.SUCCESS(f'Senha definida para os novos usuarios: {senha}'))
