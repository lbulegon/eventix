from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.db import DatabaseError


class EmpresaContratanteMiddleware(MiddlewareMixin):
    """
    Middleware para controlar acesso baseado na empresa contratante
    """
    
    def process_request(self, request):
        # URLs que não precisam de verificação de empresa
        urls_publicas = [
            '/',  # Página inicial
            '/eventos/',  # Lista de eventos
            '/admin/login/',
            '/admin/logout/',
            '/accounts/login/',
            '/accounts/logout/',
            '/api/token/',
            '/api/token/refresh/',
            '/api/auth/',
            '/api/v1/',  # API Mobile
            '/api/desktop/',  # API Desktop
            '/static/',
            '/media/',
            '/favicon.ico',
        ]
        
        # Se a URL é pública, não faz verificação
        if any(request.path.startswith(url) for url in urls_publicas):
            return None
            
        try:
            # Se o usuário não está autenticado, redireciona para login
            if not request.user.is_authenticated:
                return redirect('admin:login')
                
            # Se é admin do sistema, tem acesso total
            if request.user.tipo_usuario == 'admin_sistema':
                return None
                
            # Se é freelancer, só pode acessar seu próprio perfil
            if request.user.tipo_usuario == 'freelancer':
                if not self._pode_acessar_freelancer(request):
                    messages.error(request, 'Você só pode acessar seu próprio perfil.')
                    return redirect('admin:index')
                return None
                
            # Para usuários da empresa, verifica se têm empresa contratante
            if not request.user.empresa_contratante:
                messages.error(request, 'Usuário não está associado a nenhuma empresa.')
                return redirect('admin:index')
                
            # Verifica se a empresa está ativa
            if not request.user.empresa_contratante.ativo:
                messages.error(request, 'Sua empresa está inativa. Entre em contato com o suporte.')
                return redirect('admin:index')
                
            # Verifica se o usuário está ativo
            if not request.user.ativo:
                messages.error(request, 'Seu usuário está inativo. Entre em contato com o administrador.')
                return redirect('admin:index')
                
        except DatabaseError:
            # Se há erro de banco, permite o acesso (pode ser problema temporário)
            return None
        except Exception as e:
            # Se há qualquer outro erro, permite o acesso
            return None
            
        return None
    
    def _pode_acessar_freelancer(self, request):
        """
        Verifica se o freelancer pode acessar a URL solicitada
        """
        try:
            # URLs que freelancers podem acessar
            urls_permitidas = [
                '/admin/',
                '/admin/jsi18n/',
                '/admin/autocomplete/',
            ]
            
            # Se é uma URL permitida, verifica se está acessando seu próprio perfil
            if any(request.path.startswith(url) for url in urls_permitidas):
                # Se está tentando acessar perfil de outro freelancer, bloqueia
                if '/freelance/' in request.path:
                    try:
                        from app_eventos.models import Freelance
                        freelance_id = request.path.split('/')[-2]
                        if freelance_id.isdigit():
                            freelance = Freelance.objects.get(id=freelance_id)
                            if freelance.usuario != request.user:
                                return False
                    except:
                        return False
                return True
                
            return False
        except Exception:
            return False


class EmpresaContextMiddleware(MiddlewareMixin):
    """
    Middleware para adicionar contexto da empresa contratante
    """
    
    def process_request(self, request):
        try:
            if request.user.is_authenticated and hasattr(request.user, 'empresa_contratante'):
                request.empresa_contratante = request.user.empresa_contratante
            else:
                request.empresa_contratante = None
        except Exception:
            request.empresa_contratante = None
