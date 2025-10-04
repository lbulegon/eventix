#!/usr/bin/env python
"""
Comando para corrigir permissões de usuários administradores
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Corrige permissões de usuários administradores de empresa'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username específico para corrigir (opcional)'
        )
        parser.add_argument(
            '--todos',
            action='store_true',
            help='Corrigir todos os administradores de empresa'
        )

    def handle(self, *args, **options):
        username = options.get('username')
        todos = options.get('todos')

        try:
            if username:
                # Corrigir usuário específico
                try:
                    usuario = User.objects.get(username=username)
                    if usuario.tipo_usuario == 'admin_empresa':
                        usuario.is_superuser = True
                        usuario.is_staff = True
                        usuario.save()
                        self.stdout.write(
                            self.style.SUCCESS(f'Usuário {username} corrigido com sucesso!')
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'Usuário {username} não é administrador de empresa!')
                        )
                except User.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f'Usuário {username} não encontrado!')
                    )
            elif todos:
                # Corrigir todos os administradores
                administradores = User.objects.filter(tipo_usuario='admin_empresa')
                
                if not administradores.exists():
                    self.stdout.write(
                        self.style.WARNING('Nenhum administrador de empresa encontrado!')
                    )
                    return
                
                for usuario in administradores:
                    usuario.is_superuser = True
                    usuario.is_staff = True
                    usuario.save()
                    self.stdout.write(f'✓ {usuario.username} corrigido')
                
                self.stdout.write(
                    self.style.SUCCESS(f'{administradores.count()} administrador(es) corrigido(s)!')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('Use --username USERNAME ou --todos')
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro ao corrigir permissões: {str(e)}')
            )
