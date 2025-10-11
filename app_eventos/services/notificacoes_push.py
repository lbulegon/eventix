"""
Serviço de Notificações Push via Firebase Cloud Messaging (FCM)
"""
import requests
import json
from django.conf import settings


class NotificacaoPushService:
    """
    Serviço para enviar notificações push via FCM
    """
    
    FCM_URL = "https://fcm.googleapis.com/fcm/send"
    
    def __init__(self):
        # Chave do servidor FCM (deve ser configurada no settings.py)
        self.server_key = getattr(settings, 'FCM_SERVER_KEY', None)
    
    def enviar_notificacao_vaga(self, device_token, vaga):
        """
        Envia notificação sobre nova vaga para um freelancer
        """
        if not self.server_key:
            print("AVISO: FCM_SERVER_KEY não configurado no settings.py")
            return False
        
        if not device_token:
            print("AVISO: Device token não fornecido")
            return False
        
        # Preparar mensagem
        titulo = "Nova Vaga Disponível!"
        mensagem = f"{vaga.titulo} - R$ {vaga.remuneracao}"
        
        # Dados adicionais para o app
        data_adicional = {
            'vaga_id': str(vaga.id),
            'titulo': vaga.titulo,
            'remuneracao': str(vaga.remuneracao),
            'tipo_remuneracao': vaga.tipo_remuneracao,
            'evento_nome': vaga.setor.evento.nome if vaga.setor and vaga.setor.evento else '',
            'setor_nome': vaga.setor.nome if vaga.setor else '',
        }
        
        # Montar payload FCM
        payload = {
            "to": device_token,
            "notification": {
                "title": titulo,
                "body": mensagem,
                "sound": "default",
                "badge": "1",
                "icon": "ic_notification",
                "color": "#667eea"
            },
            "data": data_adicional,
            "priority": "high"
        }
        
        # Headers
        headers = {
            "Authorization": f"key={self.server_key}",
            "Content-Type": "application/json"
        }
        
        try:
            # Enviar requisição
            response = requests.post(
                self.FCM_URL,
                data=json.dumps(payload),
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success', 0) > 0:
                    print(f"✓ Notificação enviada com sucesso para vaga: {vaga.titulo}")
                    return True
                else:
                    print(f"✗ Erro ao enviar notificação: {result}")
                    return False
            else:
                print(f"✗ Erro HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"✗ Exceção ao enviar notificação: {str(e)}")
            return False
    
    def enviar_notificacao_multipla(self, device_tokens, vaga):
        """
        Envia notificação para múltiplos dispositivos
        """
        if not self.server_key:
            print("AVISO: FCM_SERVER_KEY não configurado no settings.py")
            return 0
        
        if not device_tokens or len(device_tokens) == 0:
            print("AVISO: Nenhum device token fornecido")
            return 0
        
        # Preparar mensagem
        titulo = "Nova Vaga Disponível!"
        mensagem = f"{vaga.titulo} - R$ {vaga.remuneracao}"
        
        # Dados adicionais
        data_adicional = {
            'vaga_id': str(vaga.id),
            'titulo': vaga.titulo,
            'remuneracao': str(vaga.remuneracao),
            'tipo_remuneracao': vaga.tipo_remuneracao,
            'evento_nome': vaga.setor.evento.nome if vaga.setor and vaga.setor.evento else '',
            'setor_nome': vaga.setor.nome if vaga.setor else '',
        }
        
        # Montar payload FCM para múltiplos dispositivos
        payload = {
            "registration_ids": device_tokens,
            "notification": {
                "title": titulo,
                "body": mensagem,
                "sound": "default",
                "badge": "1",
                "icon": "ic_notification",
                "color": "#667eea"
            },
            "data": data_adicional,
            "priority": "high"
        }
        
        # Headers
        headers = {
            "Authorization": f"key={self.server_key}",
            "Content-Type": "application/json"
        }
        
        try:
            # Enviar requisição
            response = requests.post(
                self.FCM_URL,
                data=json.dumps(payload),
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                sucesso = result.get('success', 0)
                print(f"✓ Notificações enviadas: {sucesso}/{len(device_tokens)}")
                return sucesso
            else:
                print(f"✗ Erro HTTP {response.status_code}: {response.text}")
                return 0
                
        except Exception as e:
            print(f"✗ Exceção ao enviar notificações: {str(e)}")
            return 0
