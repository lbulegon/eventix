from django.core.management.base import BaseCommand
from app_eventos.models import Fornecedor, EmpresaContratante


class Command(BaseCommand):
    help = 'Cria fornecedores de exemplo para todas as empresas'

    def handle(self, *args, **options):
        empresas = EmpresaContratante.objects.filter(ativo=True)
        
        if not empresas.exists():
            self.stdout.write(
                self.style.WARNING('Nenhuma empresa ativa encontrada.')
            )
            return
        
        fornecedores_exemplo = [
            {
                'nome_fantasia': 'Sound Pro Ltda',
                'razao_social': 'Sound Pro Locação de Equipamentos Ltda',
                'cnpj': '12.345.678/0001-01',
                'tipo_fornecedor': 'equipamentos',
                'telefone': '(11) 99999-1111',
                'email': 'contato@soundpro.com.br',
                'website': 'https://www.soundpro.com.br'
            },
            {
                'nome_fantasia': 'Decorações Eventos',
                'razao_social': 'Decorações Eventos Especiais Ltda',
                'cnpj': '12.345.678/0001-02',
                'tipo_fornecedor': 'decoracao',
                'telefone': '(11) 99999-2222',
                'email': 'contato@decoracoeseventos.com.br',
                'website': 'https://www.decoracoeseventos.com.br'
            },
            {
                'nome_fantasia': 'Segurança Total',
                'razao_social': 'Segurança Total Ltda',
                'cnpj': '12.345.678/0001-03',
                'tipo_fornecedor': 'seguranca',
                'telefone': '(11) 99999-3333',
                'email': 'contato@segurancatotal.com.br',
                'website': 'https://www.segurancatotal.com.br'
            },
            {
                'nome_fantasia': 'Agência Digital',
                'razao_social': 'Agência Digital Marketing Ltda',
                'cnpj': '12.345.678/0001-04',
                'tipo_fornecedor': 'marketing',
                'telefone': '(11) 99999-4444',
                'email': 'contato@agenciadigital.com.br',
                'website': 'https://www.agenciadigital.com.br'
            },
            {
                'nome_fantasia': 'Transporte Express',
                'razao_social': 'Transporte Express Ltda',
                'cnpj': '12.345.678/0001-05',
                'tipo_fornecedor': 'transporte',
                'telefone': '(11) 99999-5555',
                'email': 'contato@transporteexpress.com.br',
                'website': 'https://www.transporteexpress.com.br'
            },
            {
                'nome_fantasia': 'Catering Gourmet',
                'razao_social': 'Catering Gourmet Ltda',
                'cnpj': '12.345.678/0001-06',
                'tipo_fornecedor': 'alimentacao',
                'telefone': '(11) 99999-6666',
                'email': 'contato@cateringgourmet.com.br',
                'website': 'https://www.cateringgourmet.com.br'
            },
            {
                'nome_fantasia': 'Infraestrutura Eventos',
                'razao_social': 'Infraestrutura Eventos Ltda',
                'cnpj': '12.345.678/0001-07',
                'tipo_fornecedor': 'infraestrutura',
                'telefone': '(11) 99999-7777',
                'email': 'contato@infraestruturaeventos.com.br',
                'website': 'https://www.infraestruturaeventos.com.br'
            }
        ]
        
        total_criados = 0
        
        for empresa in empresas:
            self.stdout.write(f'Criando fornecedores para: {empresa.nome_fantasia}')
            
            for fornecedor_data in fornecedores_exemplo:
                # Modificar CNPJ para ser único por empresa
                cnpj_base = fornecedor_data['cnpj']
                cnpj_modificado = cnpj_base.replace('0001-', f'{empresa.id:02d}-')
                
                fornecedor, created = Fornecedor.objects.get_or_create(
                    empresa_contratante=empresa,
                    cnpj=cnpj_modificado,
                    defaults={
                        'nome_fantasia': fornecedor_data['nome_fantasia'],
                        'razao_social': fornecedor_data['razao_social'],
                        'tipo_fornecedor': fornecedor_data['tipo_fornecedor'],
                        'telefone': fornecedor_data['telefone'],
                        'email': fornecedor_data['email'],
                        'website': fornecedor_data['website'],
                        'ativo': True
                    }
                )
                
                if created:
                    total_criados += 1
                    self.stdout.write(f'  ✓ Criado: {fornecedor.nome_fantasia}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Processo concluído! {total_criados} fornecedores criados.')
        )
