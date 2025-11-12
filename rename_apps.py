#!/usr/bin/env python
"""
Script para renomear os apps Django para seguir o padrão app_*
"""
import os
import shutil
import re

# Mapeamento de apps antigos para novos
APP_MAPPING = {
    'briefing': 'app_briefing',
    'menu': 'app_menu',
    'financeiro': 'app_financeiro',
    'contratos': 'app_contratos',
    'producao': 'app_producao',
    'mise': 'app_mise',
    'operacao': 'app_operacao',
    'finalizacao': 'app_finalizacao',
    'fechamento': 'app_fechamento',
    'planejamento': 'app_planejamento',
}

def rename_directory(old_name, new_name):
    """Renomeia um diretório"""
    if os.path.exists(old_name) and not os.path.exists(new_name):
        print(f"Renomeando {old_name} -> {new_name}")
        shutil.move(old_name, new_name)
        return True
    elif os.path.exists(new_name):
        print(f"⚠️  {new_name} já existe, pulando...")
        return False
    else:
        print(f"❌ {old_name} não existe")
        return False

def update_file_imports(file_path, app_mapping):
    """Atualiza imports em um arquivo"""
    if not os.path.exists(file_path):
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Atualizar imports
        for old_app, new_app in app_mapping.items():
            # from old_app import
            content = re.sub(
                rf'from {old_app}\.',
                f'from {new_app}.',
                content
            )
            # import old_app
            content = re.sub(
                rf'\bimport {old_app}\b',
                f'import {new_app}',
                content
            )
            # "old_app.Model" ou 'old_app.Model'
            content = re.sub(
                rf'["\']{old_app}\.',
                f'"{new_app}.',
                content
            )
            content = re.sub(
                rf"['\"]{old_app}\.",
                f"'{new_app}.",
                content
            )
        
        # Atualizar referências de "eventos.Evento" para "app_eventos.Evento"
        content = re.sub(
            r'"eventos\.Evento"',
            '"app_eventos.Evento"',
            content
        )
        content = re.sub(
            r"'eventos\.Evento'",
            "'app_eventos.Evento'",
            content
        )
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Atualizado: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"❌ Erro ao atualizar {file_path}: {e}")
        return False

def update_apps_py(app_dir, old_name, new_name):
    """Atualiza o arquivo apps.py"""
    apps_py = os.path.join(app_dir, 'apps.py')
    if os.path.exists(apps_py):
        with open(apps_py, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Atualizar name = "old_name" para name = "new_name"
        content = re.sub(
            rf'name\s*=\s*["\']{old_name}["\']',
            f'name = "{new_name}"',
            content
        )
        
        # Atualizar nome da classe
        class_name = old_name.capitalize() + 'Config'
        new_class_name = new_name.replace('app_', '').capitalize() + 'Config'
        content = re.sub(
            rf'class {class_name}',
            f'class {new_class_name}',
            content
        )
        
        with open(apps_py, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Atualizado apps.py: {apps_py}")

def main():
    """Função principal"""
    print("🔄 Renomeando apps Django para seguir o padrão app_*")
    print("=" * 60)
    
    # 1. Renomear diretórios
    print("\n1. Renomeando diretórios...")
    for old_name, new_name in APP_MAPPING.items():
        rename_directory(old_name, new_name)
    
    # 2. Atualizar apps.py de cada app
    print("\n2. Atualizando apps.py...")
    for old_name, new_name in APP_MAPPING.items():
        if os.path.exists(new_name):
            update_apps_py(new_name, old_name, new_name)
    
    # 3. Atualizar settings.py
    print("\n3. Atualizando settings.py...")
    update_file_imports('setup/settings.py', APP_MAPPING)
    
    # 4. Atualizar arquivos que importam os apps
    print("\n4. Atualizando imports...")
    files_to_update = [
        'api_v01/urls/eventos.py',
        'contratos/tests.py',
        'contratos/views.py',
        'app_eventos/services/event_clone_service.py',
    ]
    
    for file_path in files_to_update:
        # Verificar se o arquivo está no novo local
        if 'contratos' in file_path:
            file_path = file_path.replace('contratos', 'app_contratos')
        update_file_imports(file_path, APP_MAPPING)
    
    # 5. Atualizar modelos dentro de cada app
    print("\n5. Atualizando modelos...")
    for old_name, new_name in APP_MAPPING.items():
        app_dir = new_name
        if os.path.exists(app_dir):
            # Atualizar models.py
            models_py = os.path.join(app_dir, 'models.py')
            if os.path.exists(models_py):
                update_file_imports(models_py, APP_MAPPING)
            
            # Atualizar outros arquivos Python
            for root, dirs, files in os.walk(app_dir):
                # Pular migrations e __pycache__
                if 'migrations' in root or '__pycache__' in root:
                    continue
                
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        update_file_imports(file_path, APP_MAPPING)
    
    print("\n✅ Renomeação concluída!")
    print("\n⚠️  PRÓXIMOS PASSOS:")
    print("1. Verificar se todas as referências foram atualizadas")
    print("2. Deletar migrations antigas e recriar")
    print("3. Atualizar INSTALLED_APPS no settings.py manualmente se necessário")
    print("4. Testar o sistema")

if __name__ == '__main__':
    main()

