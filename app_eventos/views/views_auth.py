from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import AuthenticationForm
from django import forms

class CustomLoginForm(AuthenticationForm):
    """Formulário de login personalizado"""
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Usuário ou E-mail',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Senha'
        })
    )

class CustomLoginView(LoginView):
    """View de login personalizada"""
    template_name = 'auth/login.html'
    form_class = CustomLoginForm
    redirect_authenticated_user = True
    
    def get_success_url(self):
        """Redireciona para o dashboard apropriado após login"""
        user = self.request.user
        
        if user.is_admin_sistema:
            return reverse_lazy('dashboard_admin_sistema')
        elif user.is_empresa_user:
            return reverse_lazy('dashboard_empresa')
        elif user.is_freelancer:
            return reverse_lazy('dashboard_freelancer')
        else:
            return reverse_lazy('dashboard_redirect')
    
    def form_valid(self, form):
        """Mensagem de sucesso após login"""
        messages.success(self.request, f'Bem-vindo, {form.get_user().first_name or form.get_user().username}!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Mensagem de erro para login inválido"""
        messages.error(self.request, 'Usuário ou senha incorretos. Tente novamente.')
        return super().form_invalid(form)

class CustomLogoutView(LogoutView):
    """View de logout personalizada"""
    next_page = reverse_lazy('home')
    
    def dispatch(self, request, *args, **kwargs):
        """Mensagem de logout"""
        if request.user.is_authenticated:
            messages.info(request, 'Você foi desconectado com sucesso.')
        return super().dispatch(request, *args, **kwargs)

@login_required
def area_restrita(request):
    """
    Área restrita principal - redireciona para o dashboard apropriado
    """
    user = request.user
    
    # Verificar se o usuário tem perfil completo
    if not hasattr(user, 'is_empresa_user') and not hasattr(user, 'is_freelancer') and not hasattr(user, 'is_admin_sistema'):
        messages.warning(request, 'Seu perfil está incompleto. Entre em contato com o administrador.')
        return redirect('home')
    
    # Redirecionar baseado no tipo de usuário
    if user.is_admin_sistema:
        return redirect('dashboard_admin_sistema')
    elif user.is_empresa_user:
        return redirect('dashboard_empresa')
    elif user.is_freelancer:
        return redirect('dashboard_freelancer')
    else:
        messages.error(request, 'Tipo de usuário não reconhecido.')
        return redirect('home')

@login_required
def perfil_usuario(request):
    """
    Página de perfil do usuário logado
    """
    user = request.user
    context = {
        'user': user,
        'is_empresa': user.is_empresa_user if hasattr(user, 'is_empresa_user') else False,
        'is_freelancer': user.is_freelancer if hasattr(user, 'is_freelancer') else False,
        'is_admin': user.is_admin_sistema if hasattr(user, 'is_admin_sistema') else False,
    }
    
    # Adicionar informações específicas do tipo de usuário
    if user.is_empresa_user:
        try:
            context['empresa'] = user.empresa_owner
        except:
            pass
    elif user.is_freelancer:
        try:
            from app_eventos.models import Freelance
            context['freelance'] = Freelance.objects.get(usuario=user)
        except:
            pass
    
    return render(request, 'auth/perfil.html', context)

@login_required
def alterar_senha(request):
    """
    Página para alterar senha do usuário
    """
    if request.method == 'POST':
        from django.contrib.auth.forms import PasswordChangeForm
        form = PasswordChangeForm(request.user, request.POST)
        
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Sua senha foi alterada com sucesso!')
            return redirect('perfil_usuario')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        from django.contrib.auth.forms import PasswordChangeForm
        form = PasswordChangeForm(request.user)
    
    return render(request, 'auth/alterar_senha.html', {'form': form})

def acesso_negado(request):
    """
    Página de acesso negado
    """
    return render(request, 'auth/acesso_negado.html', status=403)
