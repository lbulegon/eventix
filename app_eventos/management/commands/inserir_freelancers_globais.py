"""
Comando para inserir uma lista completa de freelancers globais no banco de dados
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
import random
import string

User = get_user_model()


class Command(BaseCommand):
    help = 'Insere uma lista completa de freelancers globais no banco de dados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--quantidade',
            type=int,
            default=100,
            help='Quantidade de freelancers a serem criados (padrão: 100)'
        )
        parser.add_argument(
            '--limpar',
            action='store_true',
            help='Remove todos os freelancers existentes antes de inserir os novos'
        )

    def handle(self, *args, **options):
        quantidade = options['quantidade']
        limpar = options['limpar']
        
        # Lista de nomes globais diversificados
        nomes_globais = [
            # Nomes ocidentais
            'James', 'John', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Charles', 'Joseph', 'Thomas',
            'Christopher', 'Daniel', 'Paul', 'Mark', 'Donald', 'George', 'Kenneth', 'Steven', 'Edward', 'Brian',
            'Ronald', 'Anthony', 'Kevin', 'Jason', 'Matthew', 'Gary', 'Timothy', 'Jose', 'Larry', 'Jeffrey',
            'Frank', 'Scott', 'Eric', 'Stephen', 'Andrew', 'Raymond', 'Gregory', 'Joshua', 'Jerry', 'Dennis',
            'Walter', 'Patrick', 'Peter', 'Harold', 'Douglas', 'Henry', 'Carl', 'Arthur', 'Ryan', 'Roger',
            
            'Mary', 'Patricia', 'Jennifer', 'Linda', 'Elizabeth', 'Barbara', 'Susan', 'Jessica', 'Sarah', 'Karen',
            'Nancy', 'Lisa', 'Betty', 'Helen', 'Sandra', 'Donna', 'Carol', 'Ruth', 'Sharon', 'Michelle',
            'Laura', 'Sarah', 'Kimberly', 'Deborah', 'Dorothy', 'Lisa', 'Nancy', 'Karen', 'Betty', 'Helen',
            'Sandra', 'Donna', 'Carol', 'Ruth', 'Sharon', 'Michelle', 'Laura', 'Sarah', 'Kimberly', 'Deborah',
            'Dorothy', 'Amy', 'Angela', 'Ashley', 'Brenda', 'Emma', 'Olivia', 'Cynthia', 'Marie', 'Janet',
            
            # Nomes latinos/hispânicos
            'Carlos', 'Miguel', 'José', 'Antonio', 'Francisco', 'Manuel', 'David', 'Juan', 'Roberto', 'Daniel',
            'Rafael', 'Pedro', 'Alejandro', 'Fernando', 'Luis', 'Diego', 'Sergio', 'Andrés', 'Ricardo', 'Eduardo',
            'Gabriel', 'Pablo', 'Jorge', 'Mario', 'Alberto', 'Raúl', 'Javier', 'Fernando', 'Sergio', 'Andrés',
            
            'María', 'Carmen', 'Ana', 'Laura', 'Isabel', 'Pilar', 'Cristina', 'Mónica', 'Elena', 'Sandra',
            'Patricia', 'Rosa', 'Dolores', 'Mercedes', 'Francisca', 'Manuela', 'Antonia', 'Encarnación', 'Josefa', 'Teresa',
            'Lucía', 'Paula', 'Sara', 'Raquel', 'Natalia', 'Beatriz', 'Silvia', 'Cristina', 'Mónica', 'Elena',
            
            # Nomes asiáticos
            'Wei', 'Ming', 'Jian', 'Li', 'Wang', 'Zhang', 'Liu', 'Chen', 'Yang', 'Huang',
            'Zhao', 'Wu', 'Zhou', 'Xu', 'Sun', 'Ma', 'Zhu', 'Hu', 'Guo', 'He',
            'Gao', 'Lin', 'Luo', 'Zheng', 'Liang', 'Xie', 'Tang', 'Han', 'Cao', 'Deng',
            
            'Mei', 'Li', 'Xia', 'Hui', 'Yan', 'Jing', 'Ling', 'Fang', 'Min', 'Qing',
            'Ying', 'Ping', 'Xin', 'Yan', 'Jing', 'Ling', 'Fang', 'Min', 'Qing', 'Ying',
            
            # Nomes árabes/muçulmanos
            'Ahmed', 'Mohammed', 'Ali', 'Hassan', 'Hussein', 'Omar', 'Ibrahim', 'Yusuf', 'Abdullah', 'Khalid',
            'Mahmoud', 'Said', 'Tariq', 'Nasser', 'Farid', 'Rashid', 'Karim', 'Samir', 'Adel', 'Bashir',
            
            'Fatima', 'Aisha', 'Khadija', 'Maryam', 'Zainab', 'Amina', 'Hafsa', 'Safiya', 'Ruqayya', 'Umm',
            'Layla', 'Nour', 'Hala', 'Rana', 'Dina', 'Yasmin', 'Nadia', 'Salma', 'Mona', 'Rania',
            
            # Nomes africanos
            'Kwame', 'Kofi', 'Kwaku', 'Yaw', 'Kojo', 'Ama', 'Akosua', 'Adwoa', 'Abena', 'Akua',
            'Yaa', 'Efua', 'Esi', 'Aba', 'Ama', 'Akosua', 'Adwoa', 'Abena', 'Akua', 'Yaa',
            
            'Nelson', 'Mandela', 'Thabo', 'Sipho', 'Lungile', 'Bongani', 'Sizwe', 'Thulani', 'Mthunzi', 'Lwandle',
            'Nomsa', 'Thandi', 'Nolwazi', 'Sibongile', 'Nompumelelo', 'Nokuthula', 'Zanele', 'Lindiwe', 'Ntombi', 'Nomsa',
            
            # Nomes indianos
            'Raj', 'Kumar', 'Singh', 'Sharma', 'Patel', 'Gupta', 'Agarwal', 'Jain', 'Verma', 'Yadav',
            'Pandey', 'Mishra', 'Tiwari', 'Choudhary', 'Mehta', 'Bhatt', 'Joshi', 'Reddy', 'Nair', 'Iyer',
            
            'Priya', 'Kavita', 'Sunita', 'Meera', 'Anita', 'Rekha', 'Sushila', 'Kamala', 'Lakshmi', 'Sita',
            'Gita', 'Rita', 'Neha', 'Pooja', 'Deepa', 'Seema', 'Ritu', 'Shilpa', 'Kiran', 'Rani',
            
            # Nomes russos/eslavos
            'Vladimir', 'Dmitri', 'Sergei', 'Alexander', 'Igor', 'Andrei', 'Mikhail', 'Nikolai', 'Pavel', 'Anton',
            'Yuri', 'Oleg', 'Roman', 'Viktor', 'Maxim', 'Denis', 'Artem', 'Ivan', 'Alexei', 'Boris',
            
            'Elena', 'Olga', 'Tatiana', 'Natalia', 'Svetlana', 'Irina', 'Ludmila', 'Galina', 'Valentina', 'Nina',
            'Anna', 'Maria', 'Ekaterina', 'Sofia', 'Anastasia', 'Daria', 'Polina', 'Vera', 'Larisa', 'Raisa',
        ]
        
        sobrenomes_globais = [
            # Sobrenomes ocidentais
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez',
            'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin',
            'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson',
            'Walker', 'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores',
            'Green', 'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell', 'Mitchell', 'Carter', 'Roberts',
            
            # Sobrenomes latinos/hispânicos
            'García', 'Rodríguez', 'Martínez', 'Hernández', 'López', 'González', 'Pérez', 'Sánchez', 'Ramírez', 'Cruz',
            'Flores', 'Gómez', 'Díaz', 'Reyes', 'Morales', 'Jiménez', 'Álvarez', 'Ruiz', 'Herrera', 'Medina',
            'Aguilar', 'Vargas', 'Castillo', 'Ramos', 'Romero', 'Gutiérrez', 'Torres', 'Dominguez', 'Vásquez', 'Guerrero',
            'Mendoza', 'Herrera', 'Jiménez', 'Moreno', 'Muñoz', 'Álvarez', 'Romero', 'Gutiérrez', 'Navarro', 'Ruiz',
            
            # Sobrenomes asiáticos
            'Wang', 'Li', 'Zhang', 'Liu', 'Chen', 'Yang', 'Huang', 'Zhao', 'Wu', 'Zhou',
            'Xu', 'Sun', 'Ma', 'Zhu', 'Hu', 'Guo', 'He', 'Gao', 'Lin', 'Luo',
            'Zheng', 'Liang', 'Xie', 'Tang', 'Han', 'Cao', 'Deng', 'Feng', 'Cheng', 'Jiang',
            
            # Sobrenomes árabes
            'Al-Ahmad', 'Al-Hassan', 'Al-Hussein', 'Al-Omar', 'Al-Ibrahim', 'Al-Yusuf', 'Al-Abdullah', 'Al-Khalid',
            'Al-Mahmoud', 'Al-Said', 'Al-Tariq', 'Al-Nasser', 'Al-Farid', 'Al-Rashid', 'Al-Karim', 'Al-Samir',
            'Al-Adel', 'Al-Bashir', 'Al-Fatima', 'Al-Aisha', 'Al-Khadija', 'Al-Maryam', 'Al-Zainab', 'Al-Amina',
            
            # Sobrenomes africanos
            'Mthembu', 'Ndlovu', 'Mkhize', 'Dlamini', 'Ntuli', 'Mhlongo', 'Zulu', 'Mthembu', 'Ndlovu', 'Mkhize',
            'Dlamini', 'Ntuli', 'Mhlongo', 'Zulu', 'Mthembu', 'Ndlovu', 'Mkhize', 'Dlamini', 'Ntuli', 'Mhlongo',
            
            # Sobrenomes indianos
            'Sharma', 'Patel', 'Gupta', 'Agarwal', 'Jain', 'Verma', 'Yadav', 'Pandey', 'Mishra', 'Tiwari',
            'Choudhary', 'Mehta', 'Bhatt', 'Joshi', 'Reddy', 'Nair', 'Iyer', 'Menon', 'Kumar', 'Singh',
            
            # Sobrenomes russos
            'Ivanov', 'Petrov', 'Sidorov', 'Kozlov', 'Volkov', 'Sokolov', 'Popov', 'Lebedev', 'Kozlov', 'Novikov',
            'Morozov', 'Petrov', 'Volkov', 'Alekseev', 'Lebedev', 'Semenov', 'Kuznetsov', 'Popov', 'Vasiliev', 'Sokolov',
        ]
        
        # Países e códigos de país
        paises = [
            ('Brasil', 'BR'), ('Estados Unidos', 'US'), ('Canadá', 'CA'), ('Reino Unido', 'GB'), ('França', 'FR'),
            ('Alemanha', 'DE'), ('Itália', 'IT'), ('Espanha', 'ES'), ('Portugal', 'PT'), ('Holanda', 'NL'),
            ('Bélgica', 'BE'), ('Suíça', 'CH'), ('Áustria', 'AT'), ('Suécia', 'SE'), ('Noruega', 'NO'),
            ('Dinamarca', 'DK'), ('Finlândia', 'FI'), ('Polônia', 'PL'), ('República Tcheca', 'CZ'), ('Hungria', 'HU'),
            ('Rússia', 'RU'), ('Ucrânia', 'UA'), ('Turquia', 'TR'), ('Grécia', 'GR'), ('Croácia', 'HR'),
            ('Sérvia', 'RS'), ('Bulgária', 'BG'), ('Romênia', 'RO'), ('Eslováquia', 'SK'), ('Eslovênia', 'SI'),
            ('Japão', 'JP'), ('Coreia do Sul', 'KR'), ('China', 'CN'), ('Índia', 'IN'), ('Tailândia', 'TH'),
            ('Singapura', 'SG'), ('Malásia', 'MY'), ('Indonésia', 'ID'), ('Filipinas', 'PH'), ('Vietnã', 'VN'),
            ('Austrália', 'AU'), ('Nova Zelândia', 'NZ'), ('África do Sul', 'ZA'), ('Nigéria', 'NG'), ('Egito', 'EG'),
            ('Marrocos', 'MA'), ('Argélia', 'DZ'), ('Tunísia', 'TN'), ('Líbia', 'LY'), ('Sudão', 'SD'),
            ('Etiópia', 'ET'), ('Quênia', 'KE'), ('Gana', 'GH'), ('Senegal', 'SN'), ('Costa do Marfim', 'CI'),
            ('México', 'MX'), ('Argentina', 'AR'), ('Chile', 'CL'), ('Colômbia', 'CO'), ('Peru', 'PE'),
            ('Venezuela', 'VE'), ('Uruguai', 'UY'), ('Paraguai', 'PY'), ('Bolívia', 'BO'), ('Equador', 'EC'),
            ('Israel', 'IL'), ('Emirados Árabes Unidos', 'AE'), ('Arábia Saudita', 'SA'), ('Irã', 'IR'), ('Iraque', 'IQ'),
        ]
        
        # Habilidades/funções para freelancers
        habilidades = [
            'Desenvolvimento Web', 'Desenvolvimento Mobile', 'Design Gráfico', 'Design UX/UI', 'Marketing Digital',
            'Redação', 'Tradução', 'Fotografia', 'Videografia', 'Edição de Vídeo', 'Design de Logo',
            'Ilustração', 'Animações 2D/3D', 'Desenvolvimento de Jogos', 'Consultoria de TI', 'Análise de Dados',
            'Pesquisa de Mercado', 'Gestão de Projetos', 'Suporte Técnico', 'Testes de Software', 'DevOps',
            'Segurança da Informação', 'Inteligência Artificial', 'Machine Learning', 'Blockchain', 'IoT',
            'Realidade Virtual', 'Realidade Aumentada', 'Consultoria Empresarial', 'Coaching', 'Mentoria',
            'Recursos Humanos', 'Contabilidade', 'Direito', 'Arquitetura', 'Engenharia', 'Medicina',
            'Psicologia', 'Nutrição', 'Fitness', 'Música', 'Arte', 'Artesanato', 'Culinária', 'Eventos',
            'Logística', 'Vendas', 'Atendimento ao Cliente', 'Secretariado', 'Assistência Virtual',
            'Moda', 'Beleza', 'Saúde', 'Educação', 'Treinamento', 'Consultoria Financeira', 'Investimentos',
            'Imóveis', 'Turismo', 'Hospitalidade', 'Esportes', 'Entretenimento', 'Jornalismo', 'Comunicação',
        ]

        try:
            with transaction.atomic():
                if limpar:
                    # Remove todos os freelancers existentes
                    freelancers_existentes = User.objects.filter(tipo_usuario='freelancer')
                    count_removidos = freelancers_existentes.count()
                    freelancers_existentes.delete()
                    self.stdout.write(f'Removidos {count_removidos} freelancers existentes.')

                # Cria novos freelancers
                freelancers_criados = []
                
                for i in range(quantidade):
                    # Seleciona nome e sobrenome aleatórios
                    nome = random.choice(nomes_globais)
                    sobrenome = random.choice(sobrenomes_globais)
                    
                    # Gera username único
                    username_base = f"{nome.lower()}.{sobrenome.lower()}"
                    username = username_base
                    counter = 1
                    while User.objects.filter(username=username).exists():
                        username = f"{username_base}{counter}"
                        counter += 1
                    
                    # Gera email
                    email = f"{username}@freelancer.com"
                    
                    # Seleciona país aleatório
                    pais, codigo_pais = random.choice(paises)
                    
                    # Seleciona habilidades aleatórias (1-3 habilidades)
                    num_habilidades = random.randint(1, 3)
                    habilidades_usuario = random.sample(habilidades, num_habilidades)
                    
                    # Gera dados do freelancer
                    first_name = nome
                    last_name = sobrenome
                    
                    # Cria o usuário freelancer
                    freelancer = User.objects.create_user(
                        username=username,
                        email=email,
                        password='freelancer123',  # Senha padrão
                        first_name=first_name,
                        last_name=last_name,
                        tipo_usuario='freelancer',
                        ativo=True,
                        is_staff=False,
                        is_superuser=False,
                    )
                    
                    # Adiciona informações extras se existirem campos personalizados
                    # (você pode adicionar campos específicos do freelancer aqui)
                    
                    freelancers_criados.append({
                        'username': username,
                        'nome': f"{first_name} {last_name}",
                        'email': email,
                        'pais': pais,
                        'habilidades': ', '.join(habilidades_usuario)
                    })
                    
                    if (i + 1) % 10 == 0:
                        self.stdout.write(f'Criados {i + 1} freelancers...')

                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Sucesso! {quantidade} freelancers globais criados com sucesso!'
                    )
                )
                
                # Mostra alguns exemplos
                self.stdout.write('\n📋 Exemplos de freelancers criados:')
                for i, freelancer in enumerate(freelancers_criados[:5]):
                    self.stdout.write(
                        f'  {i+1}. {freelancer["nome"]} ({freelancer["username"]}) - {freelancer["pais"]}'
                    )
                    self.stdout.write(f'     Email: {freelancer["email"]}')
                    self.stdout.write(f'     Habilidades: {freelancer["habilidades"]}')
                    self.stdout.write('')
                
                if quantidade > 5:
                    self.stdout.write(f'  ... e mais {quantidade - 5} freelancers')
                
                self.stdout.write(f'\n📊 Estatísticas:')
                self.stdout.write(f'  • Total de freelancers no sistema: {User.objects.filter(tipo_usuario="freelancer").count()}')
                self.stdout.write(f'  • Países representados: {len(set(f["pais"] for f in freelancers_criados))}')
                self.stdout.write(f'  • Habilidades únicas: {len(set(h for f in freelancers_criados for h in f["habilidades"].split(", ")))}')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao criar freelancers: {str(e)}')
            )
            raise
