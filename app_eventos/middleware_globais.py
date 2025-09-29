"""
Middleware para controle de acesso aos modelos globais
"""
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin


class ModelosGlobaisMiddleware(MiddlewareMixin):
    """
    Middleware que controla o acesso aos modelos globais
    """
    
    def process_request(self, request):
        # URLs que não precisam de verificação
        urls_publicas = [
            '/accounts/login/',
            '/accounts/logout/',
            '/api/token/',
            '/api/token/refresh/',
            '/api/auth/',
            '/api/v1/',
            '/api/desktop/',
            '/static/',
            '/media/',
            '/favicon.ico',
        ]
        
        # Se a URL é pública, não faz verificação
        if any(request.path.startswith(url) for url in urls_publicas):
            return None
        
        # Verifica se está acessando admin de modelos globais
        if '/admin/app_eventos/' in request.path:
            # Lista de modelos globais que só admin do sistema pode gerenciar
            modelos_globais_admin = [
                'categoriaglobal',
                'tipoglobal', 
                'classificacaoglobal',
                'configuracaosistema',
                'parametrosistema',
                'integracaoglobal',
                'webhookglobal',
                'templateglobal',
                'logsistema',
                'backupglobal',
                'categoriafreelancerglobal',
                'habilidadeglobal',
                'fornecedorglobal'
            ]
            
            # Verifica se está tentando acessar um modelo global
            for modelo in modelos_globais_admin:
                if f'/{modelo}/' in request.path:
                    # Verifica se é admin do sistema
                    if not request.user.is_authenticated:
                        return redirect('admin:login')
                    
                    if not request.user.is_admin_sistema:
                        messages.error(
                            request, 
                            'Apenas administradores do sistema podem gerenciar este conteúdo.'
                        )
                        return redirect('admin:index')
                    break
        
        return None
