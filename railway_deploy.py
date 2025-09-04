#!/usr/bin/env python
"""
Script para deploy completo no Railway
Executa migrações e popula dados
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.contrib.auth import get_user_model

User = get_user_model()

def create_superuser():
    """Criar superusuário se não existir"""
    try:
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@eventix.com',
                password='admin123'
            )
            print("✅ Superusuário 'admin' criado com sucesso!")
        else:
            print("ℹ️ Superusuário 'admin' já existe")
    except Exception as e:
        print(f"❌ Erro ao criar superusuário: {e}")

def main():
    """Deploy completo no Railway"""
    print("=== DEPLOY COMPLETO NO RAILWAY ===")
    
    try:
        # 1. Aplicar migrações
        print("1. Aplicando migrações...")
        execute_from_command_line(['manage.py', 'migrate', '--run-syncdb'])
        print("✅ Migrações aplicadas!")
        
        # 2. Criar superusuário
        print("2. Criando superusuário...")
        create_superuser()
        
        # 3. Verificar status
        from app_eventos.models import Evento, EmpresaContratante
        
        eventos_count = Evento.objects.count()
        empresas_count = EmpresaContratante.objects.count()
        users_count = User.objects.count()
        
        print(f"📊 Status do banco:")
        print(f"   - Eventos: {eventos_count}")
        print(f"   - Empresas: {empresas_count}")
        print(f"   - Usuários: {users_count}")
        
        # 4. Se não há dados básicos, popular
        if eventos_count == 0:
            print("4. Populando dados básicos...")
            try:
                # Executar script de população
                exec(open('populate_sistema_completo.py').read())
                print("✅ Dados básicos populados!")
            except Exception as e:
                print(f"⚠️ Erro ao popular dados básicos: {e}")
        
        # 5. Popular novos modelos se necessário
        from app_eventos.models import MetricaEvento
        metricas_count = MetricaEvento.objects.count()
        
        if metricas_count == 0:
            print("5. Populando novos modelos...")
            try:
                exec(open('populate_novos_modelos_simples.py').read())
                print("✅ Novos modelos populados!")
            except Exception as e:
                print(f"⚠️ Erro ao popular novos modelos: {e}")
        
        print("\n🎉 Deploy concluído com sucesso!")
        print("🔑 Credenciais do admin:")
        print("   Usuário: admin")
        print("   Senha: admin123")
        
    except Exception as e:
        print(f"❌ Erro no deploy: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
