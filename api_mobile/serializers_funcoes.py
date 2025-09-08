# api_mobile/serializers_funcoes.py
from rest_framework import serializers
from app_eventos.models import Funcao, TipoFuncao

class TipoFuncaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoFuncao
        fields = ['id', 'nome', 'descricao', 'ativo']

class FuncaoSerializer(serializers.ModelSerializer):
    tipo_funcao = TipoFuncaoSerializer(read_only=True)
    
    class Meta:
        model = Funcao
        fields = ['id', 'nome', 'descricao', 'tipo_funcao', 'ativo']
        read_only_fields = ['id']

class FreelancerFuncaoSerializer(serializers.ModelSerializer):
    funcao = FuncaoSerializer(read_only=True)
    funcao_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = FreelancerFuncao
        fields = [
            'id', 'funcao', 'funcao_id', 'nivel', 
            'data_adicionada', 'ativo'
        ]
        read_only_fields = ['id', 'data_adicionada', 'freelancer']
    
    def validate_nivel(self, value):
        niveis_validos = ['iniciante', 'intermediario', 'avancado', 'expert']
        if value not in niveis_validos:
            raise serializers.ValidationError(
                f"Nível deve ser um dos seguintes: {', '.join(niveis_validos)}"
            )
        return value
    
    def validate_funcao_id(self, value):
        try:
            funcao = Funcao.objects.get(id=value, ativo=True)
        except Funcao.DoesNotExist:
            raise serializers.ValidationError("Função não encontrada ou inativa")
        return value
