from django.core.management.base import BaseCommand
from app_eventos.models import Freelance, Candidatura, ContratoFreelance
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Remove todas as candidaturas e contratos do freelancer Liandro'

    def handle(self, *args, **options):
        self.stdout.write('🧹 LIMPANDO CANDIDATURAS DO LIANDRO')
        self.stdout.write('=' * 50)
        
        try:
            # Buscar freelancer Liandro
            freelancer = Freelance.objects.filter(nome_completo__icontains='Liandro').first()
            
            if not freelancer:
                self.stdout.write(self.style.ERROR("❌ Freelancer Liandro não encontrado"))
                return
            
            self.stdout.write(f"👤 Freelancer: {freelancer.nome_completo}")
            
            # Contar candidaturas antes
            candidaturas_antes = Candidatura.objects.filter(freelance=freelancer).count()
            contratos_antes = ContratoFreelance.objects.filter(freelance=freelancer).count()
            
            self.stdout.write(f"📝 Candidaturas encontradas: {candidaturas_antes}")
            self.stdout.write(f"📄 Contratos encontrados: {contratos_antes}")
            
            if candidaturas_antes == 0 and contratos_antes == 0:
                self.stdout.write(self.style.WARNING("⚠️ Nenhuma candidatura ou contrato encontrado"))
                return
            
            # Confirmar remoção
            if not options.get('force', False):
                confirmar = input(f"\n❓ Deseja remover {candidaturas_antes} candidaturas e {contratos_antes} contratos? (s/N): ")
                if confirmar.lower() != 's':
                    self.stdout.write("❌ Operação cancelada")
                    return
            
            # Remover contratos primeiro
            contratos_removidos = ContratoFreelance.objects.filter(freelance=freelancer).delete()
            self.stdout.write(f"🗑️ Contratos removidos: {contratos_removidos[0]}")
            
            # Remover candidaturas
            candidaturas_removidas = Candidatura.objects.filter(freelance=freelancer).delete()
            self.stdout.write(f"🗑️ Candidaturas removidas: {candidaturas_removidas[0]}")
            
            # Verificar se foi removido
            candidaturas_depois = Candidatura.objects.filter(freelance=freelancer).count()
            contratos_depois = ContratoFreelance.objects.filter(freelance=freelancer).count()
            
            self.stdout.write(f"\n📊 RESULTADO:")
            self.stdout.write(f"📝 Candidaturas restantes: {candidaturas_depois}")
            self.stdout.write(f"📄 Contratos restantes: {contratos_depois}")
            
            if candidaturas_depois == 0 and contratos_depois == 0:
                self.stdout.write(self.style.SUCCESS("✅ Limpeza concluída com sucesso!"))
            else:
                self.stdout.write(self.style.ERROR("❌ Ainda restam candidaturas/contratos"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro: {str(e)}"))
        
        self.stdout.write('\n✅ Operação concluída!')
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força a remoção sem confirmação',
        )
