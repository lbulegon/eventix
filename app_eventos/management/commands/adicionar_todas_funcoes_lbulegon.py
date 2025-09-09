# app_eventos/management/commands/adicionar_todas_funcoes_lbulegon.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from app_eventos.models import Freelance, FreelancerFuncao, Funcao

User = get_user_model()


class Command(BaseCommand):
    help = 'Adiciona todas as funções disponíveis para o usuário lbulegon'

    def handle(self, *args, **options):
        email = 'lbulegon@gmail.com'
        
        try:
            # Buscar usuário pelo email
            user = User.objects.get(email=email)
            self.stdout.write(f'👤 Usuário encontrado: {user.username} ({user.email})')
            
            # Verificar se é freelancer
            if user.tipo_usuario != 'freelancer':
                self.stdout.write(
                    self.style.ERROR(f'❌ Usuário {user.username} não é um freelancer!')
                )
                return

            # Buscar perfil freelancer
            try:
                freelance = user.freelance
                self.stdout.write(f'📋 Perfil freelancer encontrado: {freelance.nome_completo}')
            except Freelance.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'❌ Perfil freelancer não encontrado para {user.username}!')
                )
                return

            # Buscar todas as funções ativas
            funcoes = Funcao.objects.filter(ativo=True)
            self.stdout.write(f'📝 Encontradas {funcoes.count()} funções ativas')

            # Adicionar todas as funções
            funcoes_adicionadas = 0
            funcoes_atualizadas = 0
            
            for funcao in funcoes:
                freelancer_funcao, created = FreelancerFuncao.objects.get_or_create(
                    freelancer=freelance,
                    funcao=funcao,
                    defaults={'nivel': 'intermediario'}
                )
                
                if created:
                    funcoes_adicionadas += 1
                    self.stdout.write(f'✅ {funcao.nome} (adicionada)')
                else:
                    # Atualizar nível se já existe
                    freelancer_funcao.nivel = 'intermediario'
                    freelancer_funcao.save()
                    funcoes_atualizadas += 1
                    self.stdout.write(f'🔄 {funcao.nome} (atualizada)')

            # Resumo final
            self.stdout.write(f'\n🎯 RESUMO FINAL:')
            self.stdout.write(f'   - Usuário: {freelance.nome_completo}')
            self.stdout.write(f'   - Funções adicionadas: {funcoes_adicionadas}')
            self.stdout.write(f'   - Funções atualizadas: {funcoes_atualizadas}')
            self.stdout.write(f'   - Total de funções: {freelance.funcoes.count()}')
            
            # Verificar se cadastro está completo
            if freelance.cadastro_completo:
                self.stdout.write(f'✅ Cadastro completo: SIM')
            else:
                self.stdout.write(f'⚠️  Cadastro completo: NÃO')
                
            self.stdout.write(f'\n🚀 Agora o usuário {user.username} deve conseguir ver as vagas no Flutter!')

        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'❌ Usuário com email "{email}" não encontrado!')
            )
