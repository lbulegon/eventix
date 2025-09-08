# app_eventos/management/commands/testar_signals_todos_usuarios.py
from django.core.management.base import BaseCommand
from app_eventos.models import User, GrupoUsuario, EmpresaContratante


class Command(BaseCommand):
    help = 'Testa se os signals estão funcionando para todos os tipos de usuários'

    def handle(self, *args, **options):
        self.stdout.write('=== TESTE DOS SIGNALS PARA TODOS OS TIPOS DE USUÁRIOS ===\n')
        
        # Busca uma empresa para teste
        empresa = EmpresaContratante.objects.filter(ativo=True).first()
        if not empresa:
            self.stdout.write(
                self.style.ERROR('Nenhuma empresa encontrada. Crie uma empresa primeiro.')
            )
            return
        
        self.stdout.write(f'Empresa de teste: {empresa.nome_fantasia}\n')
        
        # Lista de tipos de usuários para testar
        tipos_usuarios = [
            ('freelancer', 'Freelancers Global', None),
            ('admin_sistema', 'Administrador do Sistema', None),
            ('admin_empresa', 'Administrador da Empresa', empresa),
            ('operador_empresa', 'Operador da Empresa', empresa),
        ]
        
        resultados = []
        
        for tipo_usuario, nome_grupo_esperado, empresa_esperada in tipos_usuarios:
            self.stdout.write(f'--- TESTANDO: {tipo_usuario.upper()} ---')
            
            # Remove usuários de teste anteriores
            User.objects.filter(username__startswith=f'teste_{tipo_usuario}').delete()
            
            # Cria usuário de teste
            username_teste = f'teste_{tipo_usuario}'
            user = User.objects.create_user(
                username=username_teste,
                email=f'{tipo_usuario}@teste.com',
                password='123456',
                tipo_usuario=tipo_usuario,
                empresa_contratante=empresa_esperada
            )
            
            self.stdout.write(f'✓ Usuário criado: {user.username}')
            self.stdout.write(f'  Tipo: {user.tipo_usuario}')
            self.stdout.write(f'  Empresa: {user.empresa_contratante.nome_fantasia if user.empresa_contratante else "Nenhuma"}')
            
            # Verifica se foi adicionado ao grupo correto
            grupos_usuario = user.get_grupos_ativos()
            grupo_encontrado = None
            
            for usuario_grupo in grupos_usuario:
                if usuario_grupo.grupo.nome == nome_grupo_esperado:
                    grupo_encontrado = usuario_grupo.grupo
                    break
            
            if grupo_encontrado:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ SUCESSO: Adicionado ao grupo "{grupo_encontrado.nome}"')
                )
                self.stdout.write(f'  Empresa do grupo: {grupo_encontrado.empresa_contratante.nome_fantasia if grupo_encontrado.empresa_contratante else "Global"}')
                
                # Mostra permissões
                permissoes = [p.codigo for p in grupo_encontrado.permissoes.filter(ativo=True)]
                self.stdout.write(f'  Permissões: {permissoes[:3]}{"..." if len(permissoes) > 3 else ""}')
                
                resultados.append(f'✓ {tipo_usuario}: OK')
            else:
                self.stdout.write(
                    self.style.ERROR(f'✗ ERRO: NÃO foi adicionado ao grupo "{nome_grupo_esperado}"')
                )
                self.stdout.write(f'  Grupos encontrados: {[ug.grupo.nome for ug in grupos_usuario]}')
                resultados.append(f'✗ {tipo_usuario}: ERRO')
            
            self.stdout.write('')
        
        # Teste de mudança de tipo
        self.stdout.write('=== TESTE DE MUDANÇA DE TIPO ===')
        
        # Cria um usuário freelancer
        user_mudanca = User.objects.create_user(
            username='teste_mudanca',
            email='mudanca@teste.com',
            password='123456',
            tipo_usuario='freelancer'
        )
        
        self.stdout.write(f'✓ Usuário criado como freelancer: {user_mudanca.username}')
        grupos_iniciais = [ug.grupo.nome for ug in user_mudanca.get_grupos_ativos()]
        self.stdout.write(f'  Grupos iniciais: {grupos_iniciais}')
        
        # Muda para admin da empresa
        user_mudanca.tipo_usuario = 'admin_empresa'
        user_mudanca.empresa_contratante = empresa
        user_mudanca.save()
        
        self.stdout.write(f'✓ Tipo alterado para admin_empresa')
        grupos_finais = [ug.grupo.nome for ug in user_mudanca.get_grupos_ativos()]
        self.stdout.write(f'  Grupos finais: {grupos_finais}')
        
        if 'Administrador da Empresa' in grupos_finais and 'Freelancers Global' not in grupos_finais:
            self.stdout.write(
                self.style.SUCCESS('✓ SUCESSO: Mudança de tipo funcionou corretamente!')
            )
            resultados.append('✓ Mudança de tipo: OK')
        else:
            self.stdout.write(
                self.style.ERROR('✗ ERRO: Mudança de tipo não funcionou!')
            )
            resultados.append('✗ Mudança de tipo: ERRO')
        
        # Limpeza
        self.stdout.write('\n=== LIMPEZA ===')
        User.objects.filter(username__startswith='teste_').delete()
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
                self.style.SUCCESS('\n🎉 TODOS OS SIGNALS ESTÃO FUNCIONANDO PERFEITAMENTE!')
            )
            self.stdout.write('Quando usuários se cadastram no Flutter, eles serão automaticamente')
            self.stdout.write('direcionados para seus respectivos grupos baseado no tipo_usuario.')
        else:
            self.stdout.write(
                self.style.ERROR('\n❌ ALGUNS SIGNALS NÃO ESTÃO FUNCIONANDO!')
            )
