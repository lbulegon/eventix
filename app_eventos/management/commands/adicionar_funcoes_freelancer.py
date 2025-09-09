# app_eventos/management/commands/adicionar_funcoes_freelancer.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from app_eventos.models import Freelance, FreelancerFuncao, Funcao, TipoFuncao

User = get_user_model()


class Command(BaseCommand):
    help = 'Adiciona funções específicas para um freelancer'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username do freelancer',
        )
        parser.add_argument(
            '--funcoes',
            type=str,
            nargs='+',
            help='Lista de funções para adicionar (ex: "Operador de Som" "Técnico de Palco")',
        )
        parser.add_argument(
            '--nivel',
            type=str,
            default='intermediario',
            choices=['iniciante', 'intermediario', 'avancado', 'expert'],
            help='Nível de proficiência (padrão: intermediario)',
        )
        parser.add_argument(
            '--listar-funcoes',
            action='store_true',
            help='Lista todas as funções disponíveis',
        )

    def handle(self, *args, **options):
        if options['listar_funcoes']:
            self.listar_funcoes_disponiveis()
            return

        username = options['username']
        if not username:
            self.stdout.write(
                self.style.ERROR('❌ Username é obrigatório! Use --username')
            )
            return

        funcoes_nomes = options['funcoes']
        nivel = options['nivel']

        try:
            # Buscar usuário
            user = User.objects.get(username=username)
            self.stdout.write(f'👤 Usuário encontrado: {user.username} ({user.email})')
            
            # Verificar se é freelancer
            if user.tipo_usuario != 'freelancer':
                self.stdout.write(
                    self.style.ERROR(f'❌ Usuário {username} não é um freelancer!')
                )
                return

            # Buscar perfil freelancer
            try:
                freelance = user.freelance
                self.stdout.write(f'📋 Perfil freelancer encontrado: {freelance.nome_completo}')
            except Freelance.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'❌ Perfil freelancer não encontrado para {username}!')
                )
                return

            # Adicionar funções
            funcoes_adicionadas = []
            for funcao_nome in funcoes_nomes:
                try:
                    funcao = Funcao.objects.get(nome=funcao_nome)
                    
                    # Verificar se já existe
                    freelancer_funcao, created = FreelancerFuncao.objects.get_or_create(
                        freelancer=freelance,
                        funcao=funcao,
                        defaults={'nivel': nivel}
                    )
                    
                    if created:
                        funcoes_adicionadas.append(funcao_nome)
                        self.stdout.write(
                            self.style.SUCCESS(f'✅ Função "{funcao_nome}" adicionada (nível: {nivel})')
                        )
                    else:
                        # Atualizar nível se já existe
                        freelancer_funcao.nivel = nivel
                        freelancer_funcao.save()
                        self.stdout.write(
                            self.style.WARNING(f'🔄 Função "{funcao_nome}" atualizada (nível: {nivel})')
                        )
                        
                except Funcao.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Função "{funcao_nome}" não encontrada!')
                    )

            # Resumo
            self.stdout.write(f'\n📊 Resumo:')
            self.stdout.write(f'   - Usuário: {freelance.nome_completo}')
            self.stdout.write(f'   - Funções adicionadas: {len(funcoes_adicionadas)}')
            self.stdout.write(f'   - Total de funções: {freelance.funcoes.count()}')
            
            # Listar funções atuais
            self.stdout.write(f'\n🎯 Funções atuais do freelancer:')
            for ff in freelance.funcoes.all():
                self.stdout.write(f'   - {ff.funcao.nome} ({ff.get_nivel_display()})')

        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'❌ Usuário "{username}" não encontrado!')
            )

    def listar_funcoes_disponiveis(self):
        """Lista todas as funções disponíveis"""
        self.stdout.write('📋 Funções disponíveis:')
        self.stdout.write('')
        
        tipos = TipoFuncao.objects.filter(ativo=True).prefetch_related('funcoes')
        
        for tipo in tipos:
            self.stdout.write(f'🏷️  {tipo.nome}:')
            funcoes = tipo.funcoes.filter(ativo=True)
            for funcao in funcoes:
                self.stdout.write(f'   - {funcao.nome}')
            self.stdout.write('')
