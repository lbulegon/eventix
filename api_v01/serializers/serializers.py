# api_v01/serializers/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from app_eventos.models import (
    EmpresaContratante, Freelance, Vaga, Candidatura, ContratoFreelance,
    CategoriaFinanceira, DespesaEvento, ReceitaEvento, Fornecedor
)

User = get_user_model()


class VagaSerializer(serializers.ModelSerializer):
    evento = serializers.CharField(source="setor.evento.nome", read_only=True)
    empresa = serializers.CharField(source="setor.evento.empresa_contratante.nome_fantasia", read_only=True)

    class Meta:
        model = Vaga
        fields = ["id", "titulo", "descricao", "quantidade", "remuneracao", "ativa", "evento", "empresa"]


class CandidaturaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidatura
        fields = ["id", "vaga"]

    def create(self, validated_data):
        request = self.context["request"]
        freelance = Freelance.objects.get(usuario=request.user)
        return Candidatura.objects.create(freelance=freelance, **validated_data)


class CandidaturaListSerializer(serializers.ModelSerializer):
    vaga = VagaSerializer(read_only=True)

    class Meta:
        model = Candidatura
        fields = ["id", "vaga", "status", "data_candidatura"]


class ContratoFreelanceSerializer(serializers.ModelSerializer):
    vaga = VagaSerializer(read_only=True)

    class Meta:
        model = ContratoFreelance
        fields = ["id", "vaga", "status", "data_contratacao"]


class LoginSerializer(serializers.Serializer):
    """Serializer para login único"""
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)


class UserRegistrationSerializer(serializers.Serializer):
    """Serializer para registro de usuário"""
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    
    # Tipo de usuário
    tipo_usuario = serializers.ChoiceField(
        choices=User.TIPO_USUARIO_CHOICES,
        default='freelancer'
    )
    
    # ID da empresa (para usuários de empresa)
    empresa_id = serializers.IntegerField(required=False, allow_null=True)
    
    # Campos específicos para freelancer
    nome_completo = serializers.CharField(max_length=255, required=False)
    telefone = serializers.CharField(max_length=20, required=False)
    cpf = serializers.CharField(max_length=14, required=False)
    
    def validate(self, data):
        # Verifica se as senhas coincidem
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("As senhas não coincidem.")
        
        # Verifica se o username já existe
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError("Este nome de usuário já está em uso.")
        
        # Verifica se o email já existe
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("Este email já está em uso.")
        
        # Validações específicas por tipo de usuário
        tipo_usuario = data.get('tipo_usuario', 'freelancer')
        empresa_id = data.get('empresa_id')
        
        # Se é usuário de empresa, verifica se a empresa existe e está ativa
        if tipo_usuario in ['admin_empresa', 'operador_empresa']:
            if not empresa_id:
                raise serializers.ValidationError("Empresa é obrigatória para usuários de empresa.")
            
            try:
                empresa = EmpresaContratante.objects.get(id=empresa_id)
                if not empresa.ativo:
                    raise serializers.ValidationError("A empresa selecionada está inativa.")
            except EmpresaContratante.DoesNotExist:
                raise serializers.ValidationError("Empresa não encontrada.")
        
        # Se é freelancer, verifica se os campos obrigatórios estão presentes
        if tipo_usuario == 'freelancer':
            if not data.get('nome_completo'):
                raise serializers.ValidationError("Nome completo é obrigatório para freelancers.")
        
        return data


class EmpresaRegistrationSerializer(serializers.Serializer):
    """Serializer para registro de empresa"""
    usuario = UserRegistrationSerializer()
    empresa = serializers.DictField()
    
    def validate_empresa(self, value):
        """Valida os dados da empresa"""
        required_fields = ['nome_fantasia', 'cnpj', 'email']
        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(f"Campo '{field}' é obrigatório para a empresa.")
        
        # Verifica se o CNPJ já existe
        if EmpresaContratante.objects.filter(cnpj=value['cnpj']).exists():
            raise serializers.ValidationError("Este CNPJ já está cadastrado.")
        
        return value


