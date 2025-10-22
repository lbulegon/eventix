"""
Serializers para Sistema Twilio
"""
from rest_framework import serializers
from app_eventos.models_twilio import UserContact, OtpLog, BroadcastLog, BroadcastMessage


class UserContactSerializer(serializers.ModelSerializer):
    """Serializer para UserContact"""
    
    class Meta:
        model = UserContact
        fields = [
            'id', 'channel_type', 'address', 'consent', 
            'is_verified', 'last_verified_at', 'ativo', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class OtpLogSerializer(serializers.ModelSerializer):
    """Serializer para OtpLog"""
    
    class Meta:
        model = OtpLog
        fields = [
            'id', 'address', 'channel_type', 'purpose', 
            'status', 'sent_timestamp', 'verified_timestamp', 
            'provider_sid'
        ]
        read_only_fields = ['id']


class BroadcastMessageSerializer(serializers.ModelSerializer):
    """Serializer para BroadcastMessage"""
    
    class Meta:
        model = BroadcastMessage
        fields = [
            'id', 'to_address', 'channel_used', 'status', 
            'message_sid', 'error_code', 'error_message',
            'sent_at', 'delivered_at', 'failed_at'
        ]


class BroadcastLogSerializer(serializers.ModelSerializer):
    """Serializer para BroadcastLog"""
    messages = BroadcastMessageSerializer(many=True, read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    evento_nome = serializers.CharField(source='evento.nome', read_only=True)
    success_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = BroadcastLog
        fields = [
            'id', 'campaign_name', 'body_template', 'channel_preferred',
            'evento', 'evento_nome', 'total_targets', 'sent', 'delivered', 
            'failed', 'success_rate', 'created_by_username', 'created_at', 
            'completed_at', 'messages'
        ]
        read_only_fields = ['id', 'created_at']


# Serializers para Requests

class VerifyStartRequestSerializer(serializers.Serializer):
    """Serializer para request de /verify/start"""
    phone_e164 = serializers.CharField(max_length=20, help_text="+5511999999999")
    empresa_id = serializers.IntegerField()
    channel = serializers.ChoiceField(choices=['whatsapp', 'sms'], default='whatsapp')
    purpose = serializers.ChoiceField(
        choices=['signup', 'login', 'password_reset', 'phone_verification'],
        default='signup'
    )


class VerifyCheckRequestSerializer(serializers.Serializer):
    """Serializer para request de /verify/check"""
    phone_e164 = serializers.CharField(max_length=20)
    code = serializers.CharField(max_length=10)
    empresa_id = serializers.IntegerField()
    channel = serializers.ChoiceField(choices=['whatsapp', 'sms'], default='whatsapp')


class BroadcastRequestSerializer(serializers.Serializer):
    """Serializer para request de /broadcast"""
    campaign_name = serializers.CharField(max_length=200)
    body = serializers.CharField()
    targets = serializers.ListField(
        child=serializers.CharField(max_length=20),
        help_text="Lista de números no formato E.164"
    )
    preferred_channel = serializers.ChoiceField(choices=['whatsapp', 'sms'], default='whatsapp')
    evento_id = serializers.IntegerField(required=False, allow_null=True)

