"""
Script para criar freelancers de teste para a empresa contratante id=1
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from app_eventos.models import User, EmpresaContratante, Freelance, Funcao, FreelancerFuncao, TipoFuncao
from django.contrib.auth.hashers import make_password

def criar_freelancers():
    try:
        # Buscar a empresa contratante
        empresa = EmpresaContratante.objects.get(id=1)
        print(f"✅ Empresa encontrada: {empresa.nome_fantasia}")
        
        # Verificar se a função ID 58 existe
        try:
            funcao_auxiliar = Funcao.objects.get(id=58)
            print(f"✅ Função encontrada: ID {funcao_auxiliar.id} - {funcao_auxiliar.nome}")
            print(f"   Empresa da função: {funcao_auxiliar.empresa_contratante}")
        except Funcao.DoesNotExist:
            print("❌ Função ID 58 não encontrada!")
            print("   Verifique se a função existe no banco de dados.")
            return
        
        # Dados dos freelancers (usando IDs de funções existentes)
        freelancers_data = [
            {
                'username': 'joao_silva',
                'email': 'joao.silva@email.com',
                'first_name': 'João',
                'last_name': 'Silva',
                'cpf': '111.222.333-44',
                'telefone': '(11) 98765-4321',
                'funcoes_ids': [58],  # Auxiliar de cozinha
            },
            {
                'username': 'maria_santos',
                'email': 'maria.santos@email.com',
                'first_name': 'Maria',
                'last_name': 'Santos',
                'cpf': '222.333.444-55',
                'telefone': '(11) 98765-4322',
                'funcoes_ids': [58],  # Auxiliar de cozinha
            },
            {
                'username': 'pedro_oliveira',
                'email': 'pedro.oliveira@email.com',
                'first_name': 'Pedro',
                'last_name': 'Oliveira',
                'cpf': '333.444.555-66',
                'telefone': '(11) 98765-4323',
                'funcoes_ids': [58],  # Auxiliar de cozinha
            },
            {
                'username': 'ana_costa',
                'email': 'ana.costa@email.com',
                'first_name': 'Ana',
                'last_name': 'Costa',
                'cpf': '444.555.666-77',
                'telefone': '(11) 98765-4324',
                'funcoes_ids': [58],  # Auxiliar de cozinha
            },
            {
                'username': 'carlos_ferreira',
                'email': 'carlos.ferreira@email.com',
                'first_name': 'Carlos',
                'last_name': 'Ferreira',
                'cpf': '555.666.777-88',
                'telefone': '(11) 98765-4325',
                'funcoes_ids': [58],  # Auxiliar de cozinha
            },
            {
                'username': 'julia_almeida',
                'email': 'julia.almeida@email.com',
                'first_name': 'Julia',
                'last_name': 'Almeida',
                'cpf': '666.777.888-99',
                'telefone': '(11) 98765-4326',
                'funcoes_ids': [58],  # Auxiliar de cozinha
            },
            {
                'username': 'lucas_pereira',
                'email': 'lucas.pereira@email.com',
                'first_name': 'Lucas',
                'last_name': 'Pereira',
                'cpf': '777.888.999-00',
                'telefone': '(11) 98765-4327',
                'funcoes_ids': [58],  # Auxiliar de cozinha
            },
            {
                'username': 'fernanda_lima',
                'email': 'fernanda.lima@email.com',
                'first_name': 'Fernanda',
                'last_name': 'Lima',
                'cpf': '888.999.000-11',
                'telefone': '(11) 98765-4328',
                'funcoes_ids': [58],  # Auxiliar de cozinha
            },
        ]
        
        freelancers_criados = 0
        
        for data in freelancers_data:
            try:
                # Verificar se o usuário já existe
                if User.objects.filter(username=data['username']).exists():
                    print(f"⚠️ Usuário {data['username']} já existe, pulando...")
                    continue
                
                # Criar usuário
                user = User.objects.create(
                    username=data['username'],
                    email=data['email'],
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    password=make_password('senha123'),  # Senha padrão: senha123
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
                
                # Associar funções
                funcoes_associadas = 0
                for funcao_id in data.get('funcoes_ids', []):
                    try:
                        funcao = Funcao.objects.get(id=funcao_id)
                        FreelancerFuncao.objects.create(
                            freelancer=freelance,
                            funcao=funcao,
                            nivel='intermediario',
                        )
                        funcoes_associadas += 1
                    except Funcao.DoesNotExist:
                        print(f"   ⚠️ Função ID {funcao_id} não encontrada")
                
                print(f"✅ Freelancer criado: {user.get_full_name()} (@{user.username}) - {funcoes_associadas} função(ões)")
                freelancers_criados += 1
                
            except Exception as e:
                print(f"❌ Erro ao criar {data['username']}: {e}")
        
        print(f"\n🎉 Resumo:")
        print(f"   - Freelancers criados: {freelancers_criados}")
        print(f"   - Empresa: {empresa.nome_fantasia}")
        print(f"   - Função: {funcao_auxiliar.nome} (ID {funcao_auxiliar.id})")
        print(f"\n📱 Credenciais de teste:")
        print(f"   - Username: joao_silva (ou qualquer outro)")
        print(f"   - Senha: senha123")
        
    except EmpresaContratante.DoesNotExist:
        print("❌ Empresa contratante com id=1 não encontrada!")
        print("   Execute primeiro um script de população de dados.")
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("🚀 Criando freelancers de teste...\n")
    criar_freelancers()

