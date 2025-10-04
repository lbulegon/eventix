#!/usr/bin/env python
"""
Comando para configurar permissões de usuários de empresa
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

User = get_user_model()


class Command(BaseCommand):
    help = 'Configura permissões para usuários de empresa'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username específico (opcional)'
        )
        parser.add_argument(
            '--todos',
            action='store_true',
            help='Configurar todos os usuários de empresa'
        )

    def handle(self, *args, **options):
        username = options.get('username')
        todos = options.get('todos')

        try:
            if username:
                # Configurar usuário específico
                try:
                    user = User.objects.get(username=username)
                    if user.tipo_usuario in ['admin_empresa', 'operador_empresa']:
                        self._configurar_permissoes_usuario(user)
                        self.stdout.write(
                            self.style.SUCCESS(f'Permissões configuradas para {username}!')
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'Usuário {username} não é de empresa!')
                        )
                except User.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f'Usuário {username} não encontrado!')
                    )
            elif todos:
                # Configurar todos os usuários de empresa
                usuarios = User.objects.filter(
                    tipo_usuario__in=['admin_empresa', 'operador_empresa']
                )
                
                for user in usuarios:
                    self._configurar_permissoes_usuario(user)
                    self.stdout.write(f'✓ {user.username} configurado')
                
                self.stdout.write(
                    self.style.SUCCESS(f'{usuarios.count()} usuário(s) configurado(s)!')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('Use --username USERNAME ou --todos')
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro: {str(e)}')
            )

    def _configurar_permissoes_usuario(self, user):
        """Configura permissões para um usuário"""
        # Garantir que é staff e ativo
        user.is_staff = True
        user.is_active = True
        user.save()
        
        # Remover todas as permissões existentes
        user.user_permissions.clear()
        
        # Adicionar permissões básicas do admin
        permissoes_basicas = [
            'app_eventos.view_evento',
            'app_eventos.add_evento',
            'app_eventos.change_evento',
            'app_eventos.delete_evento',
            'app_eventos.view_user',
            'app_eventos.add_user',
            'app_eventos.change_user',
            'app_eventos.delete_user',
            'app_eventos.view_freelance',
            'app_eventos.view_candidatura',
            'app_eventos.view_contratofreelance',
            'app_eventos.view_equipamento',
            'app_eventos.view_vaga',
            'app_eventos.view_funcao',
            'app_eventos.view_categoriaequipamento',
            'app_eventos.view_categoriafinanceira',
            'app_eventos.view_fornecedor',
            'app_eventos.view_despesaevento',
            'app_eventos.view_receitaevento',
            'app_eventos.view_grupopermissaoempresa',
        ]
        
        # Se for admin da empresa, adicionar permissões de modificação
        if user.tipo_usuario == 'admin_empresa':
            permissoes_basicas.extend([
                'app_eventos.add_freelance',
                'app_eventos.change_freelance',
                'app_eventos.delete_freelance',
                'app_eventos.add_candidatura',
                'app_eventos.change_candidatura',
                'app_eventos.delete_candidatura',
                'app_eventos.add_contratofreelance',
                'app_eventos.change_contratofreelance',
                'app_eventos.delete_contratofreelance',
                'app_eventos.add_equipamento',
                'app_eventos.change_equipamento',
                'app_eventos.delete_equipamento',
                'app_eventos.add_vaga',
                'app_eventos.change_vaga',
                'app_eventos.delete_vaga',
                'app_eventos.add_funcao',
                'app_eventos.change_funcao',
                'app_eventos.delete_funcao',
                'app_eventos.add_categoriaequipamento',
                'app_eventos.change_categoriaequipamento',
                'app_eventos.delete_categoriaequipamento',
                'app_eventos.add_categoriafinanceira',
                'app_eventos.change_categoriafinanceira',
                'app_eventos.delete_categoriafinanceira',
                'app_eventos.add_fornecedor',
                'app_eventos.change_fornecedor',
                'app_eventos.delete_fornecedor',
                'app_eventos.add_despesaevento',
                'app_eventos.change_despesaevento',
                'app_eventos.delete_despesaevento',
                'app_eventos.add_receitaevento',
                'app_eventos.change_receitaevento',
                'app_eventos.delete_receitaevento',
                'app_eventos.add_grupopermissaoempresa',
                'app_eventos.change_grupopermissaoempresa',
                'app_eventos.delete_grupopermissaoempresa',
            ])
        
        # Adicionar permissões
        for codename in permissoes_basicas:
            try:
                app_label, permission = codename.split('.')
                perm = Permission.objects.get(
                    content_type__app_label=app_label,
                    codename=permission
                )
                user.user_permissions.add(perm)
            except Permission.DoesNotExist:
                # Permissão não existe, pular
                continue
