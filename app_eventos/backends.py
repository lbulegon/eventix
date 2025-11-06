"""
Backend de autenticação customizado que aceita email ou username
"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class EmailOrUsernameBackend(ModelBackend):
    """
    Backend de autenticação que permite login com email ou username
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Tenta autenticar usando email ou username
        """
        if username is None:
            username = kwargs.get('email')
        
        if username is None or password is None:
            return None
        
        try:
            # Tenta encontrar o usuário por username ou email
            user = User.objects.get(
                Q(username=username) | Q(email=username)
            )
        except User.DoesNotExist:
            # Retorna None se não encontrar o usuário
            return None
        except User.MultipleObjectsReturned:
            # Se houver múltiplos usuários, pega o primeiro
            user = User.objects.filter(
                Q(username=username) | Q(email=username)
            ).first()
        
        # Verifica a senha usando o método do ModelBackend
        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None

