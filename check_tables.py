#!/usr/bin/env python
"""
Script para verificar tabelas no PostgreSQL
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from django.db import connection

def main():
    """Verificar tabelas no PostgreSQL"""
    print("=== VERIFICANDO TABELAS NO POSTGRESQL ===")
    
    try:
        cursor = connection.cursor()
        
        # Verificar tabelas app_eventos
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'app_eventos_%'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print(f"📊 Tabelas app_eventos encontradas: {len(tables)}")
        
        for table in tables:
            print(f"   - {table[0]}")
        
        # Verificar se a tabela app_eventos_user existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'app_eventos_user'
            );
        """)
        
        user_table_exists = cursor.fetchone()[0]
        print(f"\n🔍 Tabela app_eventos_user existe: {user_table_exists}")
        
        if not user_table_exists:
            print("❌ PROBLEMA: Tabela app_eventos_user não existe!")
            print("💡 Solução: Executar migrações")
        else:
            print("✅ Tabela app_eventos_user existe!")
            
    except Exception as e:
        print(f"❌ Erro ao verificar tabelas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
