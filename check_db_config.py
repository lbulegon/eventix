#!/usr/bin/env python
"""
Script para verificar configuração do banco de dados
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from django.conf import settings

def main():
    """Verificar configuração do banco"""
    print("=== CONFIGURAÇÃO DO BANCO DE DADOS ===")
    
    try:
        db_config = settings.DATABASES['default']
        
        print(f"🔧 Engine: {db_config['ENGINE']}")
        print(f"🏠 Host: {db_config['HOST']}")
        print(f"📊 Name: {db_config['NAME']}")
        print(f"👤 User: {db_config['USER']}")
        print(f"🔌 Port: {db_config['PORT']}")
        
        # Verificar se é PostgreSQL
        if 'postgresql' in db_config['ENGINE']:
            print("✅ Configurado para PostgreSQL")
        else:
            print("⚠️ NÃO é PostgreSQL!")
            
    except Exception as e:
        print(f"❌ Erro ao verificar configuração: {e}")

if __name__ == "__main__":
    main()
