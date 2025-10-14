"""
Comando Django para criar freelancers de teste
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from app_eventos.models import User, EmpresaContratante, Freelance, Funcao, FreelancerFuncao

class Command(BaseCommand):
    help = 'Cria freelancers de teste para a função Auxiliar de Cozinha'

    def add_arguments(self, parser):
        parser.add_argument(
            '--empresa-id',
            type=int,
            default=1,
            help='ID da empresa contratante (padrão: 1)'
        )
        parser.add_argument(
            '--funcao-id',
            type=int,
            default=58,
            help='ID da função (padrão: 58 - Auxiliar de Cozinha)'
        )

    def handle(self, *args, **options):
        empresa_id = options['empresa_id']
        funcao_id = options['funcao_id']
        
        try:
            # Buscar a empresa contratante
            empresa = EmpresaContratante.objects.get(id=empresa_id)
            self.stdout.write(self.style.SUCCESS(f'✅ Empresa encontrada: {empresa.nome_fantasia}'))
            
            # Verificar se a função existe
            try:
                funcao = Funcao.objects.get(id=funcao_id)
                self.stdout.write(self.style.SUCCESS(f'✅ Função encontrada: {funcao.nome} (ID {funcao.id})'))
            except Funcao.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'❌ Função ID {funcao_id} não encontrada!'))
                return
            
            # Dados dos freelancers
            freelancers_data = [
                {
                    'username': 'joao_silva_teste',
                    'email': 'joao.silva.teste@email.com',
                    'first_name': 'João',
                    'last_name': 'Silva',
                    'cpf': '111.222.333-44',
                    'telefone': '(11) 98765-4321',
                },
                {
                    'username': 'maria_santos_teste',
                    'email': 'maria.santos.teste@email.com',
                    'first_name': 'Maria',
                    'last_name': 'Santos',
                    'cpf': '222.333.444-55',
                    'telefone': '(11) 98765-4322',
                },
                {
                    'username': 'pedro_oliveira_teste',
                    'email': 'pedro.oliveira.teste@email.com',
                    'first_name': 'Pedro',
                    'last_name': 'Oliveira',
                    'cpf': '333.444.555-66',
                    'telefone': '(11) 98765-4323',
                },
                {
                    'username': 'ana_costa_teste',
                    'email': 'ana.costa.teste@email.com',
                    'first_name': 'Ana',
                    'last_name': 'Costa',
                    'cpf': '444.555.666-77',
                    'telefone': '(11) 98765-4324',
                },
                {
                    'username': 'carlos_ferreira_teste',
                    'email': 'carlos.ferreira.teste@email.com',
                    'first_name': 'Carlos',
                    'last_name': 'Ferreira',
                    'cpf': '555.666.777-88',
                    'telefone': '(11) 98765-4325',
                },
                {
                    'username': 'julia_almeida_teste',
                    'email': 'julia.almeida.teste@email.com',
                    'first_name': 'Julia',
                    'last_name': 'Almeida',
                    'cpf': '666.777.888-99',
                    'telefone': '(11) 98765-4326',
                },
                {
                    'username': 'lucas_pereira_teste',
                    'email': 'lucas.pereira.teste@email.com',
                    'first_name': 'Lucas',
                    'last_name': 'Pereira',
                    'cpf': '777.888.999-00',
                    'telefone': '(11) 98765-4327',
                },
                {
                    'username': 'fernanda_lima_teste',
                    'email': 'fernanda.lima.teste@email.com',
                    'first_name': 'Fernanda',
                    'last_name': 'Lima',
                    'cpf': '888.999.000-11',
                    'telefone': '(11) 98765-4328',
                },
            ]
            
            freelancers_criados = 0
            
            for data in freelancers_data:
                try:
                    # Verificar se o usuário já existe
                    if User.objects.filter(username=data['username']).exists():
                        self.stdout.write(self.style.WARNING(f"⚠️ Usuário {data['username']} já existe, pulando..."))
                        continue
                    
                    # Criar usuário
                    user = User.objects.create(
                        username=data['username'],
                        email=data['email'],
                        first_name=data['first_name'],
                        last_name=data['last_name'],
                        password=make_password('senha123'),
                        tipo_usuario='freelancer',
                        is_active=True,
                    )
                    
                    # Criar perfil freelancer
                    freelance = Freelance.objects.create(
                        usuario=user,
                        nome_completo=f"{data['first_name']} {data['last_name']}",
                        cpf=data['cpf'],
                        telefone=data['telefone'],
                        data_nascimento='1990-01-01',
                        logradouro='Rua Exemplo, 123',
                        cidade='São Paulo',
                        uf='SP',
                        cep='01234-567',
                    )
                    
                    # Associar à função
                    FreelancerFuncao.objects.create(
                        freelancer=freelance,
                        funcao=funcao,
                        nivel='intermediario',
                    )
                    
                    self.stdout.write(self.style.SUCCESS(
                        f"✅ Freelancer criado: {user.get_full_name()} (@{user.username})"
                    ))
                    freelancers_criados += 1
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"❌ Erro ao criar {data['username']}: {e}"))
            
            self.stdout.write(self.style.SUCCESS(f'\n🎉 Resumo:'))
            self.stdout.write(self.style.SUCCESS(f'   - Freelancers criados: {freelancers_criados}'))
            self.stdout.write(self.style.SUCCESS(f'   - Empresa: {empresa.nome_fantasia}'))
            self.stdout.write(self.style.SUCCESS(f'   - Função: {funcao.nome} (ID {funcao.id})'))
            self.stdout.write(self.style.SUCCESS(f'\n📱 Credenciais de teste:'))
            self.stdout.write(self.style.SUCCESS(f'   - Username: joao_silva_teste (ou qualquer outro)'))
            self.stdout.write(self.style.SUCCESS(f'   - Senha: senha123'))
            
        except EmpresaContratante.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ Empresa contratante com id={empresa_id} não encontrada!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro geral: {e}'))
            import traceback
            traceback.print_exc()

