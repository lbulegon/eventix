from django.core.management.base import BaseCommand
from app_eventos.models import Freelance
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Testa a formatação do telefone para SMS'

    def handle(self, *args, **options):
        self.stdout.write('📱 TESTE FORMATAÇÃO TELEFONE')
        self.stdout.write('=' * 50)
        
        try:
            # Buscar freelancer Liandro
            freelancer = Freelance.objects.filter(nome_completo__icontains='Liandro').first()
            
            if not freelancer:
                self.stdout.write(self.style.ERROR("❌ Freelancer Liandro não encontrado"))
                return
            
            self.stdout.write(f"👤 Nome: {freelancer.nome_completo}")
            self.stdout.write(f"📱 Telefone no banco: {freelancer.telefone}")
            self.stdout.write(f"🌍 Código País: {freelancer.codigo_telefonico_pais}")
            
            # Simular a formatação usada nas notificações
            telefone = freelancer.telefone
            codigo_pais = freelancer.codigo_telefonico_pais or '55'
            
            if telefone.startswith('+'):
                telefone_e164 = telefone
            else:
                telefone_e164 = f"+{codigo_pais}{telefone}"
            
            self.stdout.write(f"📞 Telefone formatado: {telefone_e164}")
            
            # Verificar se está correto
            if telefone_e164 == "+5551994523847":
                self.stdout.write(self.style.SUCCESS("✅ Formatação CORRETA!"))
            else:
                self.stdout.write(self.style.ERROR(f"❌ Formatação INCORRETA! Esperado: +5551994523847, Obtido: {telefone_e164}"))
            
            # Comparar com o telefone do teste SMS
            telefone_teste = "+5551994523847"
            self.stdout.write(f"🧪 Telefone do teste SMS: {telefone_teste}")
            
            if telefone_e164 == telefone_teste:
                self.stdout.write(self.style.SUCCESS("✅ IGUAL ao telefone do teste SMS!"))
            else:
                self.stdout.write(self.style.WARNING("⚠️ DIFERENTE do telefone do teste SMS"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro: {str(e)}"))
        
        self.stdout.write('\n✅ Teste concluído!')
