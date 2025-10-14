import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from django.db import connection

print("🔍 Verificando configuração do banco de dados...\n")
print(f"Engine: {connection.settings_dict['ENGINE']}")
print(f"Nome: {connection.settings_dict.get('NAME', 'N/A')}")
print(f"Host: {connection.settings_dict.get('HOST', 'N/A')}")
print(f"Port: {connection.settings_dict.get('PORT', 'N/A')}")
print(f"User: {connection.settings_dict.get('USER', 'N/A')}")

from app_eventos.models import Freelance, EmpresaContratante
print(f"\n📊 Estatísticas:")
print(f"Total de freelancers: {Freelance.objects.count()}")
print(f"Total de empresas: {EmpresaContratante.objects.count()}")

