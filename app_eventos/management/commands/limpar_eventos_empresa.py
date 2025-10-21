"""
Comando para limpar eventos, setores e vagas de uma empresa específica
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from app_eventos.models import (
    EmpresaContratante, Evento, SetorEvento, Vaga, 
    Candidatura, ContratoFreelance
)


class Command(BaseCommand):
    help = 'Limpa eventos, setores, vagas e candidaturas de uma empresa específica'

    def add_arguments(self, parser):
        parser.add_argument(
            '--empresa-id',
            type=int,
            help='ID da empresa contratante'
        )
        parser.add_argument(
            '--empresa-nome',
            type=str,
            help='Nome da empresa contratante (busca parcial)'
        )
        parser.add_argument(
            '--confirmar',
            action='store_true',
            help='Confirma a operação de limpeza (obrigatório)'
        )
        parser.add_argument(
            '--apenas-estatisticas',
            action='store_true',
            help='Apenas mostra estatísticas sem deletar'
        )

    def handle(self, *args, **options):
        empresa_id = options.get('empresa_id')
        empresa_nome = options.get('empresa_nome')
        confirmar = options.get('confirmar')
        apenas_stats = options.get('apenas_estatisticas')

        # Buscar empresa
        if empresa_id:
            try:
                empresa = EmpresaContratante.objects.get(id=empresa_id)
            except EmpresaContratante.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'❌ Empresa com ID {empresa_id} não encontrada!')
                )
                return
        elif empresa_nome:
            empresas = EmpresaContratante.objects.filter(
                nome_fantasia__icontains=empresa_nome
            )
            
            if not empresas.exists():
                self.stdout.write(
                    self.style.ERROR(f'❌ Nenhuma empresa encontrada com nome "{empresa_nome}"!')
                )
                return
            elif empresas.count() > 1:
                self.stdout.write(
                    self.style.WARNING('⚠️  Múltiplas empresas encontradas:')
                )
                for emp in empresas:
                    self.stdout.write(f'   ID: {emp.id} - {emp.nome_fantasia}')
                self.stdout.write(
                    self.style.WARNING('\nUse --empresa-id para especificar uma empresa.')
                )
                return
            else:
                empresa = empresas.first()
        else:
            self.stdout.write(
                self.style.ERROR('❌ Forneça --empresa-id ou --empresa-nome')
            )
            return

        # Buscar dados relacionados
        eventos = Evento.objects.filter(empresa_contratante=empresa)
        setores = SetorEvento.objects.filter(evento__empresa_contratante=empresa)
        vagas = Vaga.objects.filter(empresa_contratante=empresa)
        candidaturas = Candidatura.objects.filter(vaga__empresa_contratante=empresa)
        contratos = ContratoFreelance.objects.filter(vaga__empresa_contratante=empresa)

        # Estatísticas
        stats = {
            'eventos': eventos.count(),
            'setores': setores.count(),
            'vagas': vagas.count(),
            'candidaturas': candidaturas.count(),
            'contratos': contratos.count(),
        }

        # Mostrar informações
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(f'🏢 Empresa: {empresa.nome_fantasia} (ID: {empresa.id})')
        self.stdout.write('=' * 70)
        self.stdout.write('\n📊 Estatísticas:')
        self.stdout.write(f'   • Eventos: {stats["eventos"]}')
        self.stdout.write(f'   • Setores: {stats["setores"]}')
        self.stdout.write(f'   • Vagas: {stats["vagas"]}')
        self.stdout.write(f'   • Candidaturas: {stats["candidaturas"]}')
        self.stdout.write(f'   • Contratos: {stats["contratos"]}')
        self.stdout.write('')

        # Se for apenas estatísticas, parar aqui
        if apenas_stats:
            self.stdout.write(
                self.style.SUCCESS('✅ Modo apenas estatísticas - nenhum dado foi deletado.')
            )
            return

        # Verificar se tem dados
        total_registros = sum(stats.values())
        if total_registros == 0:
            self.stdout.write(
                self.style.SUCCESS('✅ Empresa não possui eventos ou vagas para limpar.')
            )
            return

        # Verificar confirmação
        if not confirmar:
            self.stdout.write(
                self.style.ERROR('\n❌ Operação cancelada!')
            )
            self.stdout.write(
                self.style.WARNING('⚠️  Para confirmar a limpeza, use o flag --confirmar')
            )
            self.stdout.write(
                self.style.WARNING('⚠️  ATENÇÃO: Esta operação é IRREVERSÍVEL!')
            )
            self.stdout.write('\nExemplo:')
            self.stdout.write(
                f'   python manage.py limpar_eventos_empresa --empresa-id {empresa.id} --confirmar'
            )
            return

        # Executar limpeza com transação
        self.stdout.write('\n🧹 Iniciando limpeza...\n')
        
        try:
            with transaction.atomic():
                # Deletar em ordem (relacionamentos)
                deletados_contratos = contratos.delete()[0]
                self.stdout.write(f'   ✓ Contratos deletados: {deletados_contratos}')
                
                deletados_candidaturas = candidaturas.delete()[0]
                self.stdout.write(f'   ✓ Candidaturas deletadas: {deletados_candidaturas}')
                
                deletados_vagas = vagas.delete()[0]
                self.stdout.write(f'   ✓ Vagas deletadas: {deletados_vagas}')
                
                deletados_setores = setores.delete()[0]
                self.stdout.write(f'   ✓ Setores deletados: {deletados_setores}')
                
                deletados_eventos = eventos.delete()[0]
                self.stdout.write(f'   ✓ Eventos deletados: {deletados_eventos}')
                
            self.stdout.write('\n' + '=' * 70)
            self.stdout.write(
                self.style.SUCCESS('✅ Limpeza concluída com sucesso!')
            )
            self.stdout.write(
                f'📊 Total de registros deletados: {sum([deletados_contratos, deletados_candidaturas, deletados_vagas, deletados_setores, deletados_eventos])}'
            )
            self.stdout.write('=' * 70 + '\n')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'\n❌ Erro ao limpar dados: {str(e)}')
            )
            raise

