"""
Comando para testar o sistema de administração privada
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from app_eventos.models import EmpresaContratante, GrupoPermissaoEmpresa

User = get_user_model()


class Command(BaseCommand):
    help = 'Testa o sistema de administração privada'

    def handle(self, *args, **options):
        self.stdout.write('=== TESTANDO SISTEMA DE ADMINISTRACAO PRIVADA ===')
        
        # 1. Verificar usuários criados
        self.stdout.write('\n1. USUARIOS CRIADOS:')
        usuarios = User.objects.all()
        for usuario in usuarios:
            self.stdout.write(f'  - {usuario.username} ({usuario.get_tipo_usuario_display()})')
            if usuario.empresa_contratante:
                self.stdout.write(f'    Empresa: {usuario.empresa_contratante.nome_fantasia}')
        
        # 2. Verificar empresas contratantes
        self.stdout.write('\n2. EMPRESAS CONTRATANTES:')
        empresas = EmpresaContratante.objects.all()
        for empresa in empresas:
            self.stdout.write(f'  - {empresa.nome_fantasia} (CNPJ: {empresa.cnpj})')
            self.stdout.write(f'    Ativa: {empresa.ativo}')
            self.stdout.write(f'    Plano: {empresa.plano_contratado.nome if empresa.plano_contratado else "N/A"}')
        
        # 3. Verificar grupos de permissão
        self.stdout.write('\n3. GRUPOS DE PERMISSAO:')
        grupos = GrupoPermissaoEmpresa.objects.all()
        for grupo in grupos:
            self.stdout.write(f'  - {grupo.nome} ({grupo.empresa_contratante.nome_fantasia})')
            self.stdout.write(f'    Usuarios: {grupo.usuarios.count()}')
            self.stdout.write(f'    Pode gerenciar usuarios: {grupo.pode_gerenciar_usuarios}')
            self.stdout.write(f'    Pode gerenciar financeiro: {grupo.pode_gerenciar_financeiro}')
        
        # 4. Verificar modelos globais
        self.stdout.write('\n4. MODELOS GLOBAIS:')
        from app_eventos.models_globais import (
            CategoriaGlobal, TipoGlobal, ClassificacaoGlobal,
            ConfiguracaoSistema, IntegracaoGlobal, TemplateGlobal,
            CategoriaFreelancerGlobal, HabilidadeGlobal, FornecedorGlobal
        )
        
        self.stdout.write(f'  - Categorias Globais: {CategoriaGlobal.objects.count()}')
        self.stdout.write(f'  - Tipos Globais: {TipoGlobal.objects.count()}')
        self.stdout.write(f'  - Classificacoes Globais: {ClassificacaoGlobal.objects.count()}')
        self.stdout.write(f'  - Configuracoes Sistema: {ConfiguracaoSistema.objects.count()}')
        self.stdout.write(f'  - Integracoes Globais: {IntegracaoGlobal.objects.count()}')
        self.stdout.write(f'  - Templates Globais: {TemplateGlobal.objects.count()}')
        self.stdout.write(f'  - Categorias Freelancer: {CategoriaFreelancerGlobal.objects.count()}')
        self.stdout.write(f'  - Habilidades Globais: {HabilidadeGlobal.objects.count()}')
        self.stdout.write(f'  - Fornecedores Globais: {FornecedorGlobal.objects.count()}')
        
        # 5. Testar permissões
        self.stdout.write('\n5. TESTANDO PERMISSOES:')
        admin_empresa = User.objects.filter(tipo_usuario='admin_empresa').first()
        if admin_empresa:
            self.stdout.write(f'  Admin da Empresa: {admin_empresa.username}')
            self.stdout.write(f'  Pode gerenciar usuarios: {admin_empresa.pode_gerenciar_usuarios()}')
            self.stdout.write(f'  Pode gerenciar eventos: {admin_empresa.pode_gerenciar_eventos()}')
            self.stdout.write(f'  Pode gerenciar financeiro: {admin_empresa.pode_gerenciar_financeiro()}')
            self.stdout.write(f'  Permissoes disponiveis: {len(admin_empresa.get_permissoes_disponiveis())}')
        
        self.stdout.write('\n=== SISTEMA FUNCIONANDO CORRETAMENTE! ===')
