"""
Comando para verificar validade de documentos e enviar notificações
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
    help = 'Verifica validade de documentos e envia notificações'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dias-antecedencia',
            type=int,
            default=30,
            help='Dias de antecedência para notificar sobre vencimento (padrão: 30)'
        )
        parser.add_argument(
            '--empresa-id',
            type=int,
            help='ID da empresa para verificar (opcional)'
        )

    def handle(self, *args, **options):
        dias_antecedencia = options['dias_antecedencia']
        empresa_id = options.get('empresa_id')
        
        self.stdout.write('=== VERIFICACAO DE VALIDADE DE DOCUMENTOS ===')
        self.stdout.write(f'Verificando documentos que vencem em {dias_antecedencia} dias')
        self.stdout.write('')
        
        # Buscar empresas
        if empresa_id:
            empresas = EmpresaContratante.objects.filter(id=empresa_id, ativo=True)
        else:
            empresas = EmpresaContratante.objects.filter(ativo=True)
        
        if not empresas.exists():
            self.stdout.write('Nenhuma empresa ativa encontrada!')
            return
        
        total_notificacoes = 0
        
        for empresa in empresas:
            self.stdout.write(f'Verificando empresa: {empresa.nome_fantasia}')
            
            # Buscar documentos da empresa
            documentos = DocumentoFreelancerEmpresa.objects.filter(
                empresa_contratante=empresa,
                status='aprovado'
            ).select_related('freelancer__usuario')
            
            if not documentos.exists():
                self.stdout.write(f'  [INFO] Nenhum documento encontrado para {empresa.nome_fantasia}')
                continue
            
            # Calcular datas de verificação
            hoje = timezone.now().date()
            data_limite = hoje + timedelta(days=dias_antecedencia)
            
            # Documentos próximos do vencimento
            documentos_vencendo = documentos.filter(
                data_vencimento__lte=data_limite,
                data_vencimento__gt=hoje
            )
            
            # Documentos já expirados
            documentos_expirados = documentos.filter(
                data_vencimento__lt=hoje
            )
            
            # Documentos válidos
            documentos_validos = documentos.filter(
                data_vencimento__gt=data_limite
            )
            
            self.stdout.write(f'  - Total de documentos: {documentos.count()}')
            self.stdout.write(f'  - Documentos válidos: {documentos_validos.count()}')
            self.stdout.write(f'  - Documentos vencendo: {documentos_vencendo.count()}')
            self.stdout.write(f'  - Documentos expirados: {documentos_expirados.count()}')
            
            # Notificar sobre documentos vencendo
            for doc in documentos_vencendo:
                dias_para_vencer = (doc.data_vencimento - hoje).days
                
                # Notificar empresa
                notificacao_empresa = Notificacao.objects.create(
                    usuario=empresa.empresa_contratante.first() if hasattr(empresa, 'empresa_contratante') else None,
                    titulo=f'Documento próximo do vencimento',
                    mensagem=f'O documento {doc.get_tipo_documento_display()} do freelancer {doc.freelancer.usuario.username} vence em {dias_para_vencer} dias.',
                    tipo='documento_vencendo',
                    prioridade='media',
                    data_vencimento=doc.data_vencimento
                )
                
                # Notificar freelancer
                notificacao_freelancer = Notificacao.objects.create(
                    usuario=doc.freelancer.usuario,
                    titulo=f'Documento próximo do vencimento',
                    mensagem=f'Seu documento {doc.get_tipo_documento_display()} vence em {dias_para_vencer} dias. Atualize-o para continuar recebendo vagas.',
                    tipo='documento_vencendo',
                    prioridade='media',
                    data_vencimento=doc.data_vencimento
                )
                
                self.stdout.write(f'    [NOTIFICACAO] {doc.get_tipo_documento_display()} - {doc.freelancer.usuario.username} (vence em {dias_para_vencer} dias)')
                total_notificacoes += 2
            
            # Notificar sobre documentos expirados
            for doc in documentos_expirados:
                dias_expirado = (hoje - doc.data_vencimento).days
                
                # Notificar empresa
                notificacao_empresa = Notificacao.objects.create(
                    usuario=empresa.empresa_contratante.first() if hasattr(empresa, 'empresa_contratante') else None,
                    titulo=f'Documento expirado',
                    mensagem=f'O documento {doc.get_tipo_documento_display()} do freelancer {doc.freelancer.usuario.username} está expirado há {dias_expirado} dias.',
                    tipo='documento_expirado',
                    prioridade='alta',
                    data_vencimento=doc.data_vencimento
                )
                
                # Notificar freelancer
                notificacao_freelancer = Notificacao.objects.create(
                    usuario=doc.freelancer.usuario,
                    titulo=f'Documento expirado',
                    mensagem=f'Seu documento {doc.get_tipo_documento_display()} está expirado há {dias_expirado} dias. Atualize-o para continuar recebendo vagas.',
                    tipo='documento_expirado',
                    prioridade='alta',
                    data_vencimento=doc.data_vencimento
                )
                
                self.stdout.write(f'    [ALERTA] {doc.get_tipo_documento_display()} - {doc.freelancer.usuario.username} (expirado há {dias_expirado} dias)')
                total_notificacoes += 2
            
            # Resumo por empresa
            self.stdout.write(f'  [RESUMO] {empresa.nome_fantasia}:')
            self.stdout.write(f'    - Documentos válidos: {documentos_validos.count()}')
            self.stdout.write(f'    - Documentos vencendo: {documentos_vencendo.count()}')
            self.stdout.write(f'    - Documentos expirados: {documentos_expirados.count()}')
            self.stdout.write('')
        
        # Resumo geral
        self.stdout.write('=== RESUMO GERAL ===')
        self.stdout.write(f'Total de notificações enviadas: {total_notificacoes}')
        self.stdout.write(f'Empresas verificadas: {empresas.count()}')
        
        # Estatísticas por tipo de documento
        self.stdout.write('\n=== ESTATISTICAS POR TIPO DE DOCUMENTO ===')
        todos_documentos = DocumentoFreelancerEmpresa.objects.filter(
            empresa_contratante__in=empresas,
            status='aprovado'
        )
        
        tipos_documento = todos_documentos.values_list('tipo_documento', flat=True).distinct()
        
        for tipo in tipos_documento:
            docs_tipo = todos_documentos.filter(tipo_documento=tipo)
            docs_vencendo = docs_tipo.filter(
                data_vencimento__lte=timezone.now().date() + timedelta(days=dias_antecedencia),
                data_vencimento__gt=timezone.now().date()
            )
            docs_expirados = docs_tipo.filter(
                data_vencimento__lt=timezone.now().date()
            )
            
            self.stdout.write(f'  {tipo}:')
            self.stdout.write(f'    - Total: {docs_tipo.count()}')
            self.stdout.write(f'    - Vencendo: {docs_vencendo.count()}')
            self.stdout.write(f'    - Expirados: {docs_expirados.count()}')
        
        self.stdout.write('\n=== VERIFICACAO CONCLUIDA ===')
        self.stdout.write('Notificações enviadas para empresas e freelancers!')
