"""
Empresa efetiva no dashboard: utilizadores de empresa (FK) ou gestor de grupo (sessão).
"""
from django.contrib import messages
from django.shortcuts import redirect

from .models import EmpresaContratante

SESSION_EMPRESA_GESTOR_KEY = 'empresa_contexto_gestor_id'


def limpar_contexto_gestor_sessao(request):
    request.session.pop(SESSION_EMPRESA_GESTOR_KEY, None)


def empresa_ativa(request):
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        return None
    if getattr(user, 'is_gestor_grupo', False):
        eid = request.session.get(SESSION_EMPRESA_GESTOR_KEY)
        if not eid:
            return None
        try:
            return EmpresaContratante.objects.get(
                pk=int(eid),
                grupo_empresarial_id=user.grupo_empresarial_id,
                ativo=True,
            )
        except (EmpresaContratante.DoesNotExist, ValueError, TypeError):
            limpar_contexto_gestor_sessao(request)
            request.session.modified = True
            return None
    ec = getattr(user, 'empresa_contratante', None)
    if ec and getattr(ec, 'ativo', True):
        return ec
    return None


def require_empresa_dashboard(request, denied_redirect='dashboard_empresa:login_empresa'):
    """
    Retorna (empresa, None) se o utilizador pode agir no dashboard com empresa resolvida;
    (None, HttpResponseRedirect) caso contrário.
    """
    user = request.user
    if not user.is_authenticated:
        return None, redirect('dashboard_empresa:login_empresa')

    if user.tipo_usuario == 'admin_sistema':
        messages.error(request, 'Acesso negado.')
        return None, redirect(denied_redirect)

    if user.tipo_usuario in ('admin_empresa', 'operador_empresa'):
        emp = user.empresa_contratante
        if not emp or not getattr(emp, 'ativo', True):
            messages.error(request, 'Usuário não está associado a nenhuma empresa ativa.')
            return None, redirect(denied_redirect)
        if not user.ativo:
            messages.error(request, 'Seu usuário está inativo.')
            return None, redirect(denied_redirect)
        return emp, None

    if getattr(user, 'is_gestor_grupo', False):
        if not user.grupo_empresarial_id:
            messages.error(request, 'Conta de gestor de grupo sem grupo associado.')
            return None, redirect(denied_redirect)
        emp = empresa_ativa(request)
        if not emp:
            messages.info(request, 'Selecione uma empresa do grupo para gerir.')
            return None, redirect('dashboard_empresa:dashboard_grupo')
        if not user.ativo:
            messages.error(request, 'Seu usuário está inativo.')
            return None, redirect(denied_redirect)
        return emp, None

    messages.error(request, 'Acesso negado.')
    return None, redirect(denied_redirect)


def _raw_empresa_context_id_api(request):
    """Valor bruto do contexto de empresa na API (cabeçalho ou query)."""
    raw = request.META.get('HTTP_X_EMPRESA_CONTEXT_ID')
    if raw is None:
        qp = getattr(request, 'query_params', None)
        if qp is not None:
            raw = qp.get('empresa_context')
    if raw is None:
        raw = request.GET.get('empresa_context')
    return raw


def empresa_contexto_api(request):
    """
    Tenant para a API: admin/operador pela FK; gestor_grupo por ``X-Empresa-Context-Id``
    (ou query ``empresa_context`` em pedidos GET).
    """
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        return None
    if user.tipo_usuario in ('admin_empresa', 'operador_empresa'):
        ec = getattr(user, 'empresa_contratante', None)
        if ec and getattr(ec, 'ativo', True):
            return ec
        return None
    if getattr(user, 'is_gestor_grupo', False):
        if not user.grupo_empresarial_id:
            return None
        raw = _raw_empresa_context_id_api(request)
        if raw is None or str(raw).strip() == '':
            return None
        try:
            return EmpresaContratante.objects.get(
                pk=int(str(raw).strip()),
                grupo_empresarial_id=user.grupo_empresarial_id,
                ativo=True,
            )
        except (ValueError, TypeError, EmpresaContratante.DoesNotExist):
            return None
    return None


def empresa_owner_api(request):
    """
    Equivalente a ``User.empresa_owner`` para escopo na API (inclui gestor + cabeçalho).
    """
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        return None
    if getattr(user, 'is_freelancer', False):
        return user.empresa_owner
    return empresa_contexto_api(request)


def is_api_empresa_actor(request):
    """Quem age em nome de uma empresa na API (não inclui admin_sistema)."""
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        return False
    if getattr(user, 'is_admin_sistema', False):
        return False
    if empresa_contexto_api(request) is None:
        return False
    return bool(
        getattr(user, 'is_empresa_user', False) or getattr(user, 'is_gestor_grupo', False)
    )
