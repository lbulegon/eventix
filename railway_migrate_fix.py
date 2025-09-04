#!/usr/bin/env python
"""
Script para corrigir migrações no Railway
Execute este script no Railway para criar as tabelas
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.db import connection
from django.contrib.auth import get_user_model

User = get_user_model()

def check_tables():
    """Verificar quais tabelas existem"""
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Tabelas existentes: {tables}")
        return tables

def create_tables_manually():
    """Criar tabelas manualmente se necessário"""
    with connection.cursor() as cursor:
        # Verificar se a tabela de usuários existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='app_eventos_user';")
        if not cursor.fetchone():
            print("Criando tabela app_eventos_user...")
            # Criar tabela de usuários básica
            cursor.execute("""
                CREATE TABLE app_eventos_user (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    password VARCHAR(128) NOT NULL,
                    last_login DATETIME,
                    is_superuser BOOLEAN NOT NULL,
                    username VARCHAR(150) NOT NULL UNIQUE,
                    first_name VARCHAR(150) NOT NULL,
                    last_name VARCHAR(150) NOT NULL,
                    email VARCHAR(254) NOT NULL,
                    is_staff BOOLEAN NOT NULL,
                    is_active BOOLEAN NOT NULL,
                    date_joined DATETIME NOT NULL
                );
            """)
            print("✅ Tabela app_eventos_user criada!")

def main():
    """Corrigir banco de dados no Railway"""
    print("=== CORRIGINDO BANCO DE DADOS NO RAILWAY ===")
    
    try:
        # 1. Verificar tabelas existentes
        print("1. Verificando tabelas existentes...")
        tables = check_tables()
        
        # 2. Aplicar migrações
        print("2. Aplicando migrações...")
        execute_from_command_line(['manage.py', 'migrate', '--run-syncdb'])
        print("✅ Migrações aplicadas!")
        
        # 3. Verificar novamente
        print("3. Verificando tabelas após migrações...")
        tables_after = check_tables()
        
        # 4. Se ainda não há tabela de usuários, criar manualmente
        if 'app_eventos_user' not in tables_after:
            print("4. Criando tabelas manualmente...")
            create_tables_manually()
        
        # 5. Criar superusuário
        print("5. Criando superusuário...")
        try:
            if not User.objects.filter(username='admin').exists():
                User.objects.create_superuser(
                    username='admin',
                    email='admin@eventix.com',
                    password='admin123'
                )
                print("✅ Superusuário 'admin' criado!")
            else:
                print("ℹ️ Superusuário 'admin' já existe")
        except Exception as e:
            print(f"⚠️ Erro ao criar superusuário: {e}")
        
        # 6. Verificar status final
        print("6. Status final do banco:")
        try:
            users_count = User.objects.count()
            print(f"   - Usuários: {users_count}")
        except Exception as e:
            print(f"   - Erro ao contar usuários: {e}")
        
        print("\n🎉 Correção concluída!")
        print("🔑 Credenciais do admin:")
        print("   Usuário: admin")
        print("   Senha: admin123")
        
    except Exception as e:
        print(f"❌ Erro na correção: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
