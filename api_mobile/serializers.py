# api_mobile/serializers.py
from rest_framework import serializers
from app_eventos.models import (
    Vaga, Candidatura, Evento, Freelance, Empresa, 
    EmpresaContratante, PlanoContratacao, SetorEvento, Funcao, LocalEvento, FreelancerFuncao
)
from django.contrib.auth import get_user_model

User = get_user_model()


class FuncaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Funcao
        fields = ['id', 'nome', 'descricao', 'tipo_funcao']


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


class SetorEventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SetorEvento
        fields = ['id', 'nome', 'descricao', 'evento']


class LocalEventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalEvento
        fields = ['id', 'nome', 'endereco', 'capacidade', 'descricao', 'ativo']


class PlanoContratacaoSerializer(serializers.ModelSerializer):
    """Serializer para dados do plano de contratação"""
    class Meta:
        model = PlanoContratacao
        fields = [
            'id', 'nome', 'tipo_plano', 'descricao',
            'max_eventos_mes', 'max_usuarios', 'max_freelancers', 
            'max_equipamentos', 'max_locais',
            'suporte_24h', 'relatorios_avancados', 'integracao_api',
            'backup_automatico', 'ssl_certificado', 'dominio_personalizado',
            'valor_mensal', 'valor_anual', 'desconto_anual'
        ]


class EmpresaContratanteSerializer(serializers.ModelSerializer):
    plano_contratado_fk = PlanoContratacaoSerializer(read_only=True)
    plano_contratado_fk_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = EmpresaContratante
        fields = [
            'id', 'nome', 'cnpj', 'razao_social', 'nome_fantasia',
            'telefone', 'email', 'website',
            'cep', 'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'uf',
            'data_contratacao', 'data_vencimento', 'plano_contratado', 'plano_contratado_fk', 'plano_contratado_fk_id',
            'valor_mensal', 'ativo', 'data_atualizacao'
        ]
        read_only_fields = ['data_contratacao', 'data_atualizacao']


class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = [
            'id', 'nome', 'cnpj', 'tipo_empresa', 'telefone', 'email', 'ativo'
        ]


class EventoSerializer(serializers.ModelSerializer):
    local = LocalEventoSerializer(read_only=True)
    local_id = serializers.IntegerField(write_only=True)
    empresa_contratante = EmpresaContratanteSerializer(read_only=True)
    empresa_contratante_id = serializers.IntegerField(write_only=True)
    empresa_produtora = EmpresaSerializer(read_only=True)
    empresa_produtora_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Evento
        fields = [
            'id', 'nome', 'descricao', 'data_inicio', 'data_fim',
            'local', 'local_id', 'empresa_contratante', 'empresa_contratante_id',
            'empresa_produtora', 'empresa_produtora_id', 'ativo', 'data_criacao'
        ]
        read_only_fields = ['data_criacao']


class VagaSerializer(serializers.ModelSerializer):
    funcao = FuncaoSerializer(read_only=True)
    funcao_id = serializers.IntegerField(write_only=True)
    setor = SetorEventoSerializer(read_only=True)
    setor_id = serializers.IntegerField(write_only=True)
    empresa_contratante = EmpresaContratanteSerializer(read_only=True)
    empresa_contratante_id = serializers.IntegerField(write_only=True)
    evento_nome = serializers.CharField(source='setor.evento.nome', read_only=True)
    candidaturas_count = serializers.SerializerMethodField()
    remuneracao = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)
    
    class Meta:
        model = Vaga
        fields = [
            'id', 'titulo', 'funcao', 'funcao_id', 'setor', 'setor_id',
            'empresa_contratante', 'empresa_contratante_id',
            'quantidade', 'remuneracao', 'descricao', 'ativa',
            'evento_nome', 'candidaturas_count'
        ]
    
    def get_candidaturas_count(self, obj):
        return obj.candidaturas.count()


class CandidaturaSerializer(serializers.ModelSerializer):
    vaga = VagaSerializer(read_only=True)
    vaga_id = serializers.IntegerField(write_only=True)
    freelance_nome = serializers.CharField(source='freelance.nome_completo', read_only=True)
    freelance_telefone = serializers.CharField(source='freelance.telefone', read_only=True)
    
    class Meta:
        model = Candidatura
        fields = [
            'id', 'vaga', 'vaga_id', 'freelance_nome', 'freelance_telefone',
            'data_candidatura', 'status'
        ]
        read_only_fields = ['data_candidatura']


class FreelanceSerializer(serializers.ModelSerializer):
    usuario_email = serializers.CharField(source='usuario.email', read_only=True)
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)
    
    class Meta:
        model = Freelance
        fields = [
            'id', 'nome_completo', 'telefone', 'documento', 'habilidades',
            'cpf', 'rg', 'data_nascimento', 'sexo', 'estado_civil',
            'cep', 'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'uf',
            'banco', 'agencia', 'conta', 'tipo_conta', 'chave_pix',
            'observacoes', 'cadastro_completo', 'atualizado_em',
            'usuario_email', 'usuario_username'
        ]
        read_only_fields = ['atualizado_em', 'cadastro_completo']


class UserProfileSerializer(serializers.ModelSerializer):
    freelance = FreelanceSerializer(read_only=True)
    empresa_contratante = EmpresaContratanteSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'tipo_usuario', 'ativo', 'data_ultimo_acesso',
            'freelance', 'empresa_contratante'
        ]
        read_only_fields = ['id', 'data_ultimo_acesso']


class PreCadastroFreelancerSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = Freelance
        fields = [
            'nome_completo', 'telefone', 'cpf', 'email', 'password',
            'data_nascimento', 'sexo', 'habilidades'
        ]
    
    def create(self, validated_data):
        # Criar usuário
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            tipo_usuario='freelancer'
        )
        
        # Criar perfil freelancer
        freelance = Freelance.objects.create(
            usuario=user,
            **validated_data
        )
        
        return freelance


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8)
