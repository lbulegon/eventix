"""
Comando para mostrar estatísticas dos freelancers no sistema
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.models import Count
from collections import Counter

User = get_user_model()


class Command(BaseCommand):
    help = 'Mostra estatísticas dos freelancers no sistema'

    def handle(self, *args, **options):
        try:
            # Busca todos os freelancers
            freelancers = User.objects.filter(tipo_usuario='freelancer', ativo=True)
            total_freelancers = freelancers.count()
            
            if total_freelancers == 0:
                self.stdout.write('❌ Nenhum freelancer encontrado no sistema.')
                return
            
            self.stdout.write('📊 ESTATÍSTICAS DOS FREELANCERS')
            self.stdout.write('=' * 50)
            
            # Estatísticas básicas
            self.stdout.write(f'👥 Total de freelancers: {total_freelancers}')
            
            # Freelancers por país (simulado baseado nos sobrenomes)
            sobrenomes_por_pais = {
                'Brasil': ['Silva', 'Santos', 'Oliveira', 'Souza', 'Rodrigues', 'Ferreira', 'Alves', 'Pereira', 'Lima', 'Gomes'],
                'Estados Unidos': ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez'],
                'México': ['García', 'Rodríguez', 'Martínez', 'Hernández', 'López', 'González', 'Pérez', 'Sánchez', 'Ramírez', 'Cruz'],
                'China': ['Wang', 'Li', 'Zhang', 'Liu', 'Chen', 'Yang', 'Huang', 'Zhao', 'Wu', 'Zhou'],
                'Índia': ['Sharma', 'Patel', 'Gupta', 'Agarwal', 'Jain', 'Verma', 'Yadav', 'Pandey', 'Mishra', 'Tiwari'],
                'Rússia': ['Ivanov', 'Petrov', 'Sidorov', 'Kozlov', 'Volkov', 'Sokolov', 'Popov', 'Lebedev', 'Kozlov', 'Novikov'],
            }
            
            # Analisa sobrenomes para determinar países
            paises_count = Counter()
            for freelancer in freelancers:
                sobrenome = freelancer.last_name
                for pais, sobrenomes in sobrenomes_por_pais.items():
                    if sobrenome in sobrenomes:
                        paises_count[pais] += 1
                        break
                else:
                    paises_count['Outros'] += 1
            
            self.stdout.write(f'\n🌍 Distribuição por país:')
            for pais, count in paises_count.most_common(10):
                porcentagem = (count / total_freelancers) * 100
                self.stdout.write(f'  {pais}: {count} ({porcentagem:.1f}%)')
            
            # Análise de nomes mais comuns
            nomes_count = Counter(freelancer.first_name for freelancer in freelancers)
            self.stdout.write(f'\n👤 Nomes mais comuns:')
            for nome, count in nomes_count.most_common(10):
                self.stdout.write(f'  {nome}: {count}')
            
            # Análise de sobrenomes mais comuns
            sobrenomes_count = Counter(freelancer.last_name for freelancer in freelancers)
            self.stdout.write(f'\n🏷️ Sobrenomes mais comuns:')
            for sobrenome, count in sobrenomes_count.most_common(10):
                self.stdout.write(f'  {sobrenome}: {count}')
            
            # Análise de emails
            emails_por_dominio = Counter()
            for freelancer in freelancers:
                if freelancer.email:
                    dominio = freelancer.email.split('@')[1]
                    emails_por_dominio[dominio] += 1
            
            self.stdout.write(f'\n📧 Domínios de email:')
            for dominio, count in emails_por_dominio.most_common(5):
                self.stdout.write(f'  {dominio}: {count}')
            
            # Usuários ativos vs inativos
            freelancers_ativos = User.objects.filter(tipo_usuario='freelancer', ativo=True).count()
            freelancers_inativos = User.objects.filter(tipo_usuario='freelancer', ativo=False).count()
            
            self.stdout.write(f'\n✅ Status dos freelancers:')
            self.stdout.write(f'  Ativos: {freelancers_ativos}')
            self.stdout.write(f'  Inativos: {freelancers_inativos}')
            
            # Usuários criados recentemente (últimos 7 dias)
            from django.utils import timezone
            from datetime import timedelta
            
            data_limite = timezone.now() - timedelta(days=7)
            freelancers_recentes = User.objects.filter(
                tipo_usuario='freelancer',
                date_joined__gte=data_limite
            ).count()
            
            self.stdout.write(f'\n🆕 Freelancers criados nos últimos 7 dias: {freelancers_recentes}')
            
            # Estatísticas de login
            freelancers_com_login = User.objects.filter(
                tipo_usuario='freelancer',
                last_login__isnull=False
            ).count()
            
            freelancers_sem_login = total_freelancers - freelancers_com_login
            
            self.stdout.write(f'\n🔐 Acesso ao sistema:')
            self.stdout.write(f'  Já fizeram login: {freelancers_com_login}')
            self.stdout.write(f'  Nunca fizeram login: {freelancers_sem_login}')
            
            # Exemplos de freelancers
            self.stdout.write(f'\n👥 Exemplos de freelancers:')
            for i, freelancer in enumerate(freelancers[:5], 1):
                status = '✅ Ativo' if freelancer.ativo else '❌ Inativo'
                login_status = '🔓 Já logou' if freelancer.last_login else '🔒 Nunca logou'
                self.stdout.write(f'  {i}. {freelancer.get_full_name()} ({freelancer.username})')
                self.stdout.write(f'     Email: {freelancer.email}')
                self.stdout.write(f'     Status: {status} | {login_status}')
                self.stdout.write(f'     Criado em: {freelancer.date_joined.strftime("%d/%m/%Y %H:%M")}')
                self.stdout.write('')
            
            if total_freelancers > 5:
                self.stdout.write(f'  ... e mais {total_freelancers - 5} freelancers')
            
            self.stdout.write('\n' + '=' * 50)
            self.stdout.write('✅ Estatísticas geradas com sucesso!')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao gerar estatísticas: {str(e)}')
            )
            raise
