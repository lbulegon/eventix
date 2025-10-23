from django.core.management.base import BaseCommand
from app_eventos.models import Freelance
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Atualiza o código telefônico do país para freelancers'

    def handle(self, *args, **options):
        self.stdout.write('📱 ATUALIZANDO CÓDIGO TELEFÔNICO')
        self.stdout.write('=' * 50)
        
        try:
            # Buscar todos os freelancers
            freelancers = Freelance.objects.all()
            
            self.stdout.write(f"👥 Encontrados {freelancers.count()} freelancers")
            
            for freelancer in freelancers:
                # Se o telefone começa com 55, o código já está no número
                if freelancer.telefone and freelancer.telefone.startswith('55'):
                    # Remover o 55 do telefone e definir código do país
                    telefone_sem_codigo = freelancer.telefone[2:]  # Remove os primeiros 2 dígitos
                    freelancer.telefone = telefone_sem_codigo
                    freelancer.codigo_telefonico_pais = '55'
                    freelancer.save()
                    
                    self.stdout.write(f"✅ {freelancer.nome_completo}: {freelancer.telefone} (código: {freelancer.codigo_telefonico_pais})")
                else:
                    # Manter código padrão 55 para Brasil
                    freelancer.codigo_telefonico_pais = '55'
                    freelancer.save()
                    
                    self.stdout.write(f"📱 {freelancer.nome_completo}: {freelancer.telefone} (código: {freelancer.codigo_telefonico_pais})")
            
            self.stdout.write(self.style.SUCCESS("✅ Códigos telefônicos atualizados com sucesso!"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro: {str(e)}"))
        
        self.stdout.write('\n✅ Operação concluída!')
