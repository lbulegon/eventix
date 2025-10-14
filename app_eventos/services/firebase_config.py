"""
Configuração do Firebase Admin SDK
"""
import json
import os
import firebase_admin
from firebase_admin import credentials
from django.conf import settings


def inicializar_firebase():
    """
    Inicializa o Firebase Admin SDK se ainda não foi inicializado
    """
    if not firebase_admin._apps:
        try:
            # Opção 1: Carregar do arquivo JSON
            sa_path = os.environ.get("FIREBASE_SA_PATH")
            if sa_path and os.path.exists(sa_path):
                cred = credentials.Certificate(sa_path)
                firebase_admin.initialize_app(cred)
                print("✓ Firebase inicializado com arquivo de credenciais")
                return True
            
            # Opção 2: Carregar do JSON inline (variável de ambiente)
            sa_json = os.environ.get("FIREBASE_SA_JSON")
            if sa_json:
                cred = credentials.Certificate(json.loads(sa_json))
                firebase_admin.initialize_app(cred)
                print("✓ Firebase inicializado com JSON inline")
                return True
            
            # Se não tem credenciais, avisar mas não travar o sistema
            print("⚠ Firebase não configurado (FIREBASE_SA_PATH ou FIREBASE_SA_JSON não definidos)")
            return False
            
        except Exception as e:
            print(f"✗ Erro ao inicializar Firebase: {str(e)}")
            return False
    
    return True


def get_firebase_app():
    """
    Retorna a instância do Firebase App
    """
    if not firebase_admin._apps:
        inicializar_firebase()
    
    if firebase_admin._apps:
        return firebase_admin.get_app()
    
    return None

