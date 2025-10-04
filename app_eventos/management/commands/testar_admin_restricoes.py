#!/usr/bin/env python
"""
Comando para testar restrições do admin do Django
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.admin.sites import site
from app_eventos.models import EmpresaContratante, TipoFuncao, PlanoContratacao

User = get_user_model()


class Command(BaseCommand):
    help = 'Testa restrições do admin do Django'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            required=True,
            help='Username do usuário para testar'
        )

    def handle(self, *args, **options):
        username = options.get('username')

        try:
            user = User.objects.get(username=username)
            self.stdout.write(f'Testando restrições do admin para: {user.username}')
            self.stdout.write(f'Tipo: {user.get_tipo_usuario_display()}')
            self.stdout.write('=' * 60)
            
            # Simular request do admin
            from django.test import RequestFactory
            factory = RequestFactory()
            request = factory.get('/admin/')
            request.user = user
            
            # Testar permissões de visualização
            self._testar_permissoes_admin(request, user)

        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Usuário {username} não encontrado!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro: {str(e)}')
            )

    def _testar_permissoes_admin(self, request, user):
        """Testa permissões através do admin do Django"""
        
        # Testar EmpresaContratante (deve ser restrito)
        try:
            admin_class = site._registry[EmpresaContratante]
            has_view = admin_class.has_view_permission(request)
            has_add = admin_class.has_add_permission(request)
            has_change = admin_class.has_change_permission(request)
            has_delete = admin_class.has_delete_permission(request)
            
            self.stdout.write(f'\n🏢 EmpresaContratante:')
            self.stdout.write(f'  Ver: {"✅" if has_view else "❌"}')
            self.stdout.write(f'  Adicionar: {"✅" if has_add else "❌"}')
            self.stdout.write(f'  Editar: {"✅" if has_change else "❌"}')
            self.stdout.write(f'  Deletar: {"✅" if has_delete else "❌"}')
            
        except Exception as e:
            self.stdout.write(f'  ❌ Erro: {str(e)}')
        
        # Testar TipoFuncao (deve ser restrito)
        try:
            admin_class = site._registry[TipoFuncao]
            has_view = admin_class.has_view_permission(request)
            has_add = admin_class.has_add_permission(request)
            has_change = admin_class.has_change_permission(request)
            has_delete = admin_class.has_delete_permission(request)
            
            self.stdout.write(f'\n🔧 TipoFuncao:')
            self.stdout.write(f'  Ver: {"✅" if has_view else "❌"}')
            self.stdout.write(f'  Adicionar: {"✅" if has_add else "❌"}')
            self.stdout.write(f'  Editar: {"✅" if has_change else "❌"}')
            self.stdout.write(f'  Deletar: {"✅" if has_delete else "❌"}')
            
        except Exception as e:
            self.stdout.write(f'  ❌ Erro: {str(e)}')
        
        # Testar PlanoContratacao (deve ser restrito)
        try:
            admin_class = site._registry[PlanoContratacao]
            has_view = admin_class.has_view_permission(request)
            has_add = admin_class.has_add_permission(request)
            has_change = admin_class.has_change_permission(request)
            has_delete = admin_class.has_delete_permission(request)
            
            self.stdout.write(f'\n📋 PlanoContratacao:')
            self.stdout.write(f'  Ver: {"✅" if has_view else "❌"}')
            self.stdout.write(f'  Adicionar: {"✅" if has_add else "❌"}')
            self.stdout.write(f'  Editar: {"✅" if has_change else "❌"}')
            self.stdout.write(f'  Deletar: {"✅" if has_delete else "❌"}')
            
        except Exception as e:
            self.stdout.write(f'  ❌ Erro: {str(e)}')

