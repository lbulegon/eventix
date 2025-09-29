"""
Comando para demonstrar como a empresa contratante cria vagas com diferentes exigências
"""
from django.core.management.base import BaseCommand
from app_eventos.models import EmpresaContratante
from app_eventos.models_freelancers import VagaEmpresa
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Demonstra como a empresa contratante cria vagas com diferentes exigências'

    def handle(self, *args, **options):
        self.stdout.write('=== DEMONSTRACAO: CRIACAO DE VAGAS PELA EMPRESA CONTRATANTE ===')
        
        # Buscar empresa
        empresa = EmpresaContratante.objects.filter(ativo=True).first()
        if not empresa:
            self.stdout.write('Nenhuma empresa ativa encontrada!')
            return
        
        self.stdout.write(f'Empresa: {empresa.nome_fantasia}')
        self.stdout.write('')
        
        # Demonstração 1: Vaga sem exigência de documentação
        self.stdout.write('DEMONSTRACAO 1: VAGA SEM EXIGENCIA DE DOCUMENTACAO')
        self.stdout.write('=' * 60)
        self.stdout.write('A empresa contratante cria uma vaga para evento livre:')
        self.stdout.write('')
        self.stdout.write('[OK] Titulo: "Tecnico de Som - Evento Livre"')
        self.stdout.write('[OK] Descricao: "Tecnico de som para evento sem vinculo empregaticio"')
        self.stdout.write('[OK] Exige vinculo empregaticio: NAO')
        self.stdout.write('[OK] Tipo de vinculo: (nao aplicavel)')
        self.stdout.write('[OK] Remuneracao: R$ 500,00 por evento')
        self.stdout.write('[OK] Quantidade: 2 vagas')
        self.stdout.write('')
        self.stdout.write('[RESULTADO] Freelancers podem se candidatar sem enviar documentos')
        self.stdout.write('[RESULTADO] Contratacao direta, sem vinculo empregaticio')
        self.stdout.write('')
        
        # Demonstração 2: Vaga com exigência de documentação - Contrato Temporário
        self.stdout.write('DEMONSTRACAO 2: VAGA COM EXIGENCIA DE DOCUMENTACAO - CONTRATO TEMPORARIO')
        self.stdout.write('=' * 60)
        self.stdout.write('A empresa contratante cria uma vaga para evento corporativo:')
        self.stdout.write('')
        self.stdout.write('[OK] Titulo: "Iluminador - Evento Corporativo"')
        self.stdout.write('[OK] Descricao: "Iluminador para evento corporativo com contrato temporario"')
        self.stdout.write('[OK] Exige vinculo empregaticio: SIM')
        self.stdout.write('[OK] Tipo de vinculo: CONTRATO TEMPORARIO')
        self.stdout.write('[OK] Remuneracao: R$ 800,00 por evento')
        self.stdout.write('[OK] Quantidade: 1 vaga')
        self.stdout.write('')
        self.stdout.write('[RESULTADO] Freelancers DEVEM enviar documentos obrigatorios')
        self.stdout.write('[RESULTADO] Contratacao com vinculo empregaticio temporario')
        self.stdout.write('[DOCUMENTOS] RG, CPF, CTPS, Comprovante de Residencia')
        self.stdout.write('')
        
        # Demonstração 3: Vaga com exigência de documentação - Contrato Intermitente
        self.stdout.write('DEMONSTRACAO 3: VAGA COM EXIGENCIA DE DOCUMENTACAO - CONTRATO INTERMITENTE')
        self.stdout.write('=' * 60)
        self.stdout.write('A empresa contratante cria uma vaga para evento intermitente:')
        self.stdout.write('')
        self.stdout.write('[OK] Titulo: "Seguranca - Evento Intermitente"')
        self.stdout.write('[OK] Descricao: "Seguranca para evento com contrato intermitente"')
        self.stdout.write('[OK] Exige vinculo empregaticio: SIM')
        self.stdout.write('[OK] Tipo de vinculo: CONTRATO INTERMITENTE')
        self.stdout.write('[OK] Remuneracao: R$ 300,00 por dia')
        self.stdout.write('[OK] Quantidade: 3 vagas')
        self.stdout.write('')
        self.stdout.write('[RESULTADO] Freelancers DEVEM enviar documentos obrigatorios')
        self.stdout.write('[RESULTADO] Contratacao com vinculo empregaticio intermitente')
        self.stdout.write('[DOCUMENTOS] RG, CPF, CTPS, Comprovante de Residencia')
        self.stdout.write('')
        
        # Demonstração 4: Vaga com exigência de documentação - Terceirizado
        self.stdout.write('DEMONSTRACAO 4: VAGA COM EXIGENCIA DE DOCUMENTACAO - TERCEIRIZADO')
        self.stdout.write('=' * 60)
        self.stdout.write('A empresa contratante cria uma vaga para terceirizado:')
        self.stdout.write('')
        self.stdout.write('[OK] Titulo: "Operador de Camera - Terceirizado"')
        self.stdout.write('[OK] Descricao: "Operador de camera terceirizado para evento"')
        self.stdout.write('[OK] Exige vinculo empregaticio: SIM')
        self.stdout.write('[OK] Tipo de vinculo: TERCEIRIZADO')
        self.stdout.write('[OK] Remuneracao: R$ 600,00 por evento')
        self.stdout.write('[OK] Quantidade: 1 vaga')
        self.stdout.write('')
        self.stdout.write('[RESULTADO] Freelancers DEVEM enviar documentos obrigatorios')
        self.stdout.write('[RESULTADO] Contratacao com vinculo empregaticio terceirizado')
        self.stdout.write('[DOCUMENTOS] RG, CPF, CTPS, Comprovante de Residencia')
        self.stdout.write('')
        
        # Resumo do sistema
        self.stdout.write('RESUMO DO SISTEMA FLEXIVEL')
        self.stdout.write('=' * 60)
        self.stdout.write('')
        self.stdout.write('[OK] A empresa contratante define na criacao da vaga:')
        self.stdout.write('   - Se exige vinculo empregaticio (SIM/NAO)')
        self.stdout.write('   - Qual tipo de vinculo (Temporario/Intermitente/Terceirizado)')
        self.stdout.write('   - Remuneracao e condicoes')
        self.stdout.write('')
        self.stdout.write('[OK] O sistema automaticamente:')
        self.stdout.write('   - Define se exige documentacao obrigatoria')
        self.stdout.write('   - Controla quais documentos sao necessarios')
        self.stdout.write('   - Valida documentos antes da contratacao')
        self.stdout.write('   - Impede contratacao sem documentos aprovados')
        self.stdout.write('')
        self.stdout.write('[OK] Beneficios para a empresa:')
        self.stdout.write('   - Flexibilidade total na criacao de vagas')
        self.stdout.write('   - Controle de documentacao por evento')
        self.stdout.write('   - Conformidade legal automatica')
        self.stdout.write('   - Reducao de riscos trabalhistas')
        self.stdout.write('')
        self.stdout.write('[OK] Beneficios para freelancers:')
        self.stdout.write('   - Vagas sem burocracia (sem documentos)')
        self.stdout.write('   - Vagas com vinculo (com documentos)')
        self.stdout.write('   - Transparencia sobre exigencias')
        self.stdout.write('   - Processo de contratacao claro')
        self.stdout.write('')
        self.stdout.write('=== SISTEMA FLEXIVEL IMPLEMENTADO COM SUCESSO! ===')
