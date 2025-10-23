from django.core.management.base import BaseCommand
from app_eventos.models import Freelance, Candidatura, ContratoFreelance
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Debug do freelancer Liandro para verificar configurações de notificação'

    def handle(self, *args, **options):
        self.stdout.write('🔍 DEBUG FREELANCER LIANDRO')
        self.stdout.write('=' * 50)
        
        try:
            # Buscar freelancer Liandro
            freelancer = Freelance.objects.filter(nome_completo__icontains='Liandro').first()
            
            if not freelancer:
                self.stdout.write(self.style.ERROR("❌ Freelancer Liandro não encontrado"))
                return
            
            self.stdout.write(f"👤 Nome: {freelancer.nome_completo}")
            self.stdout.write(f"📱 Telefone: {freelancer.telefone}")
            self.stdout.write(f"🌍 Código País: {freelancer.codigo_telefonico_pais}")
            self.stdout.write(f"📞 Telefone Formatado: +{freelancer.codigo_telefonico_pais}{freelancer.telefone}")
            self.stdout.write(f"🔔 Notificações Ativas: {freelancer.notificacoes_ativas}")
            self.stdout.write(f"✅ Cadastro Completo: {freelancer.cadastro_completo}")
            self.stdout.write(f"📧 Email: {freelancer.usuario.email if freelancer.usuario else 'N/A'}")
            
            # Verificar funções
            funcoes = freelancer.funcoes.all()
            self.stdout.write(f"\n💼 Funções ({funcoes.count()}):")
            for funcao in funcoes:
                self.stdout.write(f"   - {funcao.funcao.nome}")
            
            # Verificar candidaturas
            candidaturas = Candidatura.objects.filter(freelance=freelancer)
            self.stdout.write(f"\n📝 Candidaturas ({candidaturas.count()}):")
            for candidatura in candidaturas:
                status = candidatura.get_status_display()
                self.stdout.write(f"   - Vaga {candidatura.vaga.id} ({candidatura.vaga.funcao.nome}): {status}")
            
            # Verificar contratos
            contratos = ContratoFreelance.objects.filter(freelance=freelancer)
            self.stdout.write(f"\n📄 Contratos ({contratos.count()}):")
            for contrato in contratos:
                self.stdout.write(f"   - Vaga {contrato.vaga.id} ({contrato.vaga.funcao.nome}): {contrato.get_status_display()}")
            
            # Verificar se está sendo filtrado corretamente
            self.stdout.write(f"\n🔍 TESTE DE FILTRO:")
            freelancers_filtrados = Freelance.objects.filter(
                funcoes__funcao__nome='Segurança',
                notificacoes_ativas=True,
                telefone__isnull=False,
                telefone__gt=''
            ).distinct()
            
            self.stdout.write(f"👥 Freelancers encontrados para Segurança: {freelancers_filtrados.count()}")
            for f in freelancers_filtrados:
                self.stdout.write(f"   - {f.nome_completo} (Telefone: {f.telefone})")
            
            if freelancer in freelancers_filtrados:
                self.stdout.write(self.style.SUCCESS("✅ Liandro está sendo incluído no filtro"))
            else:
                self.stdout.write(self.style.ERROR("❌ Liandro NÃO está sendo incluído no filtro"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro: {str(e)}"))
        
        self.stdout.write('\n✅ Debug concluído!')
