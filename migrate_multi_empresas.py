#!/usr/bin/env python
"""
Script para migrar o sistema para multi-empresas
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from django.db import connection
from app_eventos.models import EmpresaContratante, TipoEmpresa, User
from datetime import date, timedelta

def criar_empresa_inicial():
    """Cria a empresa inicial do sistema"""
    print("Criando empresa inicial...")
    
    # Criar empresa contratante
    empresa_contratante, created = EmpresaContratante.objects.get_or_create(
        cnpj='00.000.000/0001-00',
        defaults={
            'nome': 'Eventix',
            'razao_social': 'Eventix LTDA',
            'nome_fantasia': 'Eventix',
            'email': 'admin@eventix.com',
            'data_vencimento': date.today() + timedelta(days=365),
            'plano_contratado': 'Premium',
            'valor_mensal': 999.99,
            'ativo': True
        }
    )
    
    if created:
        print(f"✓ Empresa '{empresa_contratante.nome_fantasia}' criada com sucesso!")
    else:
        print(f"⚠ Empresa '{empresa_contratante.nome_fantasia}' já existe.")
    
    return empresa_contratante

def criar_tipos_empresa():
    """Cria os tipos de empresa padrão"""
    print("Criando tipos de empresa...")
    
    tipos_empresa = [
        {'nome': 'Produtora', 'descricao': 'Empresas produtoras de eventos'},
        {'nome': 'Contratante de Recursos', 'descricao': 'Empresas que contratam freelancers'},
        {'nome': 'Proprietária de Local', 'descricao': 'Empresas proprietárias de locais de eventos'},
        {'nome': 'Fornecedora', 'descricao': 'Empresas fornecedoras de serviços e equipamentos'},
    ]
    
    for tipo_data in tipos_empresa:
        tipo, created = TipoEmpresa.objects.get_or_create(
            nome=tipo_data['nome'],
            defaults={'descricao': tipo_data['descricao']}
        )
        if created:
            print(f"✓ Tipo '{tipo.nome}' criado com sucesso!")
        else:
            print(f"⚠ Tipo '{tipo.nome}' já existe.")

def criar_admin_sistema():
    """Cria o administrador do sistema"""
    print("Criando administrador do sistema...")
    
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@eventix.com',
            'tipo_usuario': 'admin_sistema',
            'is_staff': True,
            'is_superuser': True,
            'ativo': True
        }
    )
    
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print(f"✓ Administrador '{admin_user.username}' criado com sucesso!")
    else:
        print(f"⚠ Administrador '{admin_user.username}' já existe.")

def atualizar_dados_existentes(empresa_contratante):
    """Atualiza dados existentes para usar a empresa contratante"""
    print("Atualizando dados existentes...")
    
    with connection.cursor() as cursor:
        # Atualizar categorias de equipamentos
        cursor.execute("""
            UPDATE app_eventos_categoriaequipamento 
            SET empresa_contratante_id = %s 
            WHERE empresa_contratante_id IS NULL
        """, [empresa_contratante.id])
        
        # Atualizar empresas
        cursor.execute("""
            UPDATE app_eventos_empresa 
            SET empresa_contratante_id = %s 
            WHERE empresa_contratante_id IS NULL
        """, [empresa_contratante.id])
        
        # Atualizar equipamentos
        cursor.execute("""
            UPDATE app_eventos_equipamento 
            SET empresa_contratante_id = %s 
            WHERE empresa_contratante_id IS NULL
        """, [empresa_contratante.id])
        
        # Atualizar locais de eventos
        cursor.execute("""
            UPDATE app_eventos_localevento 
            SET empresa_contratante_id = %s 
            WHERE empresa_contratante_id IS NULL
        """, [empresa_contratante.id])
        
        # Atualizar eventos
        cursor.execute("""
            UPDATE app_eventos_evento 
            SET empresa_contratante_id = %s 
            WHERE empresa_contratante_id IS NULL
        """, [empresa_contratante.id])
        
        # Atualizar tipos de função
        cursor.execute("""
            UPDATE app_eventos_tipofuncao 
            SET empresa_contratante_id = %s 
            WHERE empresa_contratante_id IS NULL
        """, [empresa_contratante.id])
    
    print("✓ Dados existentes atualizados com sucesso!")

def main():
    """Função principal"""
    print("=== MIGRAÇÃO PARA MULTI-EMPRESAS ===")
    print()
    
    try:
        # Criar empresa inicial
        empresa_contratante = criar_empresa_inicial()
        print()
        
        # Criar tipos de empresa
        criar_tipos_empresa()
        print()
        
        # Criar admin do sistema
        criar_admin_sistema()
        print()
        
        # Atualizar dados existentes
        atualizar_dados_existentes(empresa_contratante)
        print()
        
        print("=== MIGRAÇÃO CONCLUÍDA COM SUCESSO! ===")
        print()
        print("Credenciais do administrador:")
        print("Username: admin")
        print("Senha: admin123")
        print()
        print("Agora você pode executar:")
        print("python manage.py makemigrations")
        print("python manage.py migrate")
        
    except Exception as e:
        print(f"❌ Erro durante a migração: {e}")
        raise

if __name__ == '__main__':
    main()
