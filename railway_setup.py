#!/usr/bin/env python
"""
Script para configurar o Railway com migrações e dados
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from django.core.management import execute_from_command_line

def main():
    """Configurar Railway com migrações e dados"""
    print("=== CONFIGURANDO RAILWAY ===")
    
    try:
        # 1. Aplicar migrações
        print("1. Aplicando migrações...")
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrações aplicadas!")
        
        # 2. Verificar se há dados
        from app_eventos.models import Evento, EmpresaContratante, User
        
        eventos_count = Evento.objects.count()
        empresas_count = EmpresaContratante.objects.count()
        users_count = User.objects.count()
        
        print(f"📊 Status do banco:")
        print(f"   - Eventos: {eventos_count}")
        print(f"   - Empresas: {empresas_count}")
        print(f"   - Usuários: {users_count}")
        
        # 3. Se não há dados, popular
        if eventos_count == 0:
            print("3. Populando dados...")
            execute_from_command_line(['manage.py', 'shell', '-c', 'exec(open("populate_sistema_completo.py").read())'])
            print("✅ Dados populados!")
        
        # 4. Popular novos modelos se necessário
        from app_eventos.models import MetricaEvento
        metricas_count = MetricaEvento.objects.count()
        
        if metricas_count == 0:
            print("4. Populando novos modelos...")
            execute_from_command_line(['manage.py', 'shell', '-c', 'exec(open("populate_novos_modelos_simples.py").read())'])
            print("✅ Novos modelos populados!")
        
        print("\n🎉 Railway configurado com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro na configuração: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
