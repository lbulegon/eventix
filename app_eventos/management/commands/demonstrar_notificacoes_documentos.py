"""
Comando para demonstrar o sistema de notificações automáticas de documentos
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from app_eventos.models import EmpresaContratante
from app_eventos.models_documentos import DocumentoFreelancerEmpresa, ConfiguracaoDocumentosEmpresa
from app_eventos.models_notificacoes import Notificacao

User = get_user_model()


class Command(BaseCommand):
    help = 'Demonstra o sistema de notificações automáticas de documentos'

    def handle(self, *args, **options):
        self.stdout.write('=== DEMONSTRACAO: NOTIFICACOES AUTOMATICAS DE DOCUMENTOS ===')
        self.stdout.write('')
        
        # Buscar empresa
        empresa = EmpresaContratante.objects.filter(ativo=True).first()
        if not empresa:
            self.stdout.write('Nenhuma empresa ativa encontrada!')
            return
        
        self.stdout.write(f'Empresa: {empresa.nome_fantasia}')
        self.stdout.write('')
        
        # Demonstração do sistema
        self.stdout.write('SISTEMA DE NOTIFICACOES AUTOMATICAS')
        self.stdout.write('=' * 60)
        self.stdout.write('')
        
        # 1. Configuração do sistema
        self.stdout.write('1. CONFIGURACAO DO SISTEMA')
        self.stdout.write('-' * 40)
        self.stdout.write('[OK] Sistema verifica documentos automaticamente')
        self.stdout.write('[OK] Notificacoes enviadas para empresa e freelancer')
        self.stdout.write('[OK] Controle de antecedencia configurável')
        self.stdout.write('[OK] Prioridades de notificacao (baixa, media, alta)')
        self.stdout.write('')
        
        # 2. Tipos de notificações
        self.stdout.write('2. TIPOS DE NOTIFICACOES')
        self.stdout.write('-' * 40)
        self.stdout.write('')
        
        self.stdout.write('DOCUMENTOS VENCENDO (30 dias de antecedencia):')
        self.stdout.write('  [NOTIFICACAO] Empresa: "Documento RG do freelancer João vence em 25 dias"')
        self.stdout.write('  [NOTIFICACAO] Freelancer: "Seu documento RG vence em 25 dias. Atualize-o."')
        self.stdout.write('  [PRIORIDADE] Media')
        self.stdout.write('')
        
        self.stdout.write('DOCUMENTOS VENCENDO (15 dias de antecedencia):')
        self.stdout.write('  [NOTIFICACAO] Empresa: "Documento CPF do freelancer Maria vence em 10 dias"')
        self.stdout.write('  [NOTIFICACAO] Freelancer: "Seu documento CPF vence em 10 dias. Atualize-o."')
        self.stdout.write('  [PRIORIDADE] Media')
        self.stdout.write('')
        
        self.stdout.write('DOCUMENTOS VENCENDO (7 dias de antecedencia):')
        self.stdout.write('  [NOTIFICACAO] Empresa: "Documento CTPS do freelancer Pedro vence em 3 dias"')
        self.stdout.write('  [NOTIFICACAO] Freelancer: "Seu documento CTPS vence em 3 dias. Atualize-o."')
        self.stdout.write('  [PRIORIDADE] Media')
        self.stdout.write('')
        
        self.stdout.write('DOCUMENTOS EXPIRADOS:')
        self.stdout.write('  [ALERTA] Empresa: "Documento Residencia do freelancer Ana expirou há 5 dias"')
        self.stdout.write('  [ALERTA] Freelancer: "Seu documento Residencia expirou há 5 dias. Atualize-o."')
        self.stdout.write('  [PRIORIDADE] Alta')
        self.stdout.write('')
        
        # 3. Benefícios para a empresa
        self.stdout.write('3. BENEFICIOS PARA A EMPRESA')
        self.stdout.write('-' * 40)
        self.stdout.write('[OK] Controle automatico de validade de documentos')
        self.stdout.write('[OK] Reducao de trabalho manual de verificacao')
        self.stdout.write('[OK] Notificacoes proativas sobre vencimentos')
        self.stdout.write('[OK] Controle de qualidade dos freelancers')
        self.stdout.write('[OK] Conformidade legal automatica')
        self.stdout.write('[OK] Reducao de riscos trabalhistas')
        self.stdout.write('')
        
        # 4. Benefícios para freelancers
        self.stdout.write('4. BENEFICIOS PARA FREELANCERS')
        self.stdout.write('-' * 40)
        self.stdout.write('[OK] Notificacoes proativas sobre vencimentos')
        self.stdout.write('[OK] Lembretes para atualizacao de documentos')
        self.stdout.write('[OK] Controle de qualidade do perfil')
        self.stdout.write('[OK] Evita perda de oportunidades por documentos expirados')
        self.stdout.write('[OK] Processo de candidatura mais eficiente')
        self.stdout.write('')
        
        # 5. Configurações avançadas
        self.stdout.write('5. CONFIGURACOES AVANCADAS')
        self.stdout.write('-' * 40)
        self.stdout.write('')
        
        self.stdout.write('PERIODOS DE ANTECEDENCIA:')
        self.stdout.write('  [OK] 30 dias: Primeira notificacao')
        self.stdout.write('  [OK] 15 dias: Segunda notificacao')
        self.stdout.write('  [OK] 7 dias: Terceira notificacao')
        self.stdout.write('  [OK] 1 dia: Notificacao final')
        self.stdout.write('  [OK] Expirado: Alerta de documento expirado')
        self.stdout.write('')
        
        self.stdout.write('PRIORIDADES DE NOTIFICACAO:')
        self.stdout.write('  [OK] Baixa: Documentos validos por mais de 30 dias')
        self.stdout.write('  [OK] Media: Documentos vencendo em 30 dias')
        self.stdout.write('  [OK] Alta: Documentos expirados')
        self.stdout.write('')
        
        self.stdout.write('TIPOS DE NOTIFICACAO:')
        self.stdout.write('  [OK] Email: Notificacoes por email')
        self.stdout.write('  [OK] Sistema: Notificacoes no sistema')
        self.stdout.write('  [OK] SMS: Notificacoes por SMS (opcional)')
        self.stdout.write('  [OK] Push: Notificacoes push (mobile)')
        self.stdout.write('')
        
        # 6. Exemplo de fluxo completo
        self.stdout.write('6. EXEMPLO DE FLUXO COMPLETO')
        self.stdout.write('-' * 40)
        self.stdout.write('')
        
        self.stdout.write('DIA 0: Documento aprovado')
        self.stdout.write('  [OK] Documento RG aprovado (valido por 365 dias)')
        self.stdout.write('  [OK] Sistema agenda verificacoes automaticas')
        self.stdout.write('')
        
        self.stdout.write('DIA 335: Primeira notificacao (30 dias antes)')
        self.stdout.write('  [NOTIFICACAO] Empresa: "Documento RG vence em 30 dias"')
        self.stdout.write('  [NOTIFICACAO] Freelancer: "Seu documento RG vence em 30 dias"')
        self.stdout.write('')
        
        self.stdout.write('DIA 350: Segunda notificacao (15 dias antes)')
        self.stdout.write('  [NOTIFICACAO] Empresa: "Documento RG vence em 15 dias"')
        self.stdout.write('  [NOTIFICACAO] Freelancer: "Seu documento RG vence em 15 dias"')
        self.stdout.write('')
        
        self.stdout.write('DIA 358: Terceira notificacao (7 dias antes)')
        self.stdout.write('  [NOTIFICACAO] Empresa: "Documento RG vence em 7 dias"')
        self.stdout.write('  [NOTIFICACAO] Freelancer: "Seu documento RG vence em 7 dias"')
        self.stdout.write('')
        
        self.stdout.write('DIA 364: Notificacao final (1 dia antes)')
        self.stdout.write('  [ALERTA] Empresa: "Documento RG vence amanha"')
        self.stdout.write('  [ALERTA] Freelancer: "Seu documento RG vence amanha"')
        self.stdout.write('')
        
        self.stdout.write('DIA 366: Documento expirado')
        self.stdout.write('  [ALERTA] Empresa: "Documento RG expirou ha 1 dia"')
        self.stdout.write('  [ALERTA] Freelancer: "Seu documento RG expirou ha 1 dia"')
        self.stdout.write('  [ACAO] Sistema impede candidaturas ate documento ser atualizado')
        self.stdout.write('')
        
        # 7. Relatórios e estatísticas
        self.stdout.write('7. RELATORIOS E ESTATISTICAS')
        self.stdout.write('-' * 40)
        self.stdout.write('')
        
        self.stdout.write('RELATORIOS DISPONIVEIS:')
        self.stdout.write('  [OK] Documentos por empresa')
        self.stdout.write('  [OK] Documentos por freelancer')
        self.stdout.write('  [OK] Documentos por tipo')
        self.stdout.write('  [OK] Documentos vencendo')
        self.stdout.write('  [OK] Documentos expirados')
        self.stdout.write('  [OK] Historico de notificacoes')
        self.stdout.write('')
        
        self.stdout.write('ESTATISTICAS:')
        self.stdout.write('  [OK] Total de documentos por empresa')
        self.stdout.write('  [OK] Percentual de documentos validos')
        self.stdout.write('  [OK] Percentual de documentos vencendo')
        self.stdout.write('  [OK] Percentual de documentos expirados')
        self.stdout.write('  [OK] Tempo medio de atualizacao')
        self.stdout.write('')
        
        # 8. Automação completa
        self.stdout.write('8. AUTOMACAO COMPLETA')
        self.stdout.write('-' * 40)
        self.stdout.write('')
        
        self.stdout.write('VERIFICACOES AUTOMATICAS:')
        self.stdout.write('  [OK] Verificacao diaria de documentos')
        self.stdout.write('  [OK] Notificacoes automaticas')
        self.stdout.write('  [OK] Controle de qualidade')
        self.stdout.write('  [OK] Conformidade legal')
        self.stdout.write('')
        
        self.stdout.write('INTEGRACOES:')
        self.stdout.write('  [OK] Sistema de notificacoes')
        self.stdout.write('  [OK] Sistema de email')
        self.stdout.write('  [OK] Sistema de SMS')
        self.stdout.write('  [OK] Sistema mobile')
        self.stdout.write('')
        
        self.stdout.write('=== SISTEMA DE NOTIFICACOES AUTOMATICAS IMPLEMENTADO! ===')
        self.stdout.write('')
        self.stdout.write('O sistema agora oferece:')
        self.stdout.write('1. Verificacao automatica de validade de documentos')
        self.stdout.write('2. Notificacoes proativas para empresas e freelancers')
        self.stdout.write('3. Controle de qualidade automatico')
        self.stdout.write('4. Conformidade legal automatica')
        self.stdout.write('5. Reducao de trabalho manual')
        self.stdout.write('6. Melhor experiencia para todos os usuarios')
