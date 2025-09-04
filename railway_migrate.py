#!/usr/bin/env python
"""
Script para aplicar migrações no Railway
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from django.core.management import execute_from_command_line

def main():
    """Aplicar migrações no Railway"""
    print("=== APLICANDO MIGRAÇÕES NO RAILWAY ===")
    
    try:
        # Aplicar todas as migrações
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrações aplicadas com sucesso!")
        
        # Verificar status das migrações
        execute_from_command_line(['manage.py', 'showmigrations'])
        
    except Exception as e:
        print(f"❌ Erro ao aplicar migrações: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
