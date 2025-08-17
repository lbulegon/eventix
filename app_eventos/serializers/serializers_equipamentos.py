from rest_framework import serializers
from app_eventos.models import (
    CategoriaEquipamento, Equipamento, EquipamentoSetor, ManutencaoEquipamento
)


class CategoriaEquipamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaEquipamento
        fields = '__all__'


class EquipamentoSerializer(serializers.ModelSerializer):
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)
    empresa_proprietaria_nome = serializers.CharField(source='empresa_proprietaria.nome', read_only=True)
    
    class Meta:
        model = Equipamento
        fields = [
            'id', 'empresa_proprietaria', 'empresa_proprietaria_nome', 'codigo_patrimonial', 'categoria', 'categoria_nome', 'descricao', 
            'especificacoes_tecnicas', 'marca', 'modelo', 'numero_serie',
            'data_aquisicao', 'valor_aquisicao', 'estado_conservacao',
            'foto', 'manual_instrucoes', 'ativo', 'criado_em', 'atualizado_em'
        ]
        read_only_fields = ['criado_em', 'atualizado_em']


class EquipamentoSetorSerializer(serializers.ModelSerializer):
    equipamento_codigo = serializers.CharField(source='equipamento.codigo_patrimonial', read_only=True)
    equipamento_categoria = serializers.CharField(source='equipamento.categoria.nome', read_only=True)
    equipamento_empresa = serializers.CharField(source='equipamento.empresa_proprietaria.nome', read_only=True)
    setor_nome = serializers.CharField(source='setor.nome', read_only=True)
    evento_nome = serializers.CharField(source='setor.evento.nome', read_only=True)
    evento_empresa = serializers.CharField(source='setor.evento.empresa_contratante.nome', read_only=True)
    responsavel_nome = serializers.CharField(source='responsavel_equipamento.nome_completo', read_only=True)
    
    class Meta:
        model = EquipamentoSetor
        fields = [
            'id', 'setor', 'equipamento', 'equipamento_codigo', 'equipamento_categoria', 'equipamento_empresa',
            'setor_nome', 'evento_nome', 'evento_empresa', 'quantidade_necessaria', 'quantidade_disponivel',
            'quantidade_faltante', 'percentual_cobertura', 'observacoes',
            'data_inicio_uso', 'data_fim_uso', 'responsavel_equipamento',
            'responsavel_nome', 'status', 'criado_em', 'atualizado_em'
        ]
        read_only_fields = ['quantidade_faltante', 'percentual_cobertura', 'criado_em', 'atualizado_em']


class ManutencaoEquipamentoSerializer(serializers.ModelSerializer):
    equipamento_codigo = serializers.CharField(source='equipamento.codigo_patrimonial', read_only=True)
    responsavel_nome = serializers.CharField(source='responsavel.nome_completo', read_only=True)
    
    class Meta:
        model = ManutencaoEquipamento
        fields = [
            'id', 'equipamento', 'equipamento_codigo', 'tipo_manutencao',
            'descricao', 'data_inicio', 'data_fim', 'custo', 'fornecedor',
            'responsavel', 'responsavel_nome', 'status', 'observacoes', 'criado_em'
        ]
        read_only_fields = ['criado_em']


class EquipamentoSetorCreateSerializer(serializers.ModelSerializer):
    """
    Serializer específico para criação de equipamentos em setores
    """
    class Meta:
        model = EquipamentoSetor
        fields = [
            'setor', 'equipamento', 'quantidade_necessaria', 'quantidade_disponivel',
            'observacoes', 'data_inicio_uso', 'data_fim_uso', 'responsavel_equipamento', 'status'
        ]


class EquipamentoSetorUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer específico para atualização de equipamentos em setores
    """
    class Meta:
        model = EquipamentoSetor
        fields = [
            'quantidade_necessaria', 'quantidade_disponivel', 'observacoes',
            'data_inicio_uso', 'data_fim_uso', 'responsavel_equipamento', 'status'
        ]
