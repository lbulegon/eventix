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
        # URLs que devem ser redirecionadas para o dashboard personalizado
        admin_urls = [
            '/admin/',
            '/admin/app_eventos/',
        ]
        
        # Verificar se é uma requisição para o admin do Django
        if any(request.path.startswith(url) for url in admin_urls):
            # Verificar se o usuário está logado e é de empresa
            if (request.user.is_authenticated and 
                request.user.tipo_usuario in ['admin_empresa', 'operador_empresa']):
                
                # Redirecionar para o dashboard personalizado
                return redirect('dashboard_empresa:dashboard_empresa')
        
        return None
