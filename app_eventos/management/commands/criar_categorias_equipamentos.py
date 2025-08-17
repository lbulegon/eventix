from django.core.management.base import BaseCommand
from app_eventos.models import CategoriaEquipamento


class Command(BaseCommand):
    help = 'Cria categorias iniciais de equipamentos'

    def handle(self, *args, **options):
        categorias = [
            {
                'nome': 'Áudio',
                'descricao': 'Equipamentos de áudio como caixas de som, microfones, mesas de som, etc.'
            },
            {
                'nome': 'Iluminação',
                'descricao': 'Equipamentos de iluminação como refletores, spots, controladores, etc.'
            },
            {
                'nome': 'Segurança',
                'descricao': 'Equipamentos de segurança como detectores de metal, câmeras, etc.'
            },
            {
                'nome': 'Informática',
                'descricao': 'Equipamentos de informática como computadores, impressoras, scanners, etc.'
            },
            {
                'nome': 'Móveis',
                'descricao': 'Móveis e mobiliário como mesas, cadeiras, estantes, etc.'
            },
            {
                'nome': 'Limpeza',
                'descricao': 'Equipamentos de limpeza como aspiradores, máquinas de lavar, etc.'
            },
            {
                'nome': 'Cozinha',
                'descricao': 'Equipamentos de cozinha como fogões, geladeiras, freezers, etc.'
            },
            {
                'nome': 'Transporte',
                'descricao': 'Equipamentos de transporte como empilhadeiras, carrinhos, etc.'
            },
            {
                'nome': 'Comunicação',
                'descricao': 'Equipamentos de comunicação como rádios, telefones, etc.'
            },
            {
                'nome': 'Outros',
                'descricao': 'Outros equipamentos diversos'
            }
        ]

        for categoria_data in categorias:
            categoria, created = CategoriaEquipamento.objects.get_or_create(
                nome=categoria_data['nome'],
                defaults={'descricao': categoria_data['descricao']}
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Categoria "{categoria.nome}" criada com sucesso!')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Categoria "{categoria.nome}" já existe.')
                )

        self.stdout.write(
            self.style.SUCCESS('Processo de criação de categorias concluído!')
        )
