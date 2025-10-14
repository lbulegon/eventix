"""
Views para dashboard de validação de documentos da empresa
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q, Count

from app_eventos.models_documentos import (
    DocumentoFreelancerEmpresa,
    ConfiguracaoDocumentosEmpresa
)
from app_eventos.models import EmpresaContratante


@login_required
def dashboard_documentos_empresa(request):
    """
    Dashboard principal de validação de documentos da empresa
    """
    if request.user.tipo_usuario not in ['admin_empresa', 'operador_empresa']:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard_empresa:login_empresa')
    
    empresa = request.user.empresa_contratante
    
    # Filtros
    status_filtro = request.GET.get('status', 'todos')
    busca = request.GET.get('busca', '')
    
    # Documentos da empresa
    documentos = DocumentoFreelancerEmpresa.objects.filter(
        empresa_contratante=empresa
    ).select_related('freelancer__usuario')
    
    # Aplicar filtros
    if status_filtro != 'todos':
        documentos = documentos.filter(status=status_filtro)
    
    if busca:
        documentos = documentos.filter(
            Q(freelancer__usuario__first_name__icontains=busca) |
            Q(freelancer__usuario__last_name__icontains=busca) |
            Q(freelancer__usuario__username__icontains=busca)
        )
    
    documentos = documentos.order_by('-data_upload')
    
    # Estatísticas
    stats = {
        'total': DocumentoFreelancerEmpresa.objects.filter(empresa_contratante=empresa).count(),
        'pendentes': DocumentoFreelancerEmpresa.objects.filter(empresa_contratante=empresa, status='pendente').count(),
        'aprovados': DocumentoFreelancerEmpresa.objects.filter(empresa_contratante=empresa, status='aprovado').count(),
        'rejeitados': DocumentoFreelancerEmpresa.objects.filter(empresa_contratante=empresa, status='rejeitado').count(),
        'expirados': DocumentoFreelancerEmpresa.objects.filter(empresa_contratante=empresa, status='expirado').count(),
    }
    
    # Documentos expirando em 30 dias
    data_limite = timezone.now() + timedelta(days=30)
    docs_expirando = DocumentoFreelancerEmpresa.objects.filter(
        empresa_contratante=empresa,
        status='aprovado',
        data_vencimento__lte=data_limite,
        data_vencimento__gte=timezone.now()
    ).select_related('freelancer__usuario').order_by('data_vencimento')[:10]
    
    # Freelancers com mais documentos
    freelancers_top = DocumentoFreelancerEmpresa.objects.filter(
        empresa_contratante=empresa,
        status='aprovado'
    ).values(
        'freelancer__id',
        'freelancer__usuario__first_name',
        'freelancer__usuario__last_name'
    ).annotate(
        total_docs=Count('id')
    ).order_by('-total_docs')[:5]
    
    context = {
        'empresa': empresa,
        'documentos': documentos[:50],  # Primeiros 50
        'stats': stats,
        'docs_expirando': docs_expirando,
        'freelancers_top': freelancers_top,
        'status_filtro': status_filtro,
        'busca': busca,
    }
    
    return render(request, 'dashboard_empresa/documentos/dashboard.html', context)


@login_required
def documentos_pendentes_empresa(request):
    """
    Lista documentos pendentes de validação
    """
    if request.user.tipo_usuario not in ['admin_empresa', 'operador_empresa']:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard_empresa:login_empresa')
    
    empresa = request.user.empresa_contratante
    
    # Documentos pendentes
    documentos_pendentes = DocumentoFreelancerEmpresa.objects.filter(
        empresa_contratante=empresa,
        status='pendente'
    ).select_related('freelancer__usuario').order_by('-data_upload')
    
    context = {
        'empresa': empresa,
        'documentos': documentos_pendentes,
        'total': documentos_pendentes.count(),
    }
    
    return render(request, 'dashboard_empresa/documentos/pendentes.html', context)


@login_required
def validar_documento_empresa(request, documento_id):
    """
    Visualizar e validar documento
    """
    if request.user.tipo_usuario not in ['admin_empresa', 'operador_empresa']:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard_empresa:login_empresa')
    
    empresa = request.user.empresa_contratante
    
    documento = get_object_or_404(
        DocumentoFreelancerEmpresa,
        id=documento_id,
        empresa_contratante=empresa
    )
    
    if request.method == 'POST':
        acao = request.POST.get('acao')
        observacoes = request.POST.get('observacoes', '')
        
        if acao == 'aprovar':
            documento.status = 'aprovado'
            documento.validado_por = request.user
            documento.data_validacao = timezone.now()
            documento.observacoes = observacoes
            documento.save()
            messages.success(request, f'Documento {documento.get_tipo_documento_display()} aprovado com sucesso!')
        
        elif acao == 'rejeitar':
            if not observacoes:
                messages.error(request, 'Observações são obrigatórias ao rejeitar um documento.')
                return redirect('dashboard_empresa:validar_documento', documento_id=documento_id)
            
            documento.status = 'rejeitado'
            documento.validado_por = request.user
            documento.data_validacao = timezone.now()
            documento.observacoes = observacoes
            documento.save()
            messages.warning(request, f'Documento {documento.get_tipo_documento_display()} rejeitado.')
        
        return redirect('dashboard_empresa:documentos_pendentes')
    
    context = {
        'empresa': empresa,
        'documento': documento,
        'freelancer': documento.freelancer,
    }
    
    return render(request, 'dashboard_empresa/documentos/validar.html', context)


@login_required
def configurar_documentos_empresa(request):
    """
    Configurar documentos obrigatórios da empresa
    """
    if request.user.tipo_usuario != 'admin_empresa':
        messages.error(request, 'Apenas administradores podem configurar documentos.')
        return redirect('dashboard_empresa:home_empresa')
    
    empresa = request.user.empresa_contratante
    
    # Buscar ou criar configuração
    config, created = ConfiguracaoDocumentosEmpresa.objects.get_or_create(
        empresa_contratante=empresa
    )
    
    if request.method == 'POST':
        # Atualizar configuração
        config.rg_obrigatorio = request.POST.get('rg_obrigatorio') == 'on'
        config.cpf_obrigatorio = request.POST.get('cpf_obrigatorio') == 'on'
        config.ctps_obrigatorio = request.POST.get('ctps_obrigatorio') == 'on'
        config.comprovante_residencia_obrigatorio = request.POST.get('comprovante_residencia_obrigatorio') == 'on'
        config.certificado_reservista_obrigatorio = request.POST.get('certificado_reservista_obrigatorio') == 'on'
        config.comprovante_escolaridade_obrigatorio = request.POST.get('comprovante_escolaridade_obrigatorio') == 'on'
        config.certificado_profissional_obrigatorio = request.POST.get('certificado_profissional_obrigatorio') == 'on'
        
        # Períodos de validade
        config.periodo_validade_rg = int(request.POST.get('periodo_validade_rg', 365))
        config.periodo_validade_cpf = int(request.POST.get('periodo_validade_cpf', 365))
        config.periodo_validade_ctps = int(request.POST.get('periodo_validade_ctps', 365))
        config.periodo_validade_residencia = int(request.POST.get('periodo_validade_residencia', 90))
        config.periodo_validade_reservista = int(request.POST.get('periodo_validade_reservista', 365))
        config.periodo_validade_escolaridade = int(request.POST.get('periodo_validade_escolaridade', 365))
        config.periodo_validade_profissional = int(request.POST.get('periodo_validade_profissional', 365))
        
        # Configurações gerais
        config.aceita_documentos_externos = request.POST.get('aceita_documentos_externos') == 'on'
        config.periodo_validade_padrao = int(request.POST.get('periodo_validade_padrao', 365))
        
        config.save()
        messages.success(request, 'Configuração de documentos atualizada com sucesso!')
        return redirect('dashboard_empresa:configurar_documentos')
    
    context = {
        'empresa': empresa,
        'config': config,
    }
    
    return render(request, 'dashboard_empresa/documentos/configurar.html', context)


@login_required
def documentos_freelancer_empresa(request, freelancer_id):
    """
    Visualiza todos os documentos de um freelancer específico
    """
    if request.user.tipo_usuario not in ['admin_empresa', 'operador_empresa']:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard_empresa:login_empresa')
    
    empresa = request.user.empresa_contratante
    
    from app_eventos.models_freelancers import FreelancerGlobal
    freelancer = get_object_or_404(FreelancerGlobal, id=freelancer_id)
    
    # Documentos do freelancer para esta empresa
    documentos = DocumentoFreelancerEmpresa.objects.filter(
        empresa_contratante=empresa,
        freelancer=freelancer
    ).order_by('tipo_documento')
    
    # Configuração da empresa
    try:
        config = ConfiguracaoDocumentosEmpresa.objects.get(empresa_contratante=empresa)
        docs_obrigatorios = config.get_documentos_obrigatorios()
    except ConfiguracaoDocumentosEmpresa.DoesNotExist:
        config = None
        docs_obrigatorios = []
    
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
        'empresa': empresa,
        'freelancer': freelancer,
        'documentos': documentos,
        'docs_faltantes': docs_faltantes,
        'stats': stats,
        'config': config,
    }
    
    return render(request, 'dashboard_empresa/documentos/freelancer.html', context)


@login_required
@require_POST
def aprovar_documento_ajax(request, documento_id):
    """
    Aprovar documento via AJAX
    """
    if request.user.tipo_usuario not in ['admin_empresa', 'operador_empresa']:
        return JsonResponse({'success': False, 'error': 'Acesso negado'}, status=403)
    
    empresa = request.user.empresa_contratante
    
    documento = get_object_or_404(
        DocumentoFreelancerEmpresa,
        id=documento_id,
        empresa_contratante=empresa
    )
    
    documento.status = 'aprovado'
    documento.validado_por = request.user
    documento.data_validacao = timezone.now()
    documento.save()
    
    return JsonResponse({
        'success': True,
        'message': f'Documento {documento.get_tipo_documento_display()} aprovado!'
    })


@login_required
@require_POST
def rejeitar_documento_ajax(request, documento_id):
    """
    Rejeitar documento via AJAX
    """
    if request.user.tipo_usuario not in ['admin_empresa', 'operador_empresa']:
        return JsonResponse({'success': False, 'error': 'Acesso negado'}, status=403)
    
    empresa = request.user.empresa_contratante
    
    documento = get_object_or_404(
        DocumentoFreelancerEmpresa,
        id=documento_id,
        empresa_contratante=empresa
    )
    
    observacoes = request.POST.get('observacoes', '')
    if not observacoes:
        return JsonResponse({
            'success': False,
            'error': 'Observações são obrigatórias ao rejeitar'
        }, status=400)
    
    documento.status = 'rejeitado'
    documento.validado_por = request.user
    documento.data_validacao = timezone.now()
    documento.observacoes = observacoes
    documento.save()
    
    return JsonResponse({
        'success': True,
        'message': f'Documento {documento.get_tipo_documento_display()} rejeitado'
    })

