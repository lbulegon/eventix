#!/usr/bin/env python
"""
Comando simples para testar permissões
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from app_eventos.models import TipoFuncao, PlanoContratacao, EmpresaContratante
from app_eventos.admin import TipoFuncaoAdmin, PlanoContratacaoAdmin, EmpresaContratanteAdmin

User = get_user_model()


class Command(BaseCommand):
    help = 'Testa permissões de forma simples'

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
            factory = RequestFactory()
            request = factory.get('/admin/')
            request.user = user
            
            self.stdout.write(f'Testando permissões para: {user.username}')
            self.stdout.write(f'Tipo: {user.get_tipo_usuario_display()}')
            self.stdout.write('=' * 50)
            
            # Testar TipoFuncao (deve poder ver, não modificar)
            self._testar_admin(TipoFuncaoAdmin, TipoFuncao, request, "TipoFuncao")
            
            # Testar PlanoContratacao (deve poder ver, não modificar)
            self._testar_admin(PlanoContratacaoAdmin, PlanoContratacao, request, "PlanoContratacao")
            
            # Testar EmpresaContratante (não deve ver nem modificar)
            self._testar_admin(EmpresaContratanteAdmin, EmpresaContratante, request, "EmpresaContratante")

        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Usuário {username} não encontrado!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro: {str(e)}')
            )

    def _testar_admin(self, admin_class, model, request, nome):
        """Testa um admin específico"""
        try:
            admin = admin_class(model, None)
            
            ver = admin.has_view_permission(request)
            adicionar = admin.has_add_permission(request)
            editar = admin.has_change_permission(request)
            deletar = admin.has_delete_permission(request)
            
            self.stdout.write(f'\n{nome}:')
            self.stdout.write(f'  Ver: {"✅" if ver else "❌"}')
            self.stdout.write(f'  Adicionar: {"✅" if adicionar else "❌"}')
            self.stdout.write(f'  Editar: {"✅" if editar else "❌"}')
            self.stdout.write(f'  Deletar: {"✅" if deletar else "❌"}')
            
        except Exception as e:
            self.stdout.write(f'  ❌ Erro: {str(e)}')

