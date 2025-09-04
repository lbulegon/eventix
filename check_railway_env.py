#!/usr/bin/env python
"""
Script para verificar variáveis de ambiente do Railway
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from django.conf import settings

def main():
    """Verificar variáveis de ambiente do Railway"""
    print("=== VARIÁVEIS DE AMBIENTE DO RAILWAY ===")
    
    try:
        # Verificar variáveis do Railway
        railway_env = os.getenv('RAILWAY_ENVIRONMENT')
        railway_project_id = os.getenv('RAILWAY_PROJECT_ID')
        railway_service = os.getenv('RAILWAY_SERVICE')
        
        print(f"🚂 RAILWAY_ENVIRONMENT: {railway_env}")
        print(f"🆔 RAILWAY_PROJECT_ID: {railway_project_id}")
        print(f"🔧 RAILWAY_SERVICE: {railway_service}")
        
        # Verificar variáveis de banco
        db_url = os.getenv('DATABASE_URL')
        db_host = os.getenv('DB_HOST')
        db_name = os.getenv('DB_NAME')
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        db_port = os.getenv('DB_PORT')
        
        print(f"\n📊 VARIÁVEIS DE BANCO:")
        print(f"   DATABASE_URL: {'✅ Definida' if db_url else '❌ Não definida'}")
        print(f"   DB_HOST: {db_host}")
        print(f"   DB_NAME: {db_name}")
        print(f"   DB_USER: {db_user}")
        print(f"   DB_PASSWORD: {'✅ Definida' if db_password else '❌ Não definida'}")
        print(f"   DB_PORT: {db_port}")
        
        # Verificar configuração atual do Django
        print(f"\n🔧 CONFIGURAÇÃO ATUAL DO DJANGO:")
        db_config = settings.DATABASES['default']
        print(f"   Engine: {db_config['ENGINE']}")
        print(f"   Host: {db_config['HOST']}")
        print(f"   Name: {db_config['NAME']}")
        print(f"   User: {db_config['USER']}")
        print(f"   Port: {db_config['PORT']}")
        
        # Verificar se está no Railway
        if railway_env:
            print(f"\n✅ Executando no Railway!")
        else:
            print(f"\n⚠️ Executando localmente")
            
    except Exception as e:
        print(f"❌ Erro ao verificar variáveis: {e}")

if __name__ == "__main__":
    main()
