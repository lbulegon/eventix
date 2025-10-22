"""
Comando para testar notificações automáticas de vagas
"""
from django.core.management.base import BaseCommand
from app_eventos.models import Vaga, Funcao, Freelance
from app_eventos.services.notificacao_vagas import NotificacaoVagasService


class Command(BaseCommand):
    help = 'Testa notificação automática de vagas por função'

    def add_arguments(self, parser):
        parser.add_argument(
            '--funcao',
            type=str,
            help='Nome da função para testar (ex: "Segurança")'
        )
        parser.add_argument(
            '--vaga-id',
            type=int,
            help='ID da vaga específica para testar'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Apenas simula, não envia realmente'
        )

    def handle(self, *args, **options):
        funcao_nome = options.get('funcao')
        vaga_id = options.get('vaga_id')
        dry_run = options.get('dry_run')

        self.stdout.write('\n' + '=' * 70)
        self.stdout.write('🧪 TESTE DE NOTIFICAÇÃO AUTOMÁTICA DE VAGAS')
        self.stdout.write('=' * 70 + '\n')

        if dry_run:
            self.stdout.write(self.style.WARNING('🧪 MODO DRY-RUN (simulação)'))
            return self._simular_notificacao(funcao_nome, vaga_id)

        # Teste real
        notificacao_service = NotificacaoVagasService()

        if vaga_id:
            # Testar vaga específica
            try:
                vaga = Vaga.objects.get(id=vaga_id)
                self.stdout.write(f'📋 Testando vaga: {vaga.funcao.nome if vaga.funcao else "Sem função"}')
                
                resultado = notificacao_service.notificar_nova_vaga(vaga)
                self._mostrar_resultado(resultado)
                
            except Vaga.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'❌ Vaga ID {vaga_id} não encontrada'))
                return

        elif funcao_nome:
            # Testar por função
            self.stdout.write(f'🔍 Testando função: {funcao_nome}')
            resultado = notificacao_service.notificar_vagas_por_funcao(funcao_nome)
            self._mostrar_resultado(resultado)

        else:
            # Mostrar opções
            self.stdout.write('📋 Opções disponíveis:')
            self.stdout.write('1. Testar por função: --funcao "Segurança"')
            self.stdout.write('2. Testar vaga específica: --vaga-id 123')
            self.stdout.write('3. Simular: --dry-run')

    def _simular_notificacao(self, funcao_nome, vaga_id):
        """Simula notificação sem enviar"""
        if vaga_id:
            try:
                vaga = Vaga.objects.get(id=vaga_id)
                funcao = vaga.funcao
                if not funcao:
                    self.stdout.write(self.style.ERROR('❌ Vaga sem função definida'))
                    return
            except Vaga.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'❌ Vaga ID {vaga_id} não encontrada'))
                return
        else:
            if not funcao_nome:
                self.stdout.write(self.style.ERROR('❌ Especifique --funcao ou --vaga-id'))
                return
            
            try:
                funcao = Funcao.objects.get(nome__iexact=funcao_nome)
            except Funcao.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'❌ Função "{funcao_nome}" não encontrada'))
                return

        # Buscar freelancers
        freelancers = Freelance.objects.filter(
            funcoes__funcao=funcao,
            notificacoes_ativas=True,
            telefone__isnull=False,
            telefone__gt=''
        ).distinct()

        self.stdout.write(f'\n📊 SIMULAÇÃO:')
        self.stdout.write(f'🎯 Função: {funcao.nome}')
        self.stdout.write(f'👥 Freelancers encontrados: {freelancers.count()}')
        
        if freelancers.exists():
            self.stdout.write('\n📱 Destinatários:')
            for i, freelancer in enumerate(freelancers[:5], 1):
                self.stdout.write(f'  {i}. {freelancer.nome_completo} - {freelancer.telefone}')
            if freelancers.count() > 5:
                self.stdout.write(f'  ... e mais {freelancers.count() - 5} freelancers')
        else:
            self.stdout.write(self.style.WARNING('⚠️  Nenhum freelancer encontrado para esta função'))

        self.stdout.write('\n' + self.style.SUCCESS('✅ Simulação concluída'))

    def _mostrar_resultado(self, resultado):
        """Mostra resultado do envio"""
        if 'erro' in resultado:
            self.stdout.write(self.style.ERROR(f'❌ Erro: {resultado["erro"]}'))
            return

        self.stdout.write(f'\n📊 RESULTADO:')
        self.stdout.write(f'👥 Total de freelancers: {resultado.get("total_freelancers", 0)}')
        self.stdout.write(f'✅ Enviados: {resultado.get("enviados", 0)}')
        self.stdout.write(f'❌ Erros: {resultado.get("erros", 0)}')
        
        if resultado.get("detalhes"):
            self.stdout.write(f'\n📱 Detalhes:')
            for detalhe in resultado["detalhes"][:3]:  # Mostrar até 3
                status_icon = "✅" if detalhe["status"] == "enviado" else "❌"
                self.stdout.write(f'  {status_icon} {detalhe["freelancer"]} - {detalhe["status"]}')
            
            if len(resultado["detalhes"]) > 3:
                self.stdout.write(f'  ... e mais {len(resultado["detalhes"]) - 3} resultados')
