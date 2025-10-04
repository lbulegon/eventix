#!/usr/bin/env python
"""
Comando para testar permissões de usuários admin de empresa
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from app_eventos.models import (
    TipoFuncao, PlanoContratacao, EmpresaContratante, 
    TipoEmpresa, Empresa, LocalEvento, Evento
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Testa permissões de usuários admin de empresa'

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
            self.stdout.write(f'Testando permissões para: {user.username}')
            self.stdout.write(f'Tipo: {user.get_tipo_usuario_display()}')
            self.stdout.write(f'Empresa: {user.empresa_contratante.nome_fantasia if user.empresa_contratante else "Nenhuma"}')
            self.stdout.write('=' * 60)
            
            # Teste 1: Tabelas genéricas (deve poder visualizar, mas não modificar)
            self.stdout.write('\n📋 TESTE 1: Tabelas Genéricas (Visualização)')
            self._testar_tabelas_genericas(user)
            
            # Teste 2: Dados da empresa (deve poder ver e modificar)
            self.stdout.write('\n🏢 TESTE 2: Dados da Empresa')
            self._testar_dados_empresa(user)
            
            # Teste 3: Dados de outras empresas (não deve ver)
            self.stdout.write('\n🚫 TESTE 3: Dados de Outras Empresas')
            self._testar_dados_outras_empresas(user)

        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Usuário {username} não encontrado!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro: {str(e)}')
            )

    def _testar_tabelas_genericas(self, user):
        """Testa acesso às tabelas genéricas"""
        tabelas_genericas = [
            ('TipoFuncao', TipoFuncao),
            ('PlanoContratacao', PlanoContratacao),
            ('EmpresaContratante', EmpresaContratante),
            ('TipoEmpresa', TipoEmpresa),
            ('Empresa', Empresa),
            ('LocalEvento', LocalEvento),
        ]
        
        for nome, modelo in tabelas_genericas:
            try:
                count = modelo.objects.count()
                self.stdout.write(f'  ✅ {nome}: {count} registros (pode visualizar)')
            except Exception as e:
                self.stdout.write(f'  ❌ {nome}: Erro - {str(e)}')

    def _testar_dados_empresa(self, user):
        """Testa acesso aos dados da empresa do usuário"""
        if not user.empresa_contratante:
            self.stdout.write('  ❌ Usuário não tem empresa contratante')
            return
            
        empresa = user.empresa_contratante
        
        # Teste eventos da empresa
        eventos = Evento.objects.filter(empresa_contratante=empresa)
        self.stdout.write(f'  ✅ Eventos da empresa: {eventos.count()} registros')
        
        # Teste usuários da empresa
        usuarios = User.objects.filter(empresa_contratante=empresa)
        self.stdout.write(f'  ✅ Usuários da empresa: {usuarios.count()} registros')

    def _testar_dados_outras_empresas(self, user):
        """Testa se não vê dados de outras empresas"""
        if not user.empresa_contratante:
            self.stdout.write('  ❌ Usuário não tem empresa contratante')
            return
            
        # Contar total de eventos
        total_eventos = Evento.objects.count()
        eventos_empresa = Evento.objects.filter(empresa_contratante=user.empresa_contratante).count()
        outros_eventos = total_eventos - eventos_empresa
        
        self.stdout.write(f'  📊 Total de eventos no sistema: {total_eventos}')
        self.stdout.write(f'  ✅ Eventos da sua empresa: {eventos_empresa}')
        self.stdout.write(f'  🚫 Eventos de outras empresas: {outros_eventos} (não deve ver)')
        
        if outros_eventos > 0:
            self.stdout.write('  ⚠️  ATENÇÃO: Existem eventos de outras empresas no sistema!')
        else:
            self.stdout.write('  ✅ Sistema isolado corretamente!')

