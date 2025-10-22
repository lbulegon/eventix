"""
Views para Dashboard Personalizado da Empresa
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import (
    Evento, SetorEvento, Vaga, Candidatura, ContratoFreelance, Freelance,
    Equipamento, ManutencaoEquipamento, DespesaEvento, ReceitaEvento,
    User, GrupoPermissaoEmpresa, LocalEvento, Empresa, Funcao
)
from .mixins import EmpresaContratanteRequiredMixin


@csrf_protect
def login_empresa(request):
    """
    View de login para usuários de empresa
    """
    # Se já está logado
    if request.user.is_authenticated:
        # Usuários de empresa vão direto para o dashboard
        if request.user.tipo_usuario in ['admin_empresa', 'operador_empresa']:
            return redirect('dashboard_empresa:dashboard_empresa')
        
        # Para outros tipos de usuário, renderizar o template com mensagem
        # NÃO redirecionar - isso estava causando o problema
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Verificar se é usuário de empresa
            if user.tipo_usuario in ['admin_empresa', 'operador_empresa']:
                login(request, user)
                messages.success(request, f'Bem-vindo(a), {user.get_full_name() or user.username}!')
                return redirect('dashboard_empresa:dashboard_empresa')
            else:
                messages.error(request, 'Este login é exclusivo para usuários de empresa. Use /admin para acessar.')
        else:
            messages.error(request, 'Usuário ou senha incorretos.')
    
    return render(request, 'dashboard_empresa/login.html')


def logout_empresa(request):
    """
    View de logout para usuários de empresa
    """
    logout(request)
    messages.success(request, 'Você saiu com sucesso.')
    return redirect('dashboard_empresa:login_empresa')


@login_required(login_url='/empresa/login/')
def test_dashboard(request):
    """
    View de teste para verificar se o dashboard está funcionando
    """
    # Verificar se é usuário de empresa
    if request.user.tipo_usuario not in ['admin_empresa', 'operador_empresa']:
        messages.error(request, 'Acesso negado. Apenas usuários de empresa podem acessar este dashboard.')
        return redirect('dashboard_empresa:login_empresa')
    
    if not request.user.empresa_contratante:
        messages.error(request, 'Usuário não está associado a nenhuma empresa.')
        return redirect('dashboard_empresa:login_empresa')
    
    empresa = request.user.empresa_contratante
    
    context = {
        'empresa': empresa,
        'user': request.user,
    }
    
    return render(request, 'dashboard_empresa/test.html', context)


@login_required(login_url='/empresa/login/')
def dashboard_empresa(request):
    """
    Dashboard principal da empresa
    """
    # Verificar se é usuário de empresa
    if request.user.tipo_usuario not in ['admin_empresa', 'operador_empresa']:
        messages.error(request, 'Acesso negado. Apenas usuários de empresa podem acessar este dashboard.')
        return redirect('home')
    
    if not request.user.empresa_contratante:
        messages.error(request, 'Usuário não está associado a nenhuma empresa.')
        return redirect('home')
    
    empresa = request.user.empresa_contratante
    
    # Estatísticas gerais
    stats = {
        'total_eventos': Evento.objects.filter(empresa_contratante=empresa).count(),
        'eventos_ativos': Evento.objects.filter(empresa_contratante=empresa, ativo=True).count(),
        'total_vagas': Vaga.objects.filter(empresa_contratante=empresa).aggregate(Sum('quantidade'))['quantidade__sum'] or 0,
        'vagas_ativas': Vaga.objects.filter(empresa_contratante=empresa, ativa=True).aggregate(Sum('quantidade'))['quantidade__sum'] or 0,
        'total_candidaturas': Candidatura.objects.filter(vaga__empresa_contratante=empresa).count(),
        'candidaturas_pendentes': Candidatura.objects.filter(vaga__empresa_contratante=empresa, status='pendente').count(),
        'total_freelancers': Freelance.objects.filter(
            candidaturas__vaga__empresa_contratante=empresa
        ).distinct().count(),
        'total_equipamentos': Equipamento.objects.filter(empresa_contratante=empresa).count(),
        'equipamentos_ativos': Equipamento.objects.filter(empresa_contratante=empresa, ativo=True).count(),
        'total_usuarios': User.objects.filter(empresa_contratante=empresa).count(),
    }
    
    # Eventos recentes
    eventos_recentes = Evento.objects.filter(
        empresa_contratante=empresa
    ).order_by('-data_criacao')[:5]
    
    # Candidaturas recentes
    candidaturas_recentes = Candidatura.objects.filter(
        vaga__empresa_contratante=empresa
    ).order_by('-data_candidatura')[:5]
    
    # Receitas e despesas do mês atual
    hoje = timezone.now()
    inicio_mes = hoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    receitas_mes = ReceitaEvento.objects.filter(
        evento__empresa_contratante=empresa,
        data_vencimento__gte=inicio_mes
    ).aggregate(total=Sum('valor'))['total'] or 0
    
    despesas_mes = DespesaEvento.objects.filter(
        evento__empresa_contratante=empresa,
        data_vencimento__gte=inicio_mes
    ).aggregate(total=Sum('valor'))['total'] or 0
    
    stats['receitas_mes'] = receitas_mes
    stats['despesas_mes'] = despesas_mes
    stats['saldo_mes'] = receitas_mes - despesas_mes
    
    context = {
        'empresa': empresa,
        'stats': stats,
        'eventos_recentes': eventos_recentes,
        'candidaturas_recentes': candidaturas_recentes,
        'user': request.user,
    }
    
    return render(request, 'dashboard_empresa/home.html', context)


@login_required(login_url='/empresa/login/')
def eventos_empresa(request):
    """
    Lista de eventos da empresa
    """
    if request.user.tipo_usuario not in ['admin_empresa', 'operador_empresa']:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard_empresa:login_empresa')
    
    empresa = request.user.empresa_contratante
    eventos = Evento.objects.filter(empresa_contratante=empresa).order_by('-data_criacao')
    
    context = {
        'empresa': empresa,
        'eventos': eventos,
        'user': request.user,
    }
    
    return render(request, 'dashboard_empresa/eventos.html', context)


@login_required(login_url='/empresa/login/')
def detalhe_evento(request, evento_id):
    """
    Detalhes do evento com freelancers aprovados
    """
    if request.user.tipo_usuario not in ['admin_empresa', 'operador_empresa']:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard_empresa:login_empresa')
    
    empresa = request.user.empresa_contratante
    
    # Buscar evento
    evento = get_object_or_404(
        Evento.objects.select_related('local', 'empresa_produtora'),
        id=evento_id,
        empresa_contratante=empresa
    )
    
    # Buscar setores do evento
    setores = SetorEvento.objects.filter(evento=evento).prefetch_related('vagas')
    
    # Buscar todas as vagas do evento
    vagas = Vaga.objects.filter(setor__evento=evento).select_related('setor')
    
    # Buscar freelancers aprovados para este evento
    candidaturas_aprovadas = Candidatura.objects.filter(
        vaga__setor__evento=evento,
        status='aprovado'
    ).select_related('freelance', 'vaga', 'vaga__setor').order_by('vaga__setor__nome', 'vaga__titulo')
    
    # Buscar todas as candidaturas do evento
    todas_candidaturas = Candidatura.objects.filter(
        vaga__setor__evento=evento
    ).select_related('freelance', 'vaga', 'vaga__setor')
    
    # Estatísticas do evento
    stats_evento = {
        'total_setores': setores.count(),
        'total_vagas': vagas.aggregate(Sum('quantidade'))['quantidade__sum'] or 0,
        'vagas_ativas': vagas.filter(ativa=True).aggregate(Sum('quantidade'))['quantidade__sum'] or 0,
        'total_candidaturas': todas_candidaturas.count(),
        'aprovadas': todas_candidaturas.filter(status='aprovado').count(),
        'pendentes': todas_candidaturas.filter(status='pendente').count(),
        'rejeitadas': todas_candidaturas.filter(status='rejeitado').count(),
        'total_freelancers_aprovados': candidaturas_aprovadas.count(),
    }
    
    context = {
        'empresa': empresa,
        'evento': evento,
        'setores': setores,
        'vagas': vagas,
        'candidaturas_aprovadas': candidaturas_aprovadas,
        'stats_evento': stats_evento,
        'user': request.user,
    }
    
    return render(request, 'dashboard_empresa/detalhe_evento.html', context)


@login_required(login_url='/empresa/login/')
def criar_evento(request):
    """
    Criar novo evento
    """
    if request.user.tipo_usuario not in ['admin_empresa', 'operador_empresa']:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard_empresa:login_empresa')
    
    empresa = request.user.empresa_contratante
    
    if request.method == 'POST':
        nome = request.POST.get('nome')
        data_inicio = request.POST.get('data_inicio')
        data_fim = request.POST.get('data_fim')
        descricao = request.POST.get('descricao', '')
        local_id = request.POST.get('local')
        empresa_produtora_id = request.POST.get('empresa_produtora')
        ativo = request.POST.get('ativo') == 'on'
        
        # Validações
        if not nome or not data_inicio or not data_fim or not local_id:
            messages.error(request, 'Preencha todos os campos obrigatórios.')
        else:
            try:
                # Buscar local
                local = LocalEvento.objects.get(id=local_id)
                
                # Buscar empresa produtora (opcional)
                empresa_produtora = None
                if empresa_produtora_id:
                    empresa_produtora = Empresa.objects.get(id=empresa_produtora_id)
                
                # Criar evento
                evento = Evento.objects.create(
                    empresa_contratante=empresa,
                    nome=nome,
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                    descricao=descricao,
                    local=local,
                    empresa_produtora=empresa_produtora,
                    ativo=ativo
                )
                
                messages.success(request, f'Evento "{evento.nome}" criado com sucesso!')
                return redirect('dashboard_empresa:detalhe_evento', evento_id=evento.id)
                
            except LocalEvento.DoesNotExist:
                messages.error(request, 'Local não encontrado.')
            except Empresa.DoesNotExist:
                messages.error(request, 'Empresa produtora não encontrada.')
            except Exception as e:
                messages.error(request, f'Erro ao criar evento: {str(e)}')
    
    # Buscar locais e empresas para o formulário
    locais = LocalEvento.objects.filter(ativo=True)
    empresas_produtoras = Empresa.objects.filter(ativo=True)
    
    context = {
        'empresa': empresa,
        'locais': locais,
        'empresas_produtoras': empresas_produtoras,
        'user': request.user,
    }
    
    return render(request, 'dashboard_empresa/criar_evento.html', context)


@login_required(login_url='/empresa/login/')
def editar_evento(request, evento_id):
    """
    Editar evento existente
    """
    if request.user.tipo_usuario not in ['admin_empresa', 'operador_empresa']:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard_empresa:login_empresa')
    
    empresa = request.user.empresa_contratante
    
    # Buscar evento
    evento = get_object_or_404(
        Evento,
        id=evento_id,
        empresa_contratante=empresa
    )
    
    if request.method == 'POST':
        nome = request.POST.get('nome')
        data_inicio = request.POST.get('data_inicio')
        data_fim = request.POST.get('data_fim')
        descricao = request.POST.get('descricao', '')
        local_id = request.POST.get('local')
        empresa_produtora_id = request.POST.get('empresa_produtora')
        ativo = request.POST.get('ativo') == 'on'
        
        # Validações
        if not nome or not data_inicio or not data_fim or not local_id:
            messages.error(request, 'Preencha todos os campos obrigatórios.')
        else:
            try:
                # Buscar local
                local = LocalEvento.objects.get(id=local_id)
                
                # Buscar empresa produtora (opcional)
                empresa_produtora = None
                if empresa_produtora_id:
                    empresa_produtora = Empresa.objects.get(id=empresa_produtora_id)
                
                # Atualizar evento
                evento.nome = nome
                evento.data_inicio = data_inicio
                evento.data_fim = data_fim
                evento.descricao = descricao
                evento.local = local
                evento.empresa_produtora = empresa_produtora
                evento.ativo = ativo
                evento.save()
                
                messages.success(request, f'Evento "{evento.nome}" atualizado com sucesso!')
                return redirect('dashboard_empresa:detalhe_evento', evento_id=evento.id)
                
            except LocalEvento.DoesNotExist:
                messages.error(request, 'Local não encontrado.')
            except Empresa.DoesNotExist:
                messages.error(request, 'Empresa produtora não encontrada.')
            except Exception as e:
                messages.error(request, f'Erro ao atualizar evento: {str(e)}')
    
    # Buscar locais e empresas para o formulário
    locais = LocalEvento.objects.filter(ativo=True)
    empresas_produtoras = Empresa.objects.filter(ativo=True)
    
    context = {
        'empresa': empresa,
        'evento': evento,
        'locais': locais,
        'empresas_produtoras': empresas_produtoras,
        'user': request.user,
    }
    
    return render(request, 'dashboard_empresa/editar_evento.html', context)


@login_required(login_url='/empresa/login/')
def criar_setor(request, evento_id):
    """
    Criar novo setor para o evento
    """
    if request.user.tipo_usuario not in ['admin_empresa', 'operador_empresa']:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard_empresa:login_empresa')
    
    empresa = request.user.empresa_contratante
    
    # Buscar evento
    evento = get_object_or_404(
        Evento,
        id=evento_id,
        empresa_contratante=empresa
    )
    
    if request.method == 'POST':
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao', '')
        
        if nome:
            setor = SetorEvento.objects.create(
                evento=evento,
                nome=nome,
                descricao=descricao,
                ativo=True
            )
            messages.success(request, f'Setor "{nome}" criado com sucesso!')
            return redirect('dashboard_empresa:detalhe_evento', evento_id=evento.id)
        else:
            messages.error(request, 'Nome do setor é obrigatório.')
    
    context = {
        'empresa': empresa,
        'evento': evento,
        'user': request.user,
    }
    
    return render(request, 'dashboard_empresa/criar_setor.html', context)


@login_required(login_url='/empresa/login/')
def criar_vaga(request, setor_id):
    """
    Criar nova vaga para o setor
    """
    if request.user.tipo_usuario not in ['admin_empresa', 'operador_empresa']:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard_empresa:login_empresa')
    
    empresa = request.user.empresa_contratante
    
    # Buscar setor
    setor = get_object_or_404(
        SetorEvento.objects.select_related('evento'),
        id=setor_id,
        evento__empresa_contratante=empresa
    )
    
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        descricao = request.POST.get('descricao', '')
        quantidade = request.POST.get('quantidade')
        remuneracao = request.POST.get('remuneracao')
        tipo_remuneracao = request.POST.get('tipo_remuneracao', 'por_dia')
        nivel_experiencia = request.POST.get('nivel_experiencia', 'iniciante')
        funcao_id = request.POST.get('funcao')
        
        if titulo and quantidade and remuneracao and funcao_id:
            try:
                funcao = Funcao.objects.get(id=funcao_id)
                
                vaga = Vaga.objects.create(
                    evento=setor.evento,
                    setor=setor,
                    empresa_contratante=empresa,
                    titulo=titulo,
                    descricao=descricao,
                    quantidade=int(quantidade),
                    remuneracao=float(remuneracao),
                    tipo_remuneracao=tipo_remuneracao,
                    nivel_experiencia=nivel_experiencia,
                    funcao=funcao,
                    ativa=True
                )
                messages.success(request, f'Vaga "{titulo}" criada com sucesso!')
                return redirect('dashboard_empresa:detalhe_evento', evento_id=setor.evento.id)
            except Funcao.DoesNotExist:
                messages.error(request, 'Função selecionada não encontrada.')
        else:
            messages.error(request, 'Preencha todos os campos obrigatórios, incluindo a Função.')
    
    # Buscar funções disponíveis (globais ou da empresa)
    funcoes = Funcao.objects.filter(
        Q(empresa_contratante=empresa) | Q(empresa_contratante__isnull=True),
        ativo=True,
        disponivel_para_vagas=True
    ).select_related('tipo_funcao').order_by('tipo_funcao__nome', 'nome')
    
    context = {
        'empresa': empresa,
        'setor': setor,
        'evento': setor.evento,
        'funcoes': funcoes,
        'user': request.user,
    }
    
    return render(request, 'dashboard_empresa/criar_vaga.html', context)


@login_required(login_url='/empresa/login/')
def criar_vaga_generica(request, evento_id):
    """
    Criar vaga genérica (sem setor) para o evento
    """
    if request.user.tipo_usuario not in ['admin_empresa', 'operador_empresa']:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard_empresa:login_empresa')
    
    empresa = request.user.empresa_contratante
    
    # Buscar evento
    evento = get_object_or_404(
        Evento,
        id=evento_id,
        empresa_contratante=empresa
    )
    
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        descricao = request.POST.get('descricao', '')
        quantidade = request.POST.get('quantidade')
        remuneracao = request.POST.get('remuneracao')
        tipo_remuneracao = request.POST.get('tipo_remuneracao', 'por_dia')
        nivel_experiencia = request.POST.get('nivel_experiencia', 'iniciante')
        funcao_id = request.POST.get('funcao')
        
        if titulo and quantidade and remuneracao and funcao_id:
            try:
                funcao = Funcao.objects.get(id=funcao_id)
                
                vaga = Vaga.objects.create(
                    evento=evento,
                    setor=None,  # Vaga genérica sem setor
                    empresa_contratante=empresa,
                    titulo=titulo,
                    descricao=descricao,
                    quantidade=int(quantidade),
                    remuneracao=float(remuneracao),
                    tipo_remuneracao=tipo_remuneracao,
                    nivel_experiencia=nivel_experiencia,
                    funcao=funcao,
                    ativa=True
                )
                messages.success(request, f'Vaga genérica "{titulo}" criada com sucesso!')
                return redirect('dashboard_empresa:gerenciar_vagas_evento', evento_id=evento.id)
            except Funcao.DoesNotExist:
                messages.error(request, 'Função selecionada não encontrada.')
        else:
            messages.error(request, 'Preencha todos os campos obrigatórios, incluindo a Função.')
    
    # Buscar funções disponíveis
    funcoes = Funcao.objects.filter(
        Q(empresa_contratante=empresa) | Q(empresa_contratante__isnull=True),
        ativo=True,
        disponivel_para_vagas=True
    ).select_related('tipo_funcao').order_by('tipo_funcao__nome', 'nome')
    
    context = {
        'empresa': empresa,
        'evento': evento,
        'funcoes': funcoes,
        'user': request.user,
    }
    
    return render(request, 'dashboard_empresa/criar_vaga_generica.html', context)


@login_required(login_url='/empresa/login/')
def atrelar_vaga_setor(request, vaga_id):
    """
    Atrelar vaga a um setor
    """
    if request.user.tipo_usuario not in ['admin_empresa', 'operador_empresa']:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard_empresa:login_empresa')
    
    empresa = request.user.empresa_contratante
    
    # Buscar vaga
    vaga = get_object_or_404(
        Vaga.objects.select_related('evento'),
        id=vaga_id,
        empresa_contratante=empresa
    )
    
    if request.method == 'POST':
        setor_id = request.POST.get('setor')
        
        if setor_id:
            try:
                setor = SetorEvento.objects.get(id=setor_id, evento=vaga.evento)
                vaga.setor = setor
                vaga.save()
                messages.success(request, f'Vaga "{vaga.titulo}" atrelada ao setor "{setor.nome}"!')
                return redirect('dashboard_empresa:gerenciar_vagas_evento', evento_id=vaga.evento.id)
            except SetorEvento.DoesNotExist:
                messages.error(request, 'Setor não encontrado.')
        else:
            messages.error(request, 'Selecione um setor.')
    
    # Buscar setores do evento
    setores = SetorEvento.objects.filter(evento=vaga.evento).order_by('nome')
    
    context = {
        'empresa': empresa,
        'vaga': vaga,
        'evento': vaga.evento,
        'setores': setores,
        'user': request.user,
    }
    
    return render(request, 'dashboard_empresa/atrelar_vaga_setor.html', context)


@login_required(login_url='/empresa/login/')
def desatrelar_vaga_setor(request, vaga_id):
    """
    Desatrelar vaga de um setor (torna genérica)
    """
    if request.user.tipo_usuario not in ['admin_empresa', 'operador_empresa']:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard_empresa:login_empresa')
    
    empresa = request.user.empresa_contratante
    
    # Buscar vaga
    vaga = get_object_or_404(
        Vaga,
        id=vaga_id,
        empresa_contratante=empresa
    )
    
    if vaga.setor:
        setor_nome = vaga.setor.nome
        vaga.setor = None
        vaga.save()
        messages.success(request, f'Vaga "{vaga.titulo}" desatrelada do setor "{setor_nome}" e agora é genérica!')
    else:
        messages.info(request, 'Vaga já é genérica (sem setor).')
    
    return redirect('dashboard_empresa:gerenciar_vagas_evento', evento_id=vaga.evento.id)


@login_required(login_url='/empresa/login/')
def gerenciar_vagas_evento(request, evento_id):
    """
    Gerenciar todas as vagas de um evento com filtros por setor
    """
    if request.user.tipo_usuario not in ['admin_empresa', 'operador_empresa']:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard_empresa:login_empresa')
    
    empresa = request.user.empresa_contratante
    
    # Buscar evento
    evento = get_object_or_404(
        Evento,
        id=evento_id,
        empresa_contratante=empresa
    )
    
    # Filtros
    setor_id = request.GET.get('setor')
    status_filtro = request.GET.get('status', 'todas')
    tipo_filtro = request.GET.get('tipo', 'todas')  # todas, genericas, setores
    
    # Buscar vagas do evento (com ou sem setor)
    vagas = Vaga.objects.filter(evento=evento).select_related('setor', 'funcao')
    
    # Filtro por tipo (genéricas ou de setores)
    if tipo_filtro == 'genericas':
        vagas = vagas.filter(setor__isnull=True)
    elif tipo_filtro == 'setores':
        vagas = vagas.filter(setor__isnull=False)
    
    # Filtro por setor específico
    if setor_id:
        vagas = vagas.filter(setor__id=setor_id)
    
    # Filtro por status
    if status_filtro == 'ativas':
        vagas = vagas.filter(ativa=True)
    elif status_filtro == 'inativas':
        vagas = vagas.filter(ativa=False)
    
    # Ordenar: genéricas primeiro, depois por setor
    vagas = vagas.order_by('setor__nome', 'titulo')
    
    # Buscar setores do evento
    setores = SetorEvento.objects.filter(evento=evento).order_by('nome')
    
    # Estatísticas por setor
    stats_setores = []
    for setor in setores:
        vagas_setor = Vaga.objects.filter(setor=setor)
        candidaturas_setor = Candidatura.objects.filter(vaga__setor=setor)
        
        stats_setores.append({
            'setor': setor,
            'total_vagas': vagas_setor.aggregate(Sum('quantidade'))['quantidade__sum'] or 0,
            'vagas_ativas': vagas_setor.filter(ativa=True).aggregate(Sum('quantidade'))['quantidade__sum'] or 0,
            'total_candidaturas': candidaturas_setor.count(),
            'aprovadas': candidaturas_setor.filter(status='aprovado').count(),
        })
    
    # Estatísticas gerais
    total_vagas = Vaga.objects.filter(evento=evento)
    vagas_genericas = total_vagas.filter(setor__isnull=True)
    vagas_com_setor = total_vagas.filter(setor__isnull=False)
    
    stats_gerais = {
        'total_vagas': total_vagas.aggregate(Sum('quantidade'))['quantidade__sum'] or 0,
        'vagas_ativas': total_vagas.filter(ativa=True).aggregate(Sum('quantidade'))['quantidade__sum'] or 0,
        'vagas_inativas': total_vagas.filter(ativa=False).aggregate(Sum('quantidade'))['quantidade__sum'] or 0,
        'vagas_genericas': vagas_genericas.aggregate(Sum('quantidade'))['quantidade__sum'] or 0,
        'vagas_com_setor': vagas_com_setor.aggregate(Sum('quantidade'))['quantidade__sum'] or 0,
        'total_candidaturas': Candidatura.objects.filter(vaga__evento=evento).count(),
    }
    
    context = {
        'empresa': empresa,
        'evento': evento,
        'vagas': vagas,
        'setores': setores,
        'stats_setores': stats_setores,
        'stats_gerais': stats_gerais,
        'setor_filtro': setor_id,
        'status_filtro': status_filtro,
        'tipo_filtro': tipo_filtro,
        'user': request.user,
    }
    
    return render(request, 'dashboard_empresa/gerenciar_vagas.html', context)


@login_required(login_url='/empresa/login/')
def editar_vaga(request, vaga_id):
    """
    Editar vaga existente
    """
    if request.user.tipo_usuario not in ['admin_empresa', 'operador_empresa']:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard_empresa:login_empresa')
    
    empresa = request.user.empresa_contratante
    
    # Buscar vaga
    vaga = get_object_or_404(
        Vaga.objects.select_related('setor', 'setor__evento'),
        id=vaga_id,
        empresa_contratante=empresa
    )
    
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        descricao = request.POST.get('descricao', '')
        quantidade = request.POST.get('quantidade')
        remuneracao = request.POST.get('remuneracao')
        tipo_remuneracao = request.POST.get('tipo_remuneracao', 'por_dia')
        nivel_experiencia = request.POST.get('nivel_experiencia', 'iniciante')
        funcao_id = request.POST.get('funcao')
        ativa = request.POST.get('ativa') == 'on'
        
        if titulo and quantidade and remuneracao and funcao_id:
            try:
                funcao = Funcao.objects.get(id=funcao_id)
                
                vaga.titulo = titulo
                vaga.descricao = descricao
                vaga.quantidade = int(quantidade)
                vaga.remuneracao = float(remuneracao)
                vaga.tipo_remuneracao = tipo_remuneracao
                vaga.nivel_experiencia = nivel_experiencia
                vaga.funcao = funcao
                vaga.ativa = ativa
                vaga.save()
                
                messages.success(request, f'Vaga "{titulo}" atualizada com sucesso!')
                return redirect('dashboard_empresa:gerenciar_vagas_evento', evento_id=vaga.setor.evento.id)
            except Funcao.DoesNotExist:
                messages.error(request, 'Função selecionada não encontrada.')
        else:
            messages.error(request, 'Preencha todos os campos obrigatórios, incluindo a Função.')
    
    # Buscar funções disponíveis (globais ou da empresa)
    funcoes = Funcao.objects.filter(
        Q(empresa_contratante=empresa) | Q(empresa_contratante__isnull=True),
        ativo=True,
        disponivel_para_vagas=True
    ).select_related('tipo_funcao').order_by('tipo_funcao__nome', 'nome')
    
    context = {
        'empresa': empresa,
        'vaga': vaga,
        'setor': vaga.setor,
        'evento': vaga.setor.evento,
        'funcoes': funcoes,
        'user': request.user,
    }
    
    return render(request, 'dashboard_empresa/editar_vaga.html', context)


@login_required(login_url='/empresa/login/')
def desativar_vaga(request, vaga_id):
    """
    Desativar/Ativar vaga
    """
    if request.user.tipo_usuario not in ['admin_empresa', 'operador_empresa']:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard_empresa:login_empresa')
    
    empresa = request.user.empresa_contratante
    
    # Buscar vaga
    vaga = get_object_or_404(
        Vaga.objects.select_related('setor', 'setor__evento'),
        id=vaga_id,
        empresa_contratante=empresa
    )
    
    # Toggle status
    vaga.ativa = not vaga.ativa
    vaga.save()
    
    status_texto = "ativada" if vaga.ativa else "desativada"
    messages.success(request, f'Vaga "{vaga.titulo}" {status_texto} com sucesso!')
    
    # Redirecionar para a página anterior ou para gerenciar vagas
    return redirect(request.META.get('HTTP_REFERER', 'dashboard_empresa:gerenciar_vagas_evento'), evento_id=vaga.setor.evento.id)


@login_required(login_url='/empresa/login/')
def candidaturas_empresa(request):
    """
    Lista de candidaturas da empresa
    """
    if request.user.tipo_usuario not in ['admin_empresa', 'operador_empresa']:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard_empresa:login_empresa')
    
    empresa = request.user.empresa_contratante
    candidaturas = Candidatura.objects.filter(
        vaga__empresa_contratante=empresa
    ).select_related('freelance', 'vaga', 'vaga__setor', 'vaga__setor__evento').order_by('-data_candidatura')
    
    context = {
        'empresa': empresa,
        'candidaturas': candidaturas,
        'user': request.user,
    }
    
    return render(request, 'dashboard_empresa/candidaturas.html', context)


@login_required(login_url='/empresa/login/')
def detalhe_candidatura(request, candidatura_id):
    """
    Detalhes da candidatura e freelancers aprovados para o evento
    """
    if request.user.tipo_usuario not in ['admin_empresa', 'operador_empresa']:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard_empresa:login_empresa')
    
    empresa = request.user.empresa_contratante
    
    # Buscar candidatura
    candidatura = get_object_or_404(
        Candidatura.objects.select_related('freelance', 'vaga', 'vaga__setor', 'vaga__setor__evento'),
        id=candidatura_id,
        vaga__empresa_contratante=empresa
    )
    
    evento = candidatura.vaga.setor.evento
    
    # Buscar todos os freelancers aprovados para este evento
    candidaturas_aprovadas = Candidatura.objects.filter(
        vaga__setor__evento=evento,
        status='aprovado'
    ).select_related('freelance', 'vaga', 'vaga__setor').order_by('vaga__setor__nome', 'vaga__titulo')
    
    # Buscar todas as candidaturas deste evento
    todas_candidaturas = Candidatura.objects.filter(
        vaga__setor__evento=evento
    ).select_related('freelance', 'vaga', 'vaga__setor')
    
    # Estatísticas do evento
    stats_evento = {
        'total_candidaturas': todas_candidaturas.count(),
        'aprovadas': todas_candidaturas.filter(status='aprovado').count(),
        'pendentes': todas_candidaturas.filter(status='pendente').count(),
        'rejeitadas': todas_candidaturas.filter(status='rejeitado').count(),
        'total_vagas': Vaga.objects.filter(setor__evento=evento).count(),
    }
    
    context = {
        'empresa': empresa,
        'candidatura': candidatura,
        'evento': evento,
        'candidaturas_aprovadas': candidaturas_aprovadas,
        'stats_evento': stats_evento,
        'user': request.user,
    }
    
    return render(request, 'dashboard_empresa/detalhe_candidatura.html', context)


@login_required(login_url='/empresa/login/')
def aprovar_candidatura(request, candidatura_id):
    """
    Aprovar candidatura
    """
    if request.user.tipo_usuario not in ['admin_empresa', 'operador_empresa']:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard_empresa:login_empresa')
    
    empresa = request.user.empresa_contratante
    
    # Buscar candidatura
    candidatura = get_object_or_404(
        Candidatura,
        id=candidatura_id,
        vaga__empresa_contratante=empresa
    )
    
    # Aprovar candidatura
    candidatura.status = 'aprovado'
    candidatura.data_resposta = timezone.now()
    candidatura.save()
    
    messages.success(request, f'Candidatura de {candidatura.freelance.nome_completo} aprovada com sucesso!')
    
    # Redirecionar de volta para a página de candidaturas
    return redirect('dashboard_empresa:candidaturas_empresa')


@login_required(login_url='/empresa/login/')
def rejeitar_candidatura(request, candidatura_id):
    """
    Rejeitar candidatura
    """
    if request.user.tipo_usuario not in ['admin_empresa', 'operador_empresa']:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard_empresa:login_empresa')
    
    empresa = request.user.empresa_contratante
    
    # Buscar candidatura
    candidatura = get_object_or_404(
        Candidatura,
        id=candidatura_id,
        vaga__empresa_contratante=empresa
    )
    
    # Rejeitar candidatura
    candidatura.status = 'rejeitado'
    candidatura.data_resposta = timezone.now()
    candidatura.save()
    
    messages.warning(request, f'Candidatura de {candidatura.freelance.nome_completo} rejeitada.')
    
    # Redirecionar de volta para a página de candidaturas
    return redirect('dashboard_empresa:candidaturas_empresa')


@login_required(login_url='/empresa/login/')
def freelancers_empresa(request):
    """
    Lista de freelancers da empresa
    """
    if request.user.tipo_usuario not in ['admin_empresa', 'operador_empresa']:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard_empresa:login_empresa')
    
    empresa = request.user.empresa_contratante
    
    # Buscar parâmetro de filtro
    filtro = request.GET.get('filtro', 'todos')  # 'todos' ou 'candidatos'
    
    if filtro == 'candidatos':
        # Apenas freelancers que se candidataram a vagas da empresa
        freelancers = Freelance.objects.filter(
            candidaturas__vaga__empresa_contratante=empresa
        ).select_related('usuario').prefetch_related(
            'funcoes__funcao'
        ).distinct().order_by('nome_completo')
    else:
        # TODOS os freelancers do sistema
        freelancers = Freelance.objects.select_related(
            'usuario'
        ).prefetch_related(
            'funcoes__funcao'
        ).all().order_by('nome_completo')
    
    # Buscar funções disponíveis para o filtro
    funcoes_disponiveis = Funcao.objects.filter(
        Q(empresa_contratante=empresa) | Q(empresa_contratante__isnull=True),
        ativo=True
    ).select_related('tipo_funcao').order_by('tipo_funcao__nome', 'nome')
    
    context = {
        'empresa': empresa,
        'freelancers': freelancers,
        'funcoes_disponiveis': funcoes_disponiveis,
        'user': request.user,
        'filtro': filtro,
        'total_freelancers': freelancers.count(),
    }
    
    return render(request, 'dashboard_empresa/freelancers.html', context)


@login_required(login_url='/empresa/login/')
def detalhe_freelancer(request, freelancer_id):
    """
    Detalhes completos do freelancer
    """
    if request.user.tipo_usuario not in ['admin_empresa', 'operador_empresa']:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard_empresa:login_empresa')
    
    empresa = request.user.empresa_contratante
    
    # Buscar freelancer
    freelancer = get_object_or_404(
        Freelance.objects.select_related('usuario').prefetch_related('funcoes__funcao__tipo_funcao'),
        id=freelancer_id
    )
    
    # Buscar candidaturas deste freelancer para vagas da empresa
    candidaturas = Candidatura.objects.filter(
        freelance=freelancer,
        vaga__empresa_contratante=empresa
    ).select_related('vaga', 'vaga__setor', 'vaga__setor__evento').order_by('-data_candidatura')
    
    # Buscar contratos ativos
    contratos = ContratoFreelance.objects.filter(
        freelance=freelancer,
        vaga__empresa_contratante=empresa
    ).select_related('vaga', 'vaga__setor', 'vaga__setor__evento').order_by('-data_contratacao')
    
    # Estatísticas do freelancer com a empresa
    stats = {
        'total_candidaturas': candidaturas.count(),
        'aprovadas': candidaturas.filter(status='aprovado').count(),
        'pendentes': candidaturas.filter(status='pendente').count(),
        'rejeitadas': candidaturas.filter(status='rejeitado').count(),
        'contratos_ativos': contratos.filter(status='ativo').count(),
        'contratos_finalizados': contratos.filter(status='finalizado').count(),
    }
    
    context = {
        'empresa': empresa,
        'freelancer': freelancer,
        'candidaturas': candidaturas,
        'contratos': contratos,
        'stats': stats,
        'user': request.user,
    }
    
    return render(request, 'dashboard_empresa/detalhe_freelancer.html', context)


# Views de notificação (importadas)
notificar_freelancers_evento = NotificarFreelancersEventoView.as_view()
notificar_freelancers_vaga_especifica = notificar_freelancers_vaga_especifica


@login_required(login_url='/empresa/login/')
def usuarios_empresa(request):
    """
    Lista de usuários da empresa (apenas para admin)
    """
    if request.user.tipo_usuario != 'admin_empresa':
        messages.error(request, 'Apenas administradores podem gerenciar usuários.')
        return redirect('dashboard_empresa:dashboard_empresa')
    
    empresa = request.user.empresa_contratante
    usuarios = User.objects.filter(empresa_contratante=empresa).order_by('username')
    
    context = {
        'empresa': empresa,
        'usuarios': usuarios,
        'user': request.user,
    }
    
    return render(request, 'dashboard_empresa/usuarios.html', context)


@login_required(login_url='/empresa/login/')
def equipamentos_empresa(request):
    """
    Lista de equipamentos da empresa
    """
    if request.user.tipo_usuario not in ['admin_empresa', 'operador_empresa']:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard_empresa:login_empresa')
    
    empresa = request.user.empresa_contratante
    equipamentos = Equipamento.objects.filter(empresa_contratante=empresa).order_by('codigo_patrimonial')
    
    context = {
        'empresa': empresa,
        'equipamentos': equipamentos,
        'user': request.user,
    }
    
    return render(request, 'dashboard_empresa/equipamentos.html', context)


@login_required(login_url='/empresa/login/')
def financeiro_empresa(request):
    """
    Dashboard financeiro da empresa
    """
    if request.user.tipo_usuario not in ['admin_empresa', 'operador_empresa']:
        messages.error(request, 'Acesso negado.')
        return redirect('home')
    
    empresa = request.user.empresa_contratante
    
    # Receitas e despesas por mês (últimos 6 meses)
    hoje = timezone.now()
    meses = []
    
    for i in range(6):
        data = hoje - timedelta(days=30*i)
        inicio_mes = data.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        fim_mes = (inicio_mes + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        receitas = ReceitaEvento.objects.filter(
            evento__empresa_contratante=empresa,
            data_vencimento__range=[inicio_mes, fim_mes]
        ).aggregate(total=Sum('valor'))['total'] or 0
        
        despesas = DespesaEvento.objects.filter(
            evento__empresa_contratante=empresa,
            data_vencimento__range=[inicio_mes, fim_mes]
        ).aggregate(total=Sum('valor'))['total'] or 0
        
        meses.append({
            'mes': inicio_mes.strftime('%m/%Y'),
            'receitas': receitas,
            'despesas': despesas,
            'saldo': receitas - despesas
        })
    
    context = {
        'empresa': empresa,
        'meses': reversed(meses),  # Mostrar do mais antigo para o mais recente
        'user': request.user,
    }
    
    return render(request, 'dashboard_empresa/financeiro.html', context)
