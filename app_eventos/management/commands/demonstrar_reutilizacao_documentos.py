"""
Comando para demonstrar o fluxo de reutilização de documentos
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from app_eventos.models import EmpresaContratante
from app_eventos.models_freelancers import FreelancerGlobal, VagaEmpresa, CandidaturaEmpresa
from app_eventos.models_documentos import (
    DocumentoFreelancerEmpresa, ConfiguracaoDocumentosEmpresa, ReutilizacaoDocumento
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Demonstra o fluxo de reutilização de documentos'

    def handle(self, *args, **options):
        self.stdout.write('=== DEMONSTRACAO: REUTILIZACAO DE DOCUMENTOS ===')
        self.stdout.write('')
        
        # Buscar empresa
        empresa = EmpresaContratante.objects.filter(ativo=True).first()
        if not empresa:
            self.stdout.write('Nenhuma empresa ativa encontrada!')
            return
        
        self.stdout.write(f'Empresa: {empresa.nome_fantasia}')
        self.stdout.write('')
        
        # Demonstração do fluxo
        self.stdout.write('FLUXO COMPLETO DE REUTILIZACAO DE DOCUMENTOS')
        self.stdout.write('=' * 60)
        self.stdout.write('')
        
        # Passo 1: Primeira contratação
        self.stdout.write('PASSO 1: PRIMEIRA CONTRATACAO')
        self.stdout.write('-' * 40)
        self.stdout.write('Freelancer se candidata a uma vaga que exige documentos:')
        self.stdout.write('')
        self.stdout.write('[OK] Vaga: "Tecnico de Som - Evento Corporativo"')
        self.stdout.write('[OK] Exige vinculo empregaticio: SIM')
        self.stdout.write('[OK] Documentos obrigatorios: RG, CPF, CTPS, Comprovante de Residencia')
        self.stdout.write('')
        self.stdout.write('Freelancer envia documentos:')
        self.stdout.write('[OK] RG - Aprovado (valido por 365 dias)')
        self.stdout.write('[OK] CPF - Aprovado (valido por 365 dias)')
        self.stdout.write('[OK] CTPS - Aprovado (valido por 365 dias)')
        self.stdout.write('[OK] Comprovante de Residencia - Aprovado (valido por 90 dias)')
        self.stdout.write('')
        self.stdout.write('[RESULTADO] Freelancer contratado com sucesso!')
        self.stdout.write('[RESULTADO] Documentos armazenados no cadastro da empresa')
        self.stdout.write('')
        
        # Passo 2: Segunda contratação (reutilização)
        self.stdout.write('PASSO 2: SEGUNDA CONTRATACAO (REUTILIZACAO)')
        self.stdout.write('-' * 40)
        self.stdout.write('Freelancer se candidata a outra vaga da mesma empresa:')
        self.stdout.write('')
        self.stdout.write('[OK] Vaga: "Iluminador - Evento Corporativo"')
        self.stdout.write('[OK] Exige vinculo empregaticio: SIM')
        self.stdout.write('[OK] Documentos obrigatorios: RG, CPF, CTPS, Comprovante de Residencia')
        self.stdout.write('')
        self.stdout.write('Sistema verifica documentos existentes:')
        self.stdout.write('[OK] RG - Ja aprovado (valido por mais 300 dias) - REUTILIZAR')
        self.stdout.write('[OK] CPF - Ja aprovado (valido por mais 300 dias) - REUTILIZAR')
        self.stdout.write('[OK] CTPS - Ja aprovado (valido por mais 300 dias) - REUTILIZAR')
        self.stdout.write('[OK] Comprovante de Residencia - Ja aprovado (valido por mais 60 dias) - REUTILIZAR')
        self.stdout.write('')
        self.stdout.write('[RESULTADO] Freelancer contratado SEM enviar documentos novamente!')
        self.stdout.write('[RESULTADO] Documentos reutilizados automaticamente')
        self.stdout.write('')
        
        # Passo 3: Terceira contratação (documento expirado)
        self.stdout.write('PASSO 3: TERCEIRA CONTRATACAO (DOCUMENTO EXPIRADO)')
        self.stdout.write('-' * 40)
        self.stdout.write('Freelancer se candidata a terceira vaga (apos 100 dias):')
        self.stdout.write('')
        self.stdout.write('[OK] Vaga: "Seguranca - Evento Corporativo"')
        self.stdout.write('[OK] Exige vinculo empregaticio: SIM')
        self.stdout.write('[OK] Documentos obrigatorios: RG, CPF, CTPS, Comprovante de Residencia')
        self.stdout.write('')
        self.stdout.write('Sistema verifica documentos existentes:')
        self.stdout.write('[OK] RG - Ja aprovado (valido por mais 265 dias) - REUTILIZAR')
        self.stdout.write('[OK] CPF - Ja aprovado (valido por mais 265 dias) - REUTILIZAR')
        self.stdout.write('[OK] CTPS - Ja aprovado (valido por mais 265 dias) - REUTILIZAR')
        self.stdout.write('[WARN] Comprovante de Residencia - EXPIRADO (vencido ha 10 dias) - SOLICITAR NOVO')
        self.stdout.write('')
        self.stdout.write('[RESULTADO] Freelancer envia APENAS o comprovante de residencia atualizado')
        self.stdout.write('[RESULTADO] Demais documentos reutilizados')
        self.stdout.write('')
        
        # Passo 4: Contratação em empresa diferente
        self.stdout.write('PASSO 4: CONTRATACAO EM EMPRESA DIFERENTE')
        self.stdout.write('-' * 40)
        self.stdout.write('Freelancer se candidata a vaga de outra empresa:')
        self.stdout.write('')
        self.stdout.write('[OK] Vaga: "Operador de Camera - Empresa B"')
        self.stdout.write('[OK] Exige vinculo empregaticio: SIM')
        self.stdout.write('[OK] Documentos obrigatorios: RG, CPF, CTPS, Comprovante de Residencia')
        self.stdout.write('')
        self.stdout.write('Sistema verifica configuracoes da empresa:')
        self.stdout.write('[OK] Empresa B aceita documentos externos: SIM')
        self.stdout.write('[OK] Sistema busca documentos validos de outras empresas')
        self.stdout.write('')
        self.stdout.write('Documentos encontrados:')
        self.stdout.write('[OK] RG - Valido na Empresa A (valido por mais 200 dias) - REUTILIZAR')
        self.stdout.write('[OK] CPF - Valido na Empresa A (valido por mais 200 dias) - REUTILIZAR')
        self.stdout.write('[OK] CTPS - Valido na Empresa A (valido por mais 200 dias) - REUTILIZAR')
        self.stdout.write('[OK] Comprovante de Residencia - Valido na Empresa A (valido por mais 30 dias) - REUTILIZAR')
        self.stdout.write('')
        self.stdout.write('[RESULTADO] Freelancer contratado SEM enviar documentos novamente!')
        self.stdout.write('[RESULTADO] Documentos reutilizados entre empresas')
        self.stdout.write('')
        
        # Benefícios do sistema
        self.stdout.write('BENEFICIOS DO SISTEMA DE CACHE DE DOCUMENTOS')
        self.stdout.write('=' * 60)
        self.stdout.write('')
        self.stdout.write('PARA FREELANCERS:')
        self.stdout.write('[OK] Nao precisa enviar documentos repetidamente')
        self.stdout.write('[OK] Processo de candidatura mais rapido')
        self.stdout.write('[OK] Menos burocracia para contratoes futuras')
        self.stdout.write('[OK] Historico de documentos centralizado')
        self.stdout.write('')
        self.stdout.write('PARA EMPRESAS:')
        self.stdout.write('[OK] Reducao de tempo de processamento')
        self.stdout.write('[OK] Historico completo de documentos')
        self.stdout.write('[OK] Controle automatico de validade')
        self.stdout.write('[OK] Seguranca e conformidade legal')
        self.stdout.write('[OK] Reducao de custos operacionais')
        self.stdout.write('')
        self.stdout.write('PARA O SISTEMA:')
        self.stdout.write('[OK] Otimizacao de recursos')
        self.stdout.write('[OK] Melhor experiencia do usuario')
        self.stdout.write('[OK] Controle de qualidade')
        self.stdout.write('[OK] Auditoria completa')
        self.stdout.write('')
        
        # Configurações por empresa
        self.stdout.write('CONFIGURACOES POR EMPRESA')
        self.stdout.write('=' * 60)
        self.stdout.write('')
        self.stdout.write('Cada empresa pode configurar:')
        self.stdout.write('[OK] Quais documentos sao obrigatorios')
        self.stdout.write('[OK] Periodo de validade de cada documento')
        self.stdout.write('[OK] Se aceita documentos de outras empresas')
        self.stdout.write('[OK] Politicas de reutilizacao')
        self.stdout.write('')
        self.stdout.write('Exemplos de configuracao:')
        self.stdout.write('- Empresa A: RG (365 dias), CPF (365 dias), CTPS (365 dias), Residencia (90 dias)')
        self.stdout.write('- Empresa B: RG (180 dias), CPF (180 dias), CTPS (180 dias), Residencia (60 dias)')
        self.stdout.write('- Empresa C: RG (365 dias), CPF (365 dias), CTPS (365 dias), Residencia (30 dias)')
        self.stdout.write('')
        
        self.stdout.write('=== SISTEMA DE CACHE DE DOCUMENTOS IMPLEMENTADO! ===')
        self.stdout.write('')
        self.stdout.write('O sistema agora suporta:')
        self.stdout.write('1. Reutilizacao automatica de documentos validos')
        self.stdout.write('2. Controle de validade por tipo de documento')
        self.stdout.write('3. Reutilizacao entre empresas (quando configurado)')
        self.stdout.write('4. Controle de expiracao automatico')
        self.stdout.write('5. Auditoria completa de reutilizacoes')
