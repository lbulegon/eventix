#!/usr/bin/env python
"""
Script para corrigir o banco de dados no Railway
Execute este script diretamente no Railway
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

def main():
    """Corrigir banco de dados no Railway"""
    print("=== CORRIGINDO BANCO DE DADOS NO RAILWAY ===")
    
    try:
        # 1. Aplicar migrações
        print("1. Aplicando migrações...")
        execute_from_command_line(['manage.py', 'migrate', '--run-syncdb'])
        print("✅ Migrações aplicadas!")
        
        # 2. Criar superusuário
        print("2. Criando superusuário...")
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
        
        # 3. Verificar status
        from app_eventos.models import Evento, EmpresaContratante
        
        eventos_count = Evento.objects.count()
        empresas_count = EmpresaContratante.objects.count()
        users_count = User.objects.count()
        
        print(f"📊 Status do banco:")
        print(f"   - Eventos: {eventos_count}")
        print(f"   - Empresas: {empresas_count}")
        print(f"   - Usuários: {users_count}")
        
        # 4. Se não há dados, criar dados básicos
        if eventos_count == 0:
            print("4. Criando dados básicos...")
            try:
                # Criar empresa contratante
                from app_eventos.models import EmpresaContratante, LocalEvento, Evento
                
                empresa, created = EmpresaContratante.objects.get_or_create(
                    cnpj='12.345.678/0001-90',
                    defaults={
                        'razao_social': 'Eventos Premium LTDA',
                        'nome_fantasia': 'Eventos Premium',
                        'logradouro': 'Rua das Flores',
                        'numero': '123',
                        'bairro': 'Centro',
                        'cidade': 'São Paulo',
                        'uf': 'SP',
                        'cep': '01234-567',
                        'telefone': '(11) 99999-9999',
                        'email': 'contato@eventospremium.com'
                    }
                )
                
                if created:
                    print("✅ Empresa contratante criada")
                
                # Criar local do evento
                local, created = LocalEvento.objects.get_or_create(
                    nome='Centro de Convenções',
                    defaults={
                        'endereco': 'Av. Paulista, 1000 - São Paulo/SP',
                        'capacidade': 500
                    }
                )
                
                if created:
                    print("✅ Local do evento criado")
                
                # Criar evento
                evento, created = Evento.objects.get_or_create(
                    nome='Evento de Teste',
                    defaults={
                        'empresa_contratante': empresa,
                        'local': local,
                        'data_inicio': '2024-12-01 09:00:00',
                        'data_fim': '2024-12-01 18:00:00',
                        'descricao': 'Evento de teste para demonstração'
                    }
                )
                
                if created:
                    print("✅ Evento criado")
                
                print("✅ Dados básicos criados!")
                
            except Exception as e:
                print(f"⚠️ Erro ao criar dados básicos: {e}")
        
        print("\n🎉 Banco de dados corrigido com sucesso!")
        print("🔑 Credenciais do admin:")
        print("   Usuário: admin")
        print("   Senha: admin123")
        
    except Exception as e:
        print(f"❌ Erro na correção: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
