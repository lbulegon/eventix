"""
Middleware para redirecionar usuários de empresa para dashboard personalizado
"""
from django.shortcuts import redirect
from django.urls import reverse


class DashboardRedirectMiddleware:
    """
    Middleware para redirecionar usuários de empresa para o dashboard personalizado
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # URLs que NÃO devem sofrer qualquer tipo de redirecionamento
        excecoes = [
            '/admin/login/',
            '/admin/logout/',
            '/empresa/login/',
            '/empresa/logout/',
            '/empresa/test/',
            '/api/',
            '/static/',
            '/media/',
        ]
        
        # Não redirecionar se for uma URL de exceção
        if any(request.path.startswith(url) for url in excecoes):
            return None
        
        # URLs do dashboard empresa - não redirecionar, apenas verificar
        if request.path.startswith('/empresa/'):
            # Deixar as views do dashboard tratarem a autenticação
            return None
        
        # URLs do admin que devem ser redirecionadas para o dashboard personalizado
        admin_urls = [
            '/admin/',
        ]
        
        # Verificar se é uma requisição para o admin do Django
        if any(request.path.startswith(url) for url in admin_urls):
            # Se não está autenticado, deixar seguir para a tela de login
            if not request.user.is_authenticated:
                return None
            
            # Admin do sistema pode acessar o admin normalmente
            if request.user.tipo_usuario == 'admin_sistema':
                return None
            
            # Usuários de empresa vão para o dashboard personalizado
            if request.user.tipo_usuario in ['admin_empresa', 'operador_empresa']:
                return redirect('dashboard_empresa:dashboard_empresa')
        
        return None