class RegistroUnicoSerializer(serializers.Serializer):
    """Serializer para registro único de qualquer tipo de usuário"""
    # Dados básicos do usuário
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    
    # Tipo de usuário
    tipo_usuario = serializers.ChoiceField(
        choices=User.TIPO_USUARIO_CHOICES,
        default='freelancer'
    )
    
    # ID da empresa (para usuários de empresa)
    empresa_id = serializers.IntegerField(required=False, allow_null=True)
    
    # Dados da empresa (se for criar uma nova empresa)
    empresa_nova = serializers.DictField(required=False)
    
    # Campos específicos para freelancer
    nome_completo = serializers.CharField(max_length=255, required=False)
    telefone = serializers.CharField(max_length=20, required=False)
    cpf = serializers.CharField(max_length=14, required=False)
    
    def validate(self, data):
        # Verifica se as senhas coincidem
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("As senhas não coincidem.")
        
        # Verifica se o username já existe
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError("Este nome de usuário já está em uso.")
        
        # Verifica se o email já existe
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("Este email já está em uso.")
        
        tipo_usuario = data.get('tipo_usuario', 'freelancer')
        empresa_id = data.get('empresa_id')
        empresa_nova = data.get('empresa_nova')
        
        # Validações específicas por tipo de usuário
        if tipo_usuario in ['admin_empresa', 'operador_empresa']:
            # Se não tem empresa_id, deve ter empresa_nova
            if not empresa_id and not empresa_nova:
                raise serializers.ValidationError("Para usuários de empresa, deve fornecer empresa_id ou dados de nova empresa.")
            
            # Se tem empresa_id, verifica se existe e está ativa
            if empresa_id:
                try:
                    empresa = EmpresaContratante.objects.get(id=empresa_id)
                    if not empresa.ativo:
                        raise serializers.ValidationError("A empresa selecionada está inativa.")
                except EmpresaContratante.DoesNotExist:
                    raise serializers.ValidationError("Empresa não encontrada.")
            
            # Se tem empresa_nova, valida os dados
            if empresa_nova:
                required_fields = ['nome_fantasia', 'cnpj', 'email']
                for field in required_fields:
                    if field not in empresa_nova:
                        raise serializers.ValidationError(f"Campo '{field}' é obrigatório para a empresa.")
                
                # Verifica se o CNPJ já existe
                if EmpresaContratante.objects.filter(cnpj=empresa_nova['cnpj']).exists():
                    raise serializers.ValidationError("Este CNPJ já está cadastrado.")
        
        # Se é freelancer, verifica se os campos obrigatórios estão presentes
        if tipo_usuario == 'freelancer':
            if not data.get('nome_completo'):
                raise serializers.ValidationError("Nome completo é obrigatório para freelancers.")
            
            # Para freelancers, verifica se a Eventix existe
            try:
                eventix = EmpresaContratante.objects.filter(nome_fantasia__icontains='Eventix').first()
                if not eventix:
                    raise serializers.ValidationError("Empresa Eventix não encontrada no sistema.")
                if not eventix.ativo:
                    raise serializers.ValidationError("Empresa Eventix está inativa.")
            except Exception:
                raise serializers.ValidationError("Erro ao verificar empresa Eventix.")
        
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer para perfil do usuário"""
    tipo_usuario_display = serializers.CharField(source='get_user_type_display_name', read_only=True)
    is_freelancer = serializers.BooleanField(read_only=True)
    is_empresa_user = serializers.BooleanField(read_only=True)
    is_admin_sistema = serializers.BooleanField(read_only=True)
    dashboard_url = serializers.CharField(source='get_dashboard_url', read_only=True)
    empresa_contratante_nome = serializers.CharField(source='empresa_contratante.nome_fantasia', read_only=True)
    empresa_owner_nome = serializers.CharField(source='empresa_owner.nome_fantasia', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'tipo_usuario', 'tipo_usuario_display', 'ativo',
            'is_freelancer', 'is_empresa_user', 'is_admin_sistema',
            'empresa_contratante_nome', 'empresa_owner_nome', 'dashboard_url',
            'data_ultimo_acesso', 'date_joined'
        ]
        read_only_fields = ['id', 'date_joined', 'data_ultimo_acesso']


class FreelanceProfileSerializer(serializers.ModelSerializer):
    """Serializer para perfil de freelancer"""
    usuario = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = Freelance
        fields = [
            'id', 'usuario', 'nome_completo', 'telefone', 'cpf',
            'cadastro_completo', 'atualizado_em'
        ]
        read_only_fields = ['id', 'cadastro_completo', 'atualizado_em']


class EmpresaProfileSerializer(serializers.ModelSerializer):
    """Serializer para perfil de empresa"""
    usuarios = UserProfileSerializer(many=True, read_only=True)
    
    class Meta:
        model = EmpresaContratante
        fields = [
            'id', 'nome_fantasia', 'razao_social', 'cnpj',
            'telefone', 'email', 'website', 'ativo',
            'data_contratacao', 'data_vencimento',
            'plano_contratado', 'valor_mensal', 'usuarios'
        ]
        read_only_fields = ['id', 'data_contratacao', 'data_atualizacao']


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer para alteração de senha"""
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, data):
        user = self.context['request'].user
        
        # Verifica se a senha atual está correta
        if not user.check_password(data['current_password']):
            raise serializers.ValidationError("Senha atual incorreta.")
        
        # Verifica se as novas senhas coincidem
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError("As novas senhas não coincidem.")
        
        return data


class UpdateProfileSerializer(serializers.ModelSerializer):
    """Serializer para atualização de perfil"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
    
    def validate_email(self, value):
        user = self.context['request'].user
        if User.objects.exclude(id=user.id).filter(email=value).exists():
            raise serializers.ValidationError("Este email já está em uso.")
        return value


# Serializers para o sistema financeiro
class CategoriaFinanceiraSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaFinanceira
        fields = [
            'id', 'nome', 'descricao', 'tipo', 'cor', 'ativo'
        ]


class DespesaEventoSerializer(serializers.ModelSerializer):
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)
    evento_nome = serializers.CharField(source='evento.nome', read_only=True)
    atrasada = serializers.BooleanField(read_only=True)
    dias_atraso = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = DespesaEvento
        fields = [
            'id', 'evento', 'evento_nome', 'categoria', 'categoria_nome',
            'descricao', 'valor', 'data_vencimento', 'data_pagamento',
            'fornecedor', 'numero_documento', 'status', 'observacoes',
            'atrasada', 'dias_atraso', 'data_criacao', 'data_atualizacao'
        ]
        read_only_fields = ['data_criacao', 'data_atualizacao']


class ReceitaEventoSerializer(serializers.ModelSerializer):
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)
    evento_nome = serializers.CharField(source='evento.nome', read_only=True)
    atrasada = serializers.BooleanField(read_only=True)
    dias_atraso = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = ReceitaEvento
        fields = [
            'id', 'evento', 'evento_nome', 'categoria', 'categoria_nome',
            'descricao', 'valor', 'data_vencimento', 'data_recebimento',
            'cliente', 'numero_documento', 'status', 'observacoes',
            'atrasada', 'dias_atraso', 'data_criacao', 'data_atualizacao'
        ]
        read_only_fields = ['data_criacao', 'data_atualizacao']


class FluxoCaixaEventoSerializer(serializers.Serializer):
    """Serializer para resumo do fluxo de caixa de um evento"""
    evento_id = serializers.IntegerField()
    evento_nome = serializers.CharField()
    total_despesas = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_receitas = serializers.DecimalField(max_digits=10, decimal_places=2)
    saldo_financeiro = serializers.DecimalField(max_digits=10, decimal_places=2)
    despesas_pagas = serializers.DecimalField(max_digits=10, decimal_places=2)
    receitas_recebidas = serializers.DecimalField(max_digits=10, decimal_places=2)
    saldo_realizado = serializers.DecimalField(max_digits=10, decimal_places=2)
    despesas_pendentes = serializers.DecimalField(max_digits=10, decimal_places=2)
    receitas_pendentes = serializers.DecimalField(max_digits=10, decimal_places=2)
    despesas_atrasadas_count = serializers.IntegerField()
    receitas_atrasadas_count = serializers.IntegerField()


# Serializers para Fornecedores
class FornecedorSerializer(serializers.ModelSerializer):
    endereco_completo = serializers.CharField(read_only=True)
    total_despesas = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    despesas_pagas = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    despesas_pendentes = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Fornecedor
        fields = [
            'id', 'nome_fantasia', 'razao_social', 'cnpj', 'tipo_fornecedor',
            'telefone', 'email', 'website', 'endereco_completo',
            'cep', 'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'uf',
            'banco', 'agencia', 'conta', 'pix', 'observacoes', 'ativo',
            'data_cadastro', 'data_atualizacao',
            'total_despesas', 'despesas_pagas', 'despesas_pendentes'
        ]
        read_only_fields = ['data_cadastro', 'data_atualizacao']


class FornecedorCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fornecedor
        fields = [
            'nome_fantasia', 'razao_social', 'cnpj', 'tipo_fornecedor',
            'telefone', 'email', 'website',
            'cep', 'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'uf',
            'banco', 'agencia', 'conta', 'pix', 'observacoes', 'ativo'
        ]
    
    def create(self, validated_data):
        # Associar automaticamente à empresa do usuário
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['empresa_contratante'] = request.user.empresa_owner
        return super().create(validated_data)


class FornecedorUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fornecedor
        fields = [
            'nome_fantasia', 'razao_social', 'cnpj', 'tipo_fornecedor',
            'telefone', 'email', 'website',
            'cep', 'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'uf',
            'banco', 'agencia', 'conta', 'pix', 'observacoes', 'ativo'
        ]
