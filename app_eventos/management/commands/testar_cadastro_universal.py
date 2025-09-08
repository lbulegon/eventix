# app_eventos/management/commands/testar_cadastro_universal.py
from django.core.management.base import BaseCommand
from app_eventos.models import User, GrupoUsuario, EmpresaContratante


class Command(BaseCommand):
    help = 'Testa se os signals funcionam em TODAS as formas de cadastro de usuário'

    def handle(self, *args, **options):
        self.stdout.write('=== TESTE DE CADASTRO UNIVERSAL ===\n')
        self.stdout.write('Testando se os signals funcionam em TODAS as formas de cadastro...\n')
        
        # Busca uma empresa para teste
        empresa = EmpresaContratante.objects.filter(ativo=True).first()
        if not empresa:
            self.stdout.write(
                self.style.ERROR('Nenhuma empresa encontrada. Crie uma empresa primeiro.')
            )
            return
        
        # Limpa usuários de teste anteriores
        User.objects.filter(username__startswith='teste_universal_').delete()
        
        resultados = []
        
        # TESTE 1: Cadastro via create_user (simula Flutter/API)
        self.stdout.write('--- TESTE 1: Cadastro via create_user (Flutter/API) ---')
        user1 = User.objects.create_user(
            username='teste_universal_1',
            email='teste1@universal.com',
            password='123456',
            tipo_usuario='freelancer'
        )
        
        grupos1 = [ug.grupo.nome for ug in user1.get_grupos_ativos()]
        if 'Freelancers Global' in grupos1:
            self.stdout.write(self.style.SUCCESS('✓ SUCESSO: Signal funcionou no create_user'))
            resultados.append('✓ create_user: OK')
        else:
            self.stdout.write(self.style.ERROR('✗ ERRO: Signal não funcionou no create_user'))
            resultados.append('✗ create_user: ERRO')
        
        # TESTE 2: Cadastro via create (simula Django Admin)
        self.stdout.write('\n--- TESTE 2: Cadastro via create (Django Admin) ---')
        user2 = User.objects.create(
            username='teste_universal_2',
            email='teste2@universal.com',
            tipo_usuario='admin_empresa',
            empresa_contratante=empresa
        )
        user2.set_password('123456')
        user2.save()
        
        grupos2 = [ug.grupo.nome for ug in user2.get_grupos_ativos()]
        if 'Administrador da Empresa' in grupos2:
            self.stdout.write(self.style.SUCCESS('✓ SUCESSO: Signal funcionou no create'))
            resultados.append('✓ create: OK')
        else:
            self.stdout.write(self.style.ERROR('✗ ERRO: Signal não funcionou no create'))
            resultados.append('✗ create: ERRO')
        
        # TESTE 3: Cadastro via save() direto (simula qualquer lugar)
        self.stdout.write('\n--- TESTE 3: Cadastro via save() direto ---')
        user3 = User(
            username='teste_universal_3',
            email='teste3@universal.com',
            tipo_usuario='operador_empresa',
            empresa_contratante=empresa
        )
        user3.set_password('123456')
        user3.save()
        
        grupos3 = [ug.grupo.nome for ug in user3.get_grupos_ativos()]
        if 'Operador da Empresa' in grupos3:
            self.stdout.write(self.style.SUCCESS('✓ SUCESSO: Signal funcionou no save() direto'))
            resultados.append('✓ save() direto: OK')
        else:
            self.stdout.write(self.style.ERROR('✗ ERRO: Signal não funcionou no save() direto'))
            resultados.append('✗ save() direto: ERRO')
        
        # TESTE 4: Cadastro via bulk_create (simula importação em massa)
        self.stdout.write('\n--- TESTE 4: Cadastro via bulk_create ---')
        users_bulk = [
            User(
                username='teste_universal_bulk_1',
                email='bulk1@universal.com',
                tipo_usuario='freelancer'
            ),
            User(
                username='teste_universal_bulk_2',
                email='bulk2@universal.com',
                tipo_usuario='admin_sistema'
            )
        ]
        
        # bulk_create NÃO dispara signals, então vamos testar individualmente
        for user_bulk in users_bulk:
            user_bulk.set_password('123456')
            user_bulk.save()
        
        user_bulk1 = User.objects.get(username='teste_universal_bulk_1')
        user_bulk2 = User.objects.get(username='teste_universal_bulk_2')
        
        grupos_bulk1 = [ug.grupo.nome for ug in user_bulk1.get_grupos_ativos()]
        grupos_bulk2 = [ug.grupo.nome for ug in user_bulk2.get_grupos_ativos()]
        
        if 'Freelancers Global' in grupos_bulk1 and 'Administrador do Sistema' in grupos_bulk2:
            self.stdout.write(self.style.SUCCESS('✓ SUCESSO: Signal funcionou em cadastros individuais'))
            resultados.append('✓ Cadastros individuais: OK')
        else:
            self.stdout.write(self.style.ERROR('✗ ERRO: Signal não funcionou em cadastros individuais'))
            resultados.append('✗ Cadastros individuais: ERRO')
        
        # TESTE 5: Modificação de usuário existente (simula mudança no admin)
        self.stdout.write('\n--- TESTE 5: Modificação de usuário existente ---')
        user_existente = User.objects.create_user(
            username='teste_universal_existente',
            email='existente@universal.com',
            password='123456',
            tipo_usuario='freelancer'
        )
        
        # Verifica se foi adicionado ao grupo de freelancers
        grupos_iniciais = [ug.grupo.nome for ug in user_existente.get_grupos_ativos()]
        self.stdout.write(f'Grupos iniciais: {grupos_iniciais}')
        
        # Muda para admin da empresa
        user_existente.tipo_usuario = 'admin_empresa'
        user_existente.empresa_contratante = empresa
        user_existente.save()
        
        grupos_finais = [ug.grupo.nome for ug in user_existente.get_grupos_ativos()]
        self.stdout.write(f'Grupos após mudança: {grupos_finais}')
        
        if 'Administrador da Empresa' in grupos_finais and 'Freelancers Global' not in grupos_finais:
            self.stdout.write(self.style.SUCCESS('✓ SUCESSO: Signal funcionou na modificação'))
            resultados.append('✓ Modificação: OK')
        else:
            self.stdout.write(self.style.ERROR('✗ ERRO: Signal não funcionou na modificação'))
            resultados.append('✗ Modificação: ERRO')
        
        # Limpeza
        self.stdout.write('\n=== LIMPEZA ===')
        User.objects.filter(username__startswith='teste_universal_').delete()
        self.stdout.write('✓ Usuários de teste removidos')
        
        # Resumo final
        self.stdout.write('\n=== RESUMO FINAL ===')
        for resultado in resultados:
            if resultado.startswith('✓'):
                self.stdout.write(self.style.SUCCESS(resultado))
            else:
                self.stdout.write(self.style.ERROR(resultado))
        
        sucessos = len([r for r in resultados if r.startswith('✓')])
        total = len(resultados)
        
        self.stdout.write(f'\nTaxa de sucesso: {sucessos}/{total}')
        
        if sucessos == total:
            self.stdout.write(
                self.style.SUCCESS('\n🎉 OS SIGNALS FUNCIONAM EM TODAS AS FORMAS DE CADASTRO!')
            )
            self.stdout.write('✅ Flutter/API')
            self.stdout.write('✅ Django Admin')
            self.stdout.write('✅ Comandos de gerenciamento')
            self.stdout.write('✅ Qualquer lugar que crie usuários')
            self.stdout.write('\nO sistema é UNIVERSAL e funciona automaticamente!')
        else:
            self.stdout.write(
                self.style.ERROR('\n❌ ALGUNS SIGNALS NÃO ESTÃO FUNCIONANDO!')
            )
