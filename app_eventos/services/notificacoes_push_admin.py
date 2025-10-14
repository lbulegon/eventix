"""
Serviço de Notificações Push via Firebase Admin SDK (Recomendado)
"""
from firebase_admin import messaging
from .firebase_config import get_firebase_app


class NotificacaoPushAdminService:
    """
    Serviço para enviar notificações push via Firebase Admin SDK
    Mais seguro e recomendado que requisições HTTP diretas
    """
    
    def __init__(self):
        self.app = get_firebase_app()
    
    def enviar_notificacao_vaga(self, device_token, vaga):
        """
        Envia notificação sobre nova vaga para um freelancer
        """
        if not self.app:
            print("AVISO: Firebase não configurado")
            return False
        
        if not device_token:
            print("AVISO: Device token não fornecido")
            return False
        
        try:
            # Preparar mensagem
            titulo = "Nova Vaga Disponível!"
            corpo = f"{vaga.titulo} - R$ {vaga.remuneracao}"
            
            # Dados adicionais para o app
            data_adicional = {
                'vaga_id': str(vaga.id),
                'titulo': vaga.titulo,
                'remuneracao': str(vaga.remuneracao),
                'tipo_remuneracao': vaga.tipo_remuneracao,
                'evento_nome': vaga.setor.evento.nome if vaga.setor and vaga.setor.evento else '',
                'setor_nome': vaga.setor.nome if vaga.setor else '',
                'tipo': 'nova_vaga',
            }
            
            # Criar mensagem FCM
            message = messaging.Message(
                token=device_token,
                notification=messaging.Notification(
                    title=titulo,
                    body=corpo,
                ),
                data=data_adicional,
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        icon='ic_notification',
                        color='#667eea',
                        sound='default',
                    ),
                ),
                apns=messaging.APNSConfig(
                    headers={'apns-priority': '10'},
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            sound='default',
                            badge=1,
                            content_available=True,
                        ),
                    ),
                ),
            )
            
            # Enviar mensagem
            response = messaging.send(message)
            print(f"✓ Notificação enviada com sucesso: {response}")
            return True
            
        except Exception as e:
            print(f"✗ Erro ao enviar notificação: {str(e)}")
            # Se o token é inválido, retornar False para marcar como inativo
            if 'not-found' in str(e).lower() or 'invalid' in str(e).lower():
                return 'token_invalido'
            return False
    
    def enviar_notificacao_multipla(self, device_tokens, vaga):
        """
        Envia notificação para múltiplos dispositivos
        """
        if not self.app:
            print("AVISO: Firebase não configurado")
            return 0
        
        if not device_tokens or len(device_tokens) == 0:
            print("AVISO: Nenhum device token fornecido")
            return 0
        
        try:
            # Preparar mensagem
            titulo = "Nova Vaga Disponível!"
            corpo = f"{vaga.titulo} - R$ {vaga.remuneracao}"
            
            # Dados adicionais
            data_adicional = {
                'vaga_id': str(vaga.id),
                'titulo': vaga.titulo,
                'remuneracao': str(vaga.remuneracao),
                'tipo_remuneracao': vaga.tipo_remuneracao,
                'evento_nome': vaga.setor.evento.nome if vaga.setor and vaga.setor.evento else '',
                'setor_nome': vaga.setor.nome if vaga.setor else '',
                'tipo': 'nova_vaga',
            }
            
            # Criar mensagem multicast
            message = messaging.MulticastMessage(
                tokens=device_tokens,
                notification=messaging.Notification(
                    title=titulo,
                    body=corpo,
                ),
                data=data_adicional,
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        icon='ic_notification',
                        color='#667eea',
                        sound='default',
                    ),
                ),
                apns=messaging.APNSConfig(
                    headers={'apns-priority': '10'},
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            sound='default',
                            badge=1,
                            content_available=True,
                        ),
                    ),
                ),
            )
            
            # Enviar para múltiplos dispositivos
            response = messaging.send_multicast(message)
            
            print(f"✓ Notificações enviadas: {response.success_count}/{len(device_tokens)}")
            
            # Tratar tokens inválidos
            if response.failure_count > 0:
                for idx, result in enumerate(response.responses):
                    if not result.success:
                        print(f"✗ Falha no token {device_tokens[idx][:20]}...: {result.exception}")
            
            return response.success_count
            
        except Exception as e:
            print(f"✗ Erro ao enviar notificações: {str(e)}")
            return 0

