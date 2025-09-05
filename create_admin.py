#!/usr/bin/env python
"""
Script para criar superusuário no PostgreSQL
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def main():
    """Criar superusuário admin"""
    print("=== CRIANDO SUPERUSUÁRIO NO POSTGRESQL ===")
    
    try:
        # Criar ou atualizar superusuário
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@eventix.com',
                'is_superuser': True,
                'is_staff': True
            }
        )
        
        # Definir senha
        user.set_password('admin123')
        user.save()
        
        if created:
            print("✅ Superusuário 'admin' criado com sucesso!")
        else:
            print("✅ Superusuário 'admin' atualizado com sucesso!")
        
        print("🔑 Credenciais:")
        print("   Usuário: admin")
        print("   Senha: admin123")
        
        # Verificar usuários no banco
        total_users = User.objects.count()
        superusers = User.objects.filter(is_superuser=True).count()
        
        print(f"\n📊 Status do banco PostgreSQL:")
        print(f"   - Total de usuários: {total_users}")
        print(f"   - Superusuários: {superusers}")
        
    except Exception as e:
        print(f"❌ Erro ao criar superusuário: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
