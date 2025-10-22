"""
Views para Integração Twilio (WhatsApp + SMS)
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.shortcuts import get_object_or_404

from app_eventos.models_twilio import UserContact, OtpLog, BroadcastLog, BroadcastMessage
from app_eventos.models import EmpresaContratante, Freelance, Vaga, Evento
from app_eventos.services.twilio_service import TwilioService


class VerifyStartView(APIView):
    """
    POST /api/v1/twilio/verify/start
    
    Inicia verificação de telefone (envia código OTP)
    """
    permission_classes = [AllowAny]  # Pode ser público para onboarding
    
    def post(self, request):
        phone_e164 = request.data.get('phone_e164')
        empresa_id = request.data.get('empresa_id')
        channel = request.data.get('channel', 'whatsapp')
        purpose = request.data.get('purpose', 'signup')
        
        # Validações
        if not phone_e164:
            return Response(
                {'error': 'phone_e164 é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not empresa_id:
            return Response(
                {'error': 'empresa_id é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Buscar empresa
        try:
            empresa = EmpresaContratante.objects.get(id=empresa_id)
        except EmpresaContratante.DoesNotExist:
            return Response(
                {'error': 'Empresa não encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Inicializar Twilio
        twilio = TwilioService()
        
        if not twilio.is_configured():
            return Response(
                {'error': 'Serviço Twilio não configurado'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # Enviar código
        verification = twilio.start_verify(phone_e164, channel=channel)
        
        if not verification:
            return Response(
                {'error': 'Falha ao enviar código'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Registrar no log
        OtpLog.objects.create(
            empresa_contratante=empresa,
            address=phone_e164,
            channel_type=channel,
            purpose=purpose,
            status='sent',
            provider_sid=verification.sid,
            meta={'twilio_status': verification.status}
        )
        
        return Response({
            'success': True,
            'message': f'Código enviado via {channel}',
            'channel': channel,
            'to': phone_e164,
            'sid': verification.sid
        }, status=status.HTTP_200_OK)


class VerifyCheckView(APIView):
    """
    POST /api/v1/twilio/verify/check
    
    Verifica código OTP
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        phone_e164 = request.data.get('phone_e164')
        code = request.data.get('code')
        empresa_id = request.data.get('empresa_id')
        channel = request.data.get('channel', 'whatsapp')
        
        # Validações
        if not phone_e164 or not code:
            return Response(
                {'error': 'phone_e164 e code são obrigatórios'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not empresa_id:
            return Response(
                {'error': 'empresa_id é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Buscar empresa
        try:
            empresa = EmpresaContratante.objects.get(id=empresa_id)
        except EmpresaContratante.DoesNotExist:
            return Response(
                {'error': 'Empresa não encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar código
        twilio = TwilioService()
        is_verified = twilio.check_verify(phone_e164, code, channel=channel)
        
        if is_verified:
            # Atualizar UserContact
            contact, created = UserContact.objects.update_or_create(
                empresa_contratante=empresa,
                address=phone_e164,
                channel_type=channel,
                defaults={
                    'is_verified': True,
                    'last_verified_at': timezone.now(),
                    'consent': True,
                    'consent_timestamp': timezone.now()
                }
            )
            
            # Atualizar OTP Log
            OtpLog.objects.filter(
                empresa_contratante=empresa,
                address=phone_e164,
                status='sent'
            ).update(
                status='verified',
                verified_timestamp=timezone.now()
            )
            
            return Response({
                'verified': True,
                'message': 'Telefone verificado com sucesso',
                'contact_id': contact.id
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'verified': False,
                'message': 'Código inválido ou expirado'
            }, status=status.HTTP_400_BAD_REQUEST)


class BroadcastView(APIView):
    """
    POST /api/v1/twilio/broadcast
    
    Envia mensagem em massa
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Apenas admins podem fazer broadcast
        if request.user.tipo_usuario not in ['admin_empresa', 'admin_sistema']:
            return Response(
                {'error': 'Permissão negada'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        empresa = request.user.empresa_contratante
        campaign_name = request.data.get('campaign_name')
        body = request.data.get('body')
        targets = request.data.get('targets', [])  # Lista de números
        preferred_channel = request.data.get('preferred_channel', 'whatsapp')
        evento_id = request.data.get('evento_id')
        
        # Validações
        if not campaign_name or not body or not targets:
            return Response(
                {'error': 'campaign_name, body e targets são obrigatórios'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Buscar evento (opcional)
        evento = None
        if evento_id:
            try:
                evento = Evento.objects.get(id=evento_id, empresa_contratante=empresa)
            except Evento.DoesNotExist:
                pass
        
        # Criar log de broadcast
        broadcast_log = BroadcastLog.objects.create(
            empresa_contratante=empresa,
            campaign_name=campaign_name,
            body_template=body,
            channel_preferred=preferred_channel,
            evento=evento,
            total_targets=len(targets),
            created_by=request.user
        )
        
        # Enviar mensagens
        twilio = TwilioService()
        results = twilio.send_broadcast(targets, body, preferred_channel, evento)
        
        # Atualizar estatísticas
        broadcast_log.sent = results['sent']
        broadcast_log.delivered = results['delivered']
        broadcast_log.failed = results['failed']
        broadcast_log.completed_at = timezone.now()
        broadcast_log.save()
        
        # Salvar mensagens individuais
        for result in results['results']:
            if result['success']:
                BroadcastMessage.objects.create(
                    broadcast=broadcast_log,
                    to_address=result['phone'],
                    channel_used=result['channel'],
                    message_sid=result['sid'],
                    status='sent'
                )
        
        return Response({
            'success': True,
            'broadcast_id': broadcast_log.id,
            'stats': {
                'total': results['total'],
                'sent': results['sent'],
                'failed': results['failed']
            }
        }, status=status.HTTP_200_OK)


class TwilioStatusWebhook(APIView):
    """
    POST /api/v1/twilio/status
    
    Webhook do Twilio para atualizar status de mensagens
    """
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def post(self, request):
        # TODO: Validar assinatura do Twilio (X-Twilio-Signature)
        
        message_sid = request.data.get('MessageSid') or request.data.get('SmsSid')
        message_status = request.data.get('MessageStatus') or request.data.get('SmsStatus')
        error_code = request.data.get('ErrorCode')
        error_message = request.data.get('ErrorMessage')
        
        if not message_sid:
            return Response({'error': 'MessageSid não fornecido'}, status=400)
        
        # Atualizar BroadcastMessage
        try:
            msg = BroadcastMessage.objects.get(message_sid=message_sid)
            msg.status = message_status
            
            if error_code:
                msg.error_code = error_code
                msg.error_message = error_message
                msg.failed_at = timezone.now()
            elif message_status == 'delivered':
                msg.delivered_at = timezone.now()
            
            msg.save()
            
            # Atualizar estatísticas do broadcast
            broadcast = msg.broadcast
            broadcast.delivered = broadcast.messages.filter(status='delivered').count()
            broadcast.failed = broadcast.messages.filter(status__in=['failed', 'undelivered']).count()
            broadcast.save()
            
        except BroadcastMessage.DoesNotExist:
            # Mensagem não encontrada, pode ser uma mensagem individual
            pass
        
        return Response({'ok': True}, status=200)


class NotificarFreelancersVagaView(APIView):
    """
    POST /api/v1/twilio/notificar-vaga
    
    Notifica freelancers sobre nova vaga via WhatsApp/SMS
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        vaga_id = request.data.get('vaga_id')
        
        if not vaga_id:
            return Response(
                {'error': 'vaga_id é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Buscar vaga
        try:
            vaga = Vaga.objects.select_related('funcao', 'setor__evento', 'empresa_contratante').get(id=vaga_id)
        except Vaga.DoesNotExist:
            return Response(
                {'error': 'Vaga não encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Buscar freelancers com a função da vaga e com telefone cadastrado
        if vaga.funcao:
            freelancers = Freelance.objects.filter(
                funcoes__funcao=vaga.funcao,
                cadastro_completo=True,
                telefone__isnull=False
            ).exclude(telefone='').distinct()
        else:
            freelancers = Freelance.objects.filter(
                cadastro_completo=True,
                telefone__isnull=False
            ).exclude(telefone='').distinct()
        
        # Enviar notificações
        twilio = TwilioService()
        evento = vaga.setor.evento if vaga.setor else vaga.evento
        notificados = 0
        erros = 0
        
        for freelancer in freelancers:
            phone_e164 = twilio.format_phone_e164(freelancer.telefone)
            
            if twilio.validate_phone_e164(phone_e164):
                result = twilio.send_vaga_notification(phone_e164, vaga, evento)
                if result['success']:
                    notificados += 1
                else:
                    erros += 1
        
        return Response({
            'success': True,
            'total_freelancers': freelancers.count(),
            'notificados': notificados,
            'erros': erros
        }, status=status.HTTP_200_OK)

