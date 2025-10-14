"""
Views para dashboard de documentos do freelancer
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from app_eventos.models_documentos import (
    DocumentoFreelancerEmpresa,
    ConfiguracaoDocumentosEmpresa,
    ReutilizacaoDocumento
)
from app_eventos.models import EmpresaContratante
from app_eventos.models_freelancers import FreelancerGlobal


@login_required
def dashboard_documentos_freelancer(request):
    """
    Dashboard principal de documentos do freelancer
    """
    try:
        freelancer = FreelancerGlobal.objects.get(usuario=request.user)
    except FreelancerGlobal.DoesNotExist:
        messages.error(request, 'Perfil de freelancer não encontrado.')
        return redirect('home')
    
    # Documentos do freelancer agrupados por empresa
    documentos_por_empresa = {}
    empresas = EmpresaContratante.objects.filter(
        documentos_freelancers__freelancer=freelancer
    ).distinct()
    
    for empresa in empresas:
        docs = DocumentoFreelancerEmpresa.objects.filter(
            empresa_contratante=empresa,
            freelancer=freelancer
        ).order_by('tipo_documento')
        
        documentos_por_empresa[empresa] = {
            'documentos': docs,
            'total': docs.count(),
            'aprovados': docs.filter(status='aprovado').count(),
            'pendentes': docs.filter(status='pendente').count(),
            'rejeitados': docs.filter(status='rejeitado').count(),
            'expirados': docs.filter(status='expirado').count(),
        }
    
    # Documentos pendentes por empresa (empresas que exigem docs que o freelancer não enviou)
    empresas_com_pendencias = []
    todas_empresas = EmpresaContratante.objects.all()[:20]  # Limitar para performance
    
    for empresa in todas_empresas:
        try:
            config = ConfiguracaoDocumentosEmpresa.objects.get(empresa_contratante=empresa)
            docs_obrigatorios = config.get_documentos_obrigatorios()
            
            # Documentos que o freelancer já enviou para esta empresa
            docs_enviados = DocumentoFreelancerEmpresa.objects.filter(
                empresa_contratante=empresa,
                freelancer=freelancer
            ).values_list('tipo_documento', flat=True)
            
            # Documentos faltantes
            docs_faltantes = [doc for doc in docs_obrigatorios if doc not in docs_enviados]
            
            if docs_faltantes:
                empresas_com_pendencias.append({
                    'empresa': empresa,
                    'documentos_faltantes': docs_faltantes,
                    'total_faltantes': len(docs_faltantes)
                })
        except ConfiguracaoDocumentosEmpresa.DoesNotExist:
            continue
    
    # Documentos expirando em 30 dias
    data_limite = timezone.now() + timedelta(days=30)
    docs_expirando = DocumentoFreelancerEmpresa.objects.filter(
        freelancer=freelancer,
        status='aprovado',
        data_vencimento__lte=data_limite,
        data_vencimento__gte=timezone.now()
    ).order_by('data_vencimento')
    
    # Histórico de reutilizações
    reutilizacoes = ReutilizacaoDocumento.objects.filter(
        documento_original__freelancer=freelancer
    ).select_related(
        'documento_original',
        'vaga_utilizada',
        'candidatura'
    ).order_by('-data_reutilizacao')[:10]
    
    context = {
        'freelancer': freelancer,
        'documentos_por_empresa': documentos_por_empresa,
        'empresas_com_pendencias': empresas_com_pendencias,
        'docs_expirando': docs_expirando,
        'reutilizacoes': reutilizacoes,
        'total_empresas': len(documentos_por_empresa),
        'total_pendencias': len(empresas_com_pendencias),
        'total_expirando': docs_expirando.count(),
    }
    
    return render(request, 'freelancer/documentos/dashboard.html', context)


@login_required
def upload_documento_freelancer(request, empresa_id):
    """
    Upload de documento para uma empresa específica
    """
    try:
        freelancer = FreelancerGlobal.objects.get(usuario=request.user)
    except FreelancerGlobal.DoesNotExist:
        messages.error(request, 'Perfil de freelancer não encontrado.')
        return redirect('home')
    
    empresa = get_object_or_404(EmpresaContratante, id=empresa_id)
    
    if request.method == 'POST':
        tipo_documento = request.POST.get('tipo_documento')
        arquivo = request.FILES.get('arquivo')
        
        if not tipo_documento or not arquivo:
            messages.error(request, 'Tipo de documento e arquivo são obrigatórios.')
            return redirect('freelancer:documentos_empresa', empresa_id=empresa_id)
        
        # Verificar se já existe documento deste tipo para esta empresa
        doc_existente = DocumentoFreelancerEmpresa.objects.filter(
            empresa_contratante=empresa,
            freelancer=freelancer,
            tipo_documento=tipo_documento
        ).first()
        
        if doc_existente:
            # Atualizar documento existente
            doc_existente.arquivo = arquivo
            doc_existente.status = 'pendente'
            doc_existente.data_upload = timezone.now()
            doc_existente.save()
            messages.success(request, f'Documento {doc_existente.get_tipo_documento_display()} atualizado com sucesso!')
        else:
            # Criar novo documento
            try:
                config = ConfiguracaoDocumentosEmpresa.objects.get(empresa_contratante=empresa)
                periodo_validade = config.get_periodo_validade(tipo_documento)
            except ConfiguracaoDocumentosEmpresa.DoesNotExist:
                periodo_validade = 365
            
            data_vencimento = timezone.now() + timedelta(days=periodo_validade)
            
            DocumentoFreelancerEmpresa.objects.create(
                empresa_contratante=empresa,
                freelancer=freelancer,
                tipo_documento=tipo_documento,
                arquivo=arquivo,
                data_vencimento=data_vencimento,
                status='pendente'
            )
            messages.success(request, 'Documento enviado com sucesso! Aguarde a validação da empresa.')
        
        return redirect('freelancer:documentos_empresa', empresa_id=empresa_id)
    
    # GET - Mostrar formulário
    try:
        config = ConfiguracaoDocumentosEmpresa.objects.get(empresa_contratante=empresa)
        docs_obrigatorios = config.get_documentos_obrigatorios()
    except ConfiguracaoDocumentosEmpresa.DoesNotExist:
        docs_obrigatorios = []
    
    # Documentos já enviados
    docs_enviados = DocumentoFreelancerEmpresa.objects.filter(
        empresa_contratante=empresa,
        freelancer=freelancer
    )
    
    context = {
        'freelancer': freelancer,
        'empresa': empresa,
        'docs_obrigatorios': docs_obrigatorios,
        'docs_enviados': docs_enviados,
        'tipos_documentos': DocumentoFreelancerEmpresa.TIPO_DOCUMENTO_CHOICES,
    }
    
    return render(request, 'freelancer/documentos/upload.html', context)


@login_required
def documentos_empresa_freelancer(request, empresa_id):
    """
    Visualiza documentos do freelancer para uma empresa específica
    """
    try:
        freelancer = FreelancerGlobal.objects.get(usuario=request.user)
    except FreelancerGlobal.DoesNotExist:
        messages.error(request, 'Perfil de freelancer não encontrado.')
        return redirect('home')
    
    empresa = get_object_or_404(EmpresaContratante, id=empresa_id)
    
    # Configuração da empresa
    try:
        config = ConfiguracaoDocumentosEmpresa.objects.get(empresa_contratante=empresa)
        docs_obrigatorios = config.get_documentos_obrigatorios()
    except ConfiguracaoDocumentosEmpresa.DoesNotExist:
        config = None
        docs_obrigatorios = []
    
    # Documentos do freelancer para esta empresa
    documentos = DocumentoFreelancerEmpresa.objects.filter(
        empresa_contratante=empresa,
        freelancer=freelancer
    ).order_by('tipo_documento')
    
    # Documentos faltantes
    docs_enviados_tipos = documentos.values_list('tipo_documento', flat=True)
    docs_faltantes = [doc for doc in docs_obrigatorios if doc not in docs_enviados_tipos]
    
    # Estatísticas
    stats = {
        'total': documentos.count(),
        'aprovados': documentos.filter(status='aprovado').count(),
        'pendentes': documentos.filter(status='pendente').count(),
        'rejeitados': documentos.filter(status='rejeitado').count(),
        'faltantes': len(docs_faltantes),
    }
    
    context = {
        'freelancer': freelancer,
        'empresa': empresa,
        'config': config,
        'documentos': documentos,
        'docs_faltantes': docs_faltantes,
        'stats': stats,
        'tipos_documentos': DocumentoFreelancerEmpresa.TIPO_DOCUMENTO_CHOICES,
    }
    
    return render(request, 'freelancer/documentos/empresa.html', context)


@login_required
@require_POST
def excluir_documento_freelancer(request, documento_id):
    """
    Exclui um documento do freelancer
    """
    try:
        freelancer = FreelancerGlobal.objects.get(usuario=request.user)
    except FreelancerGlobal.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Freelancer não encontrado'}, status=404)
    
    documento = get_object_or_404(
        DocumentoFreelancerEmpresa,
        id=documento_id,
        freelancer=freelancer
    )
    
    # Não permitir excluir se estiver aprovado
    if documento.status == 'aprovado':
        return JsonResponse({
            'success': False,
            'error': 'Não é possível excluir documento aprovado. Entre em contato com a empresa.'
        }, status=400)
    
    empresa_id = documento.empresa_contratante.id
    documento.delete()
    
    return JsonResponse({
        'success': True,
        'message': 'Documento excluído com sucesso',
        'empresa_id': empresa_id
    })

