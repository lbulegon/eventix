#!/usr/bin/env python
"""
Script para verificar e resetar senha do admin_diego
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from app_eventos.models import User

def main():
    """Verificar e resetar senha do admin_diego"""
    print("=== VERIFICANDO USUÁRIO admin_diego ===\n")
    
    # Buscar usuário
    username = 'admin_diego'
    try:
        user = User.objects.get(username=username)
        print(f"✅ Usuário encontrado: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Superusuário: {user.is_superuser}")
        print(f"   Staff: {user.is_staff}")
        print(f"   Ativo: {user.ativo if hasattr(user, 'ativo') else 'N/A'}")
        
        # Resetar senha
        nova_senha = 'admin123'
        user.set_password(nova_senha)
        user.save()
        
        print(f"\n✅ Senha resetada com sucesso!")
        print(f"   Usuário: {username}")
        print(f"   Nova senha: {nova_senha}")
        
    except User.DoesNotExist:
        print(f"❌ Usuário '{username}' não encontrado!")
        print("\n📋 Usuários admin disponíveis:")
        admins = User.objects.filter(is_superuser=True)
        for admin in admins:
            print(f"   - {admin.username} ({admin.email})")
        
        # Perguntar se quer criar
        criar = input(f"\n❓ Deseja criar o usuário '{username}'? (s/n): ")
        if criar.lower() == 's':
            email = input("   Email: ").strip() or f"{username}@eventix.com"
            senha = input("   Senha (enter para 'admin123'): ").strip() or 'admin123'
            
            user = User.objects.create_user(
                username=username,
                email=email,
                password=senha,
                is_superuser=True,
                is_staff=True
            )
            
            if hasattr(user, 'tipo_usuario'):
                user.tipo_usuario = 'admin_sistema'
                user.save()
            
            print(f"\n✅ Usuário '{username}' criado com sucesso!")
            print(f"   Email: {email}")
            print(f"   Senha: {senha}")
    
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

