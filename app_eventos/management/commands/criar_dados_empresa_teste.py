from django.core.management.base import BaseCommand
from app_eventos.models import (
    EmpresaContratante, TipoEmpresa, Empresa, LocalEvento, Evento, 
    SetorEvento, CategoriaEquipamento, Equipamento, TipoFuncao
)


class Command(BaseCommand):
    help = 'Cria dados de teste para uma empresa contratante'

    def handle(self, *args, **options):
        try:
            # Cria a empresa contratante UP Mix se não existir
            from datetime import datetime, timedelta
            data_contratacao = datetime.now()
            data_vencimento = data_contratacao + timedelta(days=365)  # Contrato de 1 ano
            
            empresa_contratante, created = EmpresaContratante.objects.get_or_create(
                nome_fantasia='UP Mix',
                defaults={
                    'nome': 'UP Mix Alimentação e Bebidas Ltda',
                    'cnpj': '12.345.678/0001-90',
                    'razao_social': 'UP Mix Alimentação e Bebidas Ltda',
                    'email': 'contato@upmix.com',
                    'telefone': '(11) 99999-9999',
                    'website': 'www.upmix.com.br',
                    'data_contratacao': data_contratacao,
                    'data_vencimento': data_vencimento,
                    'plano_contratado': 'Premium',
                    'valor_mensal': 1500.00,
                    'ativo': True
                }
            )
            
            if created:
                self.stdout.write(f'Empresa contratante "{empresa_contratante.nome_fantasia}" criada')
            
            # Cria tipo de empresa se não existir
            tipo_empresa, created = TipoEmpresa.objects.get_or_create(
                nome='Alimentação e Bebidas',
                defaults={'descricao': 'Empresa especializada em alimentação e bebidas para eventos'}
            )
            
            # Cria empresa proprietária (UP Mix também é proprietária dos locais)
            empresa_proprietaria, created = Empresa.objects.get_or_create(
                nome='UP Mix Alimentação e Bebidas',
                defaults={
                    'cnpj': '12.345.678/0001-90',
                    'email': 'contato@upmix.com',
                    'telefone': '(11) 99999-9999',
                    'tipo_empresa': tipo_empresa,
                    'empresa_contratante': empresa_contratante,
                    'ativo': True
                }
            )
            
            # Cria local de evento
            local_evento, created = LocalEvento.objects.get_or_create(
                nome='Espaço UP Mix - São Paulo',
                defaults={
                    'endereco': 'Rua Augusta, 500 - São Paulo/SP',
                    'capacidade': 3000,
                    'empresa_proprietaria': empresa_proprietaria,
                    'empresa_contratante': empresa_contratante,
                    'ativo': True
                }
            )
            
            # Cria evento
            from datetime import datetime, timedelta
            data_inicio = datetime.now() + timedelta(days=30)
            data_fim = data_inicio + timedelta(days=2)
            
            evento, created = Evento.objects.get_or_create(
                nome='Festival Gastronômico UP Mix 2024',
                defaults={
                    'data_inicio': data_inicio,
                    'data_fim': data_fim,
                    'local': local_evento,
                    'empresa_produtora': empresa_proprietaria,
                    'empresa_contratante': empresa_contratante,
                    'empresa_contratante_recursos': empresa_proprietaria,
                    'ativo': True
                }
            )
            
            # Cria setores do evento
            setores_data = [
                {'nome': 'Área de Cozinha', 'descricao': 'Cozinha principal para preparação dos pratos'},
                {'nome': 'Área de Serviço', 'descricao': 'Área de atendimento ao público'},
                {'nome': 'Bar Principal', 'descricao': 'Bar com bebidas e drinks especiais'},
                {'nome': 'Área VIP', 'descricao': 'Área exclusiva para convidados VIP'},
            ]
            
            for setor_data in setores_data:
                setor, created = SetorEvento.objects.get_or_create(
                    nome=setor_data['nome'],
                    evento=evento,
                    defaults={
                        'descricao': setor_data['descricao'],
                        'ativo': True
                    }
                )
                
                if created:
                    self.stdout.write(f'Setor "{setor.nome}" criado')
            
            # Cria categorias de equipamentos
            categorias_data = [
                {'nome': 'Cozinha', 'descricao': 'Equipamentos de cozinha'},
                {'nome': 'Refrigeração', 'descricao': 'Equipamentos de refrigeração'},
                {'nome': 'Bar', 'descricao': 'Equipamentos para bar e bebidas'},
                {'nome': 'Mobiliário', 'descricao': 'Móveis e decoração'},
            ]
            
            for cat_data in categorias_data:
                categoria, created = CategoriaEquipamento.objects.get_or_create(
                    nome=cat_data['nome'],
                    empresa_contratante=empresa_contratante,
                    defaults={
                        'descricao': cat_data['descricao'],
                        'ativo': True
                    }
                )
                
                if created:
                    self.stdout.write(f'Categoria "{categoria.nome}" criada')
            
            # Cria equipamentos
            equipamentos_data = [
                {'codigo_patrimonial': 'COZ001', 'categoria': 'Cozinha', 'descricao': 'Fogão industrial 6 bocas'},
                {'codigo_patrimonial': 'COZ002', 'categoria': 'Cozinha', 'descricao': 'Forno industrial'},
                {'codigo_patrimonial': 'REF001', 'categoria': 'Refrigeração', 'descricao': 'Freezer industrial'},
                {'codigo_patrimonial': 'BAR001', 'categoria': 'Bar', 'descricao': 'Balcão de bar completo'},
                {'codigo_patrimonial': 'MOB001', 'categoria': 'Mobiliário', 'descricao': 'Mesas e cadeiras para 300 pessoas'},
            ]
            
            for equip_data in equipamentos_data:
                categoria = CategoriaEquipamento.objects.get(
                    nome=equip_data['categoria'],
                    empresa_contratante=empresa_contratante
                )
                
                equipamento, created = Equipamento.objects.get_or_create(
                    codigo_patrimonial=equip_data['codigo_patrimonial'],
                    defaults={
                        'descricao': equip_data['descricao'],
                        'categoria': categoria,
                        'empresa_proprietaria': empresa_proprietaria,
                        'empresa_contratante': empresa_contratante,
                        'ativo': True
                    }
                )
                
                if created:
                    self.stdout.write(f'Equipamento "{equipamento.codigo_patrimonial}" criado')
            
            # Cria tipos de função
            tipos_funcao_data = [
                {'nome': 'Chef de Cozinha', 'descricao': 'Responsável pela preparação dos pratos'},
                {'nome': 'Auxiliar de Cozinha', 'descricao': 'Auxilia na preparação dos alimentos'},
                {'nome': 'Bartender', 'descricao': 'Responsável pela preparação de bebidas'},
                {'nome': 'Garçom', 'descricao': 'Responsável pelo atendimento ao público'},
            ]
            
            for tipo_data in tipos_funcao_data:
                tipo_funcao, created = TipoFuncao.objects.get_or_create(
                    nome=tipo_data['nome'],
                    empresa_contratante=empresa_contratante,
                    defaults={
                        'descricao': tipo_data['descricao'],
                        'ativo': True
                    }
                )
                
                if created:
                    self.stdout.write(f'Tipo de função "{tipo_funcao.nome}" criado')
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Dados de teste criados com sucesso para a empresa {empresa_contratante.nome_fantasia}!'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro ao criar dados de teste: {str(e)}')
            )
