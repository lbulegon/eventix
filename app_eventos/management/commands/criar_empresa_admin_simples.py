#!/usr/bin/env python                           #
"""
Comando simples para criar usuário admin do sistema
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Cria usuário admin do sistema - versão simples'

    def handle(self, *args, **options):
        username = 'admin_sistema'
        email = 'admin@sistema.com'
        password = 'admin123'
        
        try:
            # Verificar se já existe
            if User.objects.filter(username=username).exists():
                self.stdout.write('Usuario admin_sistema ja existe!')
                return
            
            # Criar usuário admin do sistema
            admin_sistema = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                tipo_usuario='admin_sistema',
                is_staff=True,
                is_superuser=True,
                ativo=True,
                first_name='Administrador',
                last_name='do Sistema'
            )
            
            self.stdout.write('Usuario admin do sistema criado com sucesso!')
            self.stdout.write(f'Username: {username}')
            self.stdout.write(f'Email: {email}')
            self.stdout.write(f'Senha: {password}')
            self.stdout.write(f'Tipo: {admin_sistema.get_tipo_usuario_display()}')
            
        except Exception as e:
            self.stdout.write(f'Erro ao criar usuario: {str(e)}')
