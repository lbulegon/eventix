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
            '/empresa/',  # Dashboard empresa - views tratam auth com @login_required
            '/empresa/login/',
            '/empresa/logout/',
            '/freelancer/',  # Dashboard, login e rotas do freelancer (views tratam auth)
            '/app/freelancer/',  # Compatibilidade com deploy em prefixo /app
            '/freelancer-publico/login/',  # Login do freelancer (legado)
            '/freelancer-publico/logout/',  # Logout do freelancer (legado)
            '/freelancer-publico/evento/',  # Eventos públicos (sem login)
            '/freelancer-publico/vaga/',  # Vagas públicas (sem login)
            '/eventos/',  # Lista pública de eventos
            '/service-worker.js',  # Service Worker (PWA)
            '/manifest.json',  # Manifest (PWA)
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

            # Gestor de grupo não tem empresa fixa no utilizador; o dashboard web usa sessão.
            if getattr(request.user, 'is_gestor_grupo', False):
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
    Middleware para adicionar contexto completo da empresa contratante
    """
    
    def process_request(self, request):
        try:
            if not request.user.is_authenticated:
                return None
            from .utils_empresa_ativa import empresa_ativa

            empresa = empresa_ativa(request)
            if empresa:
                # Adiciona dados da empresa ao request
                request.empresa_contratante = empresa
                request.empresa_contratante_id = empresa.id
                request.empresa_contratante_nome = empresa.nome_fantasia
                request.empresa_contratante_cnpj = empresa.cnpj
                request.empresa_contratante_plano = empresa.plano_contratado
                request.empresa_contratante_ativa = empresa.ativo

                # Carrega dados do plano contratado
                if hasattr(empresa, 'plano_contratado') and empresa.plano_contratado:
                    plano = empresa.plano_contratado
                    request.empresa_plano_nome = plano.nome
                    request.empresa_plano_tipo = plano.tipo_plano
                    request.empresa_plano_limites = {
                        'max_eventos_mes': plano.max_eventos_mes,
                        'max_usuarios': plano.max_usuarios,
                        'max_freelancers': plano.max_freelancers,
                        'max_equipamentos': plano.max_equipamentos,
                        'max_locais': plano.max_locais,
                    }
                    request.empresa_plano_recursos = {
                        'suporte_24h': plano.suporte_24h,
                        'relatorios_avancados': plano.relatorios_avancados,
                        'integracao_api': plano.integracao_api,
                        'backup_automatico': plano.backup_automatico,
                        'ssl_certificado': plano.ssl_certificado,
                        'dominio_personalizado': plano.dominio_personalizado,
                    }

                # Carrega empresas parceiras da empresa contratante
                from .models import Empresa
                empresas_parceiras = Empresa.objects.filter(ativo=True)
                request.empresas_parceiras = empresas_parceiras

                # Carrega dados do usuário
                request.usuario_tipo = request.user.tipo_usuario
                request.usuario_ativo = request.user.ativo
                request.usuario_ultimo_acesso = request.user.data_ultimo_acesso

                # Atualiza último acesso
                from django.utils import timezone
                request.user.data_ultimo_acesso = timezone.now()
                request.user.save(update_fields=['data_ultimo_acesso'])
                    
        except Exception:
            # Em caso de erro, não bloqueia o acesso
            request.empresa_contratante = None
