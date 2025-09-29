"""
Views para modelos globais do sistema
Permite visualização para usuários de empresa, mas apenas admin do sistema pode gerenciar
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.db.models import Q
from .models_globais import (
    CategoriaGlobal, TipoGlobal, ClassificacaoGlobal,
    ConfiguracaoSistema, ParametroSistema,
    IntegracaoGlobal, WebhookGlobal,
    TemplateGlobal,
    CategoriaFreelancerGlobal, HabilidadeGlobal, FornecedorGlobal
)
from .permissions.permissions_globais import (
    PodeVerModelosGlobaisMixin,
    PodeVerConfiguracoesMixin,
    PodeVerMarketplaceMixin
)


# ============================================================================
# CATÁLOGOS GERAIS
# ============================================================================

class CategoriaGlobalListView(PodeVerModelosGlobaisMixin, ListView):
    """
    Lista categorias globais disponíveis
    """
    model = CategoriaGlobal
    template_name = 'app_eventos/categorias_globais_list.html'
    context_object_name = 'categorias'
    paginate_by = 20
    
    def get_queryset(self):
        return CategoriaGlobal.objects.filter(ativo=True).order_by('ordem', 'nome')


class CategoriaGlobalDetailView(PodeVerModelosGlobaisMixin, DetailView):
    """
    Detalhes de uma categoria global
    """
    model = CategoriaGlobal
    template_name = 'app_eventos/categoria_global_detail.html'
    context_object_name = 'categoria'


class TipoGlobalListView(PodeVerModelosGlobaisMixin, ListView):
    """
    Lista tipos globais disponíveis
    """
    model = TipoGlobal
    template_name = 'app_eventos/tipos_globais_list.html'
    context_object_name = 'tipos'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = TipoGlobal.objects.filter(ativo=True).select_related('categoria')
        
        # Filtro por categoria se especificado
        categoria_id = self.request.GET.get('categoria')
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
        
        return queryset.order_by('categoria', 'ordem', 'nome')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = CategoriaGlobal.objects.filter(ativo=True).order_by('ordem', 'nome')
        return context


class ClassificacaoGlobalListView(PodeVerModelosGlobaisMixin, ListView):
    """
    Lista classificações globais disponíveis
    """
    model = ClassificacaoGlobal
    template_name = 'app_eventos/classificacoes_globais_list.html'
    context_object_name = 'classificacoes'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = ClassificacaoGlobal.objects.filter(ativo=True)
        
        # Filtro por tipo se especificado
        tipo = self.request.GET.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        return queryset.order_by('tipo', 'valor', 'nome')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipos'] = ClassificacaoGlobal.objects.filter(ativo=True).values_list('tipo', flat=True).distinct()
        return context


# ============================================================================
# CONFIGURAÇÕES SISTEMA
# ============================================================================

class ConfiguracaoSistemaListView(PodeVerConfiguracoesMixin, ListView):
    """
    Lista configurações do sistema (apenas visualização)
    """
    model = ConfiguracaoSistema
    template_name = 'app_eventos/configuracoes_sistema_list.html'
    context_object_name = 'configuracoes'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = ConfiguracaoSistema.objects.filter(ativo=True)
        
        # Filtro por categoria se especificado
        categoria = self.request.GET.get('categoria')
        if categoria:
            queryset = queryset.filter(categoria=categoria)
        
        return queryset.order_by('categoria', 'chave')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = ConfiguracaoSistema.objects.filter(ativo=True).values_list('categoria', flat=True).distinct()
        return context


class ParametroSistemaListView(PodeVerConfiguracoesMixin, ListView):
    """
    Lista parâmetros do sistema (apenas visualização)
    """
    model = ParametroSistema
    template_name = 'app_eventos/parametros_sistema_list.html'
    context_object_name = 'parametros'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = ParametroSistema.objects.filter(ativo=True)
        
        # Filtro por categoria se especificado
        categoria = self.request.GET.get('categoria')
        if categoria:
            queryset = queryset.filter(categoria=categoria)
        
        return queryset.order_by('categoria', 'nome')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = ParametroSistema.objects.filter(ativo=True).values_list('categoria', flat=True).distinct()
        return context


# ============================================================================
# INTEGRAÇÕES
# ============================================================================

class IntegracaoGlobalListView(PodeVerModelosGlobaisMixin, ListView):
    """
    Lista integrações globais disponíveis
    """
    model = IntegracaoGlobal
    template_name = 'app_eventos/integracoes_globais_list.html'
    context_object_name = 'integracoes'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = IntegracaoGlobal.objects.filter(ativo=True)
        
        # Filtro por tipo se especificado
        tipo = self.request.GET.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        return queryset.order_by('nome')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipos'] = IntegracaoGlobal.objects.filter(ativo=True).values_list('tipo', flat=True).distinct()
        return context


class IntegracaoGlobalDetailView(PodeVerModelosGlobaisMixin, DetailView):
    """
    Detalhes de uma integração global
    """
    model = IntegracaoGlobal
    template_name = 'app_eventos/integracao_global_detail.html'
    context_object_name = 'integracao'


# ============================================================================
# TEMPLATES
# ============================================================================

class TemplateGlobalListView(PodeVerModelosGlobaisMixin, ListView):
    """
    Lista templates globais disponíveis
    """
    model = TemplateGlobal
    template_name = 'app_eventos/templates_globais_list.html'
    context_object_name = 'templates'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = TemplateGlobal.objects.filter(ativo=True)
        
        # Filtro por tipo se especificado
        tipo = self.request.GET.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        return queryset.order_by('tipo', 'nome')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipos'] = TemplateGlobal.TIPO_TEMPLATE_CHOICES
        return context


class TemplateGlobalDetailView(PodeVerModelosGlobaisMixin, DetailView):
    """
    Detalhes de um template global
    """
    model = TemplateGlobal
    template_name = 'app_eventos/template_global_detail.html'
    context_object_name = 'template'


# ============================================================================
# MARKETPLACE
# ============================================================================

class CategoriaFreelancerGlobalListView(PodeVerMarketplaceMixin, ListView):
    """
    Lista categorias globais de freelancers
    """
    model = CategoriaFreelancerGlobal
    template_name = 'app_eventos/categorias_freelancer_globais_list.html'
    context_object_name = 'categorias'
    paginate_by = 20
    
    def get_queryset(self):
        return CategoriaFreelancerGlobal.objects.filter(ativo=True).order_by('nome')


class HabilidadeGlobalListView(PodeVerMarketplaceMixin, ListView):
    """
    Lista habilidades globais disponíveis
    """
    model = HabilidadeGlobal
    template_name = 'app_eventos/habilidades_globais_list.html'
    context_object_name = 'habilidades'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = HabilidadeGlobal.objects.filter(ativo=True).select_related('categoria')
        
        # Filtro por categoria se especificado
        categoria_id = self.request.GET.get('categoria')
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
        
        return queryset.order_by('categoria', 'nome')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = CategoriaFreelancerGlobal.objects.filter(ativo=True).order_by('nome')
        return context


class FornecedorGlobalListView(PodeVerMarketplaceMixin, ListView):
    """
    Lista fornecedores globais do marketplace
    """
    model = FornecedorGlobal
    template_name = 'app_eventos/fornecedores_globais_list.html'
    context_object_name = 'fornecedores'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = FornecedorGlobal.objects.filter(ativo=True)
        
        # Filtro por categoria se especificado
        categoria = self.request.GET.get('categoria')
        if categoria:
            queryset = queryset.filter(categoria=categoria)
        
        # Filtro por avaliação mínima se especificado
        avaliacao_min = self.request.GET.get('avaliacao_min')
        if avaliacao_min:
            try:
                avaliacao_min = float(avaliacao_min)
                queryset = queryset.filter(avaliacao_media__gte=avaliacao_min)
            except ValueError:
                pass
        
        return queryset.order_by('-avaliacao_media', 'nome')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = FornecedorGlobal.objects.filter(ativo=True).values_list('categoria', flat=True).distinct()
        return context


class FornecedorGlobalDetailView(PodeVerMarketplaceMixin, DetailView):
    """
    Detalhes de um fornecedor global
    """
    model = FornecedorGlobal
    template_name = 'app_eventos/fornecedor_global_detail.html'
    context_object_name = 'fornecedor'


# ============================================================================
# DASHBOARD GLOBAL
# ============================================================================

def dashboard_global(request):
    """
    Dashboard com informações dos modelos globais
    """
    if not request.user.is_authenticated:
        return redirect('admin:login')
    
    # Verifica permissões básicas
    if not (request.user.is_admin_sistema or 
            (request.user.is_empresa_user and request.user.empresa_contratante)):
        messages.error(request, 'Você não tem permissão para acessar este dashboard.')
        return redirect('admin:index')
    
    context = {
        'categorias_count': CategoriaGlobal.objects.filter(ativo=True).count(),
        'tipos_count': TipoGlobal.objects.filter(ativo=True).count(),
        'integracoes_count': IntegracaoGlobal.objects.filter(ativo=True).count(),
        'templates_count': TemplateGlobal.objects.filter(ativo=True).count(),
        'fornecedores_count': FornecedorGlobal.objects.filter(ativo=True).count(),
        'habilidades_count': HabilidadeGlobal.objects.filter(ativo=True).count(),
        'is_admin_sistema': request.user.is_admin_sistema,
    }
    
    return render(request, 'app_eventos/dashboard_global.html', context)
