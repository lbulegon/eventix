# app_eventos/management/commands/adicionar_freelancers_existentes.py
from django.core.management.base import BaseCommand
from django.db import transaction
from app_eventos.models import User, GrupoUsuario


class Command(BaseCommand):
    help = 'Adiciona todos os usuários freelancers existentes ao grupo global de freelancers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra o que seria feito sem executar as alterações',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        
        # Busca todos os usuários freelancers
        freelancers = User.objects.filter(tipo_usuario='freelancer', ativo=True)
        
        if not freelancers.exists():
            self.stdout.write(
                self.style.WARNING('Nenhum usuário freelancer encontrado.')
            )
            return
        
        self.stdout.write(f'Encontrados {freelancers.count()} usuários freelancers.')
        
        # Busca o grupo global de freelancers (sem empresa específica)
        grupo_freelancers = GrupoUsuario.objects.filter(
            nome='Freelancers Global',
            empresa_contratante=None,
            ativo=True
        ).first()
        
        if not grupo_freelancers:
            self.stdout.write(
                self.style.ERROR('Grupo global de freelancers não encontrado. Execute primeiro: python manage.py popular_grupos_permissoes')
            )
            return
        
        self.stdout.write(f'Grupo encontrado: {grupo_freelancers.nome} (Global)')
        
        if dry_run:
            self.stdout.write('\n=== MODO DRY-RUN - Nenhuma alteração será feita ===')
        
        with transaction.atomic():
            adicionados = 0
            ja_estavam = 0
            
            for freelancer in freelancers:
                # Verifica se já está no grupo
                ja_no_grupo = freelancer.get_grupos_ativos().filter(
                    grupo=grupo_freelancers
                ).exists()
                
                if ja_no_grupo:
                    ja_estavam += 1
                    self.stdout.write(f'  ✓ {freelancer.username} - Já está no grupo')
                else:
                    if not dry_run:
                        freelancer.adicionar_ao_grupo(grupo_freelancers, ativo=True)
                        adicionados += 1
                        self.stdout.write(f'  + {freelancer.username} - Adicionado ao grupo')
                    else:
                        adicionados += 1
                        self.stdout.write(f'  + {freelancer.username} - Seria adicionado ao grupo')
        
        # Resumo
        self.stdout.write('\n=== RESUMO ===')
        self.stdout.write(f'Total de freelancers: {freelancers.count()}')
        self.stdout.write(f'Já estavam no grupo: {ja_estavam}')
        
        if dry_run:
            self.stdout.write(f'Seriam adicionados: {adicionados}')
            self.stdout.write('\nPara executar as alterações, rode o comando sem --dry-run')
        else:
            self.stdout.write(f'Adicionados ao grupo: {adicionados}')
            self.stdout.write(
                self.style.SUCCESS('Freelancers adicionados ao grupo global com sucesso!')
            )