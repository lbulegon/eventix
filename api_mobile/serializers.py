# api_mobile/serializers.py
from rest_framework import serializers
from django.db import IntegrityError, transaction
from app_eventos.services.onboarding_freelance import FREELANCE_ONBOARDING_NIVEL2_WRITE_FIELDS
from app_eventos.utils_empresa_ativa import empresa_contexto_api
from app_eventos.models import (
    Vaga, Candidatura, Evento, Freelance, Empresa,
    EmpresaContratante, PlanoContratacao, SetorEvento, Funcao, LocalEvento, FreelancerFuncao,
    PontoOperacao, RegistroPresencaFreelancer,
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


class PontoOperacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PontoOperacao
        fields = [
            'id', 'nome', 'descricao', 'endereco', 'cidade', 'uf', 'cep',
            'local', 'dia_semana_fechamento', 'ativo', 'data_criacao', 'data_atualizacao'
        ]
        read_only_fields = ['data_criacao', 'data_atualizacao']


class VagaSerializer(serializers.ModelSerializer):
    funcao = FuncaoSerializer(read_only=True)
    funcao_id = serializers.PrimaryKeyRelatedField(
        source='funcao',
        queryset=Funcao.objects.all(),
        write_only=True,
        required=False,
    )
    setor = SetorEventoSerializer(read_only=True)
    setor_id = serializers.PrimaryKeyRelatedField(
        source='setor',
        queryset=SetorEvento.objects.select_related('evento', 'evento__empresa_contratante'),
        write_only=True,
        required=False,
    )
    ponto_operacao = PontoOperacaoSerializer(read_only=True)
    ponto_operacao_id = serializers.PrimaryKeyRelatedField(
        source='ponto_operacao',
        queryset=PontoOperacao.objects.select_related('empresa_contratante'),
        write_only=True,
        required=False,
    )
    empresa_contratante = EmpresaContratanteSerializer(read_only=True)
    empresa_contratante_id = serializers.PrimaryKeyRelatedField(
        source='empresa_contratante',
        queryset=EmpresaContratante.objects.all(),
        write_only=True,
        required=False,
    )
    evento_nome = serializers.SerializerMethodField()
    candidaturas_count = serializers.SerializerMethodField()
    remuneracao = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)
    
    class Meta:
        model = Vaga
        fields = [
            'id', 'titulo', 'funcao', 'funcao_id', 'setor', 'setor_id',
            'ponto_operacao', 'ponto_operacao_id',
            'empresa_contratante', 'empresa_contratante_id',
            'quantidade', 'remuneracao', 'descricao', 'ativa',
            'data_inicio_trabalho', 'data_limite_candidatura',
            'evento_nome', 'candidaturas_count'
        ]
    
    def get_evento_nome(self, obj):
        if obj.ponto_operacao:
            return obj.ponto_operacao.nome
        if obj.setor and obj.setor.evento:
            return obj.setor.evento.nome
        if obj.evento:
            return obj.evento.nome
        return None
    
    def get_candidaturas_count(self, obj):
        c = getattr(obj, '_candidaturas_count', None)
        if c is not None:
            return int(c)
        return obj.candidaturas.count()
    
    def validate(self, attrs):
        """
        Regras de criação/edição:
        - origem obrigatória: setor (evento) OU ponto_operacao;
        - função obrigatória (especialidade da vaga);
        - usuário de empresa não pode criar/editar vaga fora do próprio tenant;
        - função deve ser global ou da própria empresa.
        """
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        setor = attrs.get('setor', getattr(self.instance, 'setor', None))
        ponto = attrs.get('ponto_operacao', getattr(self.instance, 'ponto_operacao', None))
        funcao = attrs.get('funcao', getattr(self.instance, 'funcao', None))
        empresa_payload = attrs.get('empresa_contratante', getattr(self.instance, 'empresa_contratante', None))

        if not setor and not ponto:
            raise serializers.ValidationError(
                "Informe setor (vaga de evento) ou ponto_operacao (operação permanente)."
            )
        if setor and ponto:
            raise serializers.ValidationError(
                "Vaga deve pertencer a evento OU ponto de operação, não ambos."
            )
        if not funcao:
            raise serializers.ValidationError("Informe a função (especialidade) da vaga.")
        data_inicio = attrs.get('data_inicio_trabalho', getattr(self.instance, 'data_inicio_trabalho', None))
        if not data_inicio:
            raise serializers.ValidationError(
                "Informe data_inicio_trabalho (início do turno) para publicar a vaga."
            )
        # Mantém consistência: por padrão o prazo de candidatura acompanha o início do turno.
        if not attrs.get('data_limite_candidatura'):
            attrs['data_limite_candidatura'] = data_inicio

        empresa_user_id = None
        if user and getattr(user, 'is_empresa_user', False) and user.empresa_contratante_id:
            empresa_user_id = user.empresa_contratante_id
        elif user and getattr(user, 'is_gestor_grupo', False):
            ec = empresa_contexto_api(request) if request else None
            empresa_user_id = ec.id if ec else None

        if empresa_user_id:

            if setor and setor.evento.empresa_contratante_id != empresa_user_id:
                raise serializers.ValidationError("Setor informado não pertence à sua empresa.")
            if ponto and ponto.empresa_contratante_id != empresa_user_id:
                raise serializers.ValidationError("Ponto de operação informado não pertence à sua empresa.")
            if empresa_payload and empresa_payload.id != empresa_user_id:
                raise serializers.ValidationError("empresa_contratante não pode divergir da empresa do usuário.")
            if funcao.empresa_contratante_id and funcao.empresa_contratante_id != empresa_user_id:
                raise serializers.ValidationError("Função informada não está disponível para sua empresa.")

        # Mantém coerência entre origem e empresa quando vier no payload (caso admin).
        if empresa_payload:
            if setor and setor.evento.empresa_contratante_id != empresa_payload.id:
                raise serializers.ValidationError("empresa_contratante deve ser a mesma do evento/setor.")
            if ponto and ponto.empresa_contratante_id != empresa_payload.id:
                raise serializers.ValidationError("empresa_contratante deve ser a mesma do ponto de operação.")

        return attrs


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
            'usuario_email', 'usuario_username',
            'score_confiabilidade', 'faltas_com_aviso', 'faltas_sem_aviso',
            'bloqueado', 'data_ultimo_evento',
        ]
        read_only_fields = [
            'atualizado_em', 'cadastro_completo',
            'score_confiabilidade', 'faltas_com_aviso', 'faltas_sem_aviso',
            'bloqueado', 'data_ultimo_evento',
        ]


class FreelanceOnboardingNivel2Serializer(serializers.ModelSerializer):
    """
    Nível 2 = dados pessoais + endereço + notas; exclui bancário e arquivos.
    Reutiliza a lista única em app_eventos.services.onboarding_freelance.
    """

    class Meta:
        model = Freelance
        fields = list(FREELANCE_ONBOARDING_NIVEL2_WRITE_FIELDS)

    def validate_cpf(self, value):
        if not value or not str(value).strip():
            return value
        cpf = ''.join(ch for ch in str(value) if ch.isdigit())
        if not cpf:
            return value
        qs = Freelance.objects.filter(cpf=cpf)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('Já existe freelancer com este CPF.')
        return value


class RegistroPresencaFreelancerSerializer(serializers.ModelSerializer):
    """Leitura do histórico de presença (sem campo interno de idempotência)."""

    class Meta:
        model = RegistroPresencaFreelancer
        fields = [
            'id', 'empresa', 'data', 'status', 'observacao', 'created_at',
        ]
        read_only_fields = fields


class RegistroPresencaManualSerializer(serializers.Serializer):
    """Corpo do POST manual de presença/falta (empresa ou admin sistema)."""

    data = serializers.DateField()
    status = serializers.ChoiceField(choices=RegistroPresencaFreelancer.STATUS_CHOICES)
    observacao = serializers.CharField(required=False, allow_blank=True, default='')
    empresa_id = serializers.IntegerField(required=False, allow_null=True)


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

    def validate_email(self, value):
        email = value.strip().lower()
        if User.objects.filter(email__iexact=email).exists() or User.objects.filter(username__iexact=email).exists():
            raise serializers.ValidationError('Já existe uma conta com este e-mail.')
        return email

    def validate_cpf(self, value):
        cpf = ''.join(ch for ch in str(value) if ch.isdigit())
        if Freelance.objects.filter(cpf=cpf).exists():
            raise serializers.ValidationError('Já existe freelancer com este CPF.')
        return cpf
    
    def create(self, validated_data):
        email = validated_data.pop('email').strip().lower()
        password = validated_data.pop('password')

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    tipo_usuario='freelancer'
                )
                freelance = Freelance.objects.create(
                    usuario=user,
                    **validated_data
                )
                return freelance
        except IntegrityError:
            raise serializers.ValidationError(
                {'detail': 'Dados já cadastrados (e-mail ou CPF).'}
            )


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8)
