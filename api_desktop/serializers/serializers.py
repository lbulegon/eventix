# api_desktop/serializers/serializers.py
from rest_framework import serializers
from app_eventos.models import (
    User, EmpresaContratante, Evento, Freelance, Vaga, 
    Candidatura, Equipamento, DespesaEvento, ReceitaEvento
)


class UsuarioDesktopSerializer(serializers.ModelSerializer):
    """Serializer para usuários no desktop"""
    empresa_nome = serializers.CharField(source='empresa_contratante.nome_fantasia', read_only=True)
    tipo_usuario_display = serializers.CharField(source='get_user_type_display_name', read_only=True)
    grupos = serializers.SerializerMethodField()
    permissoes = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'tipo_usuario', 'tipo_usuario_display', 'empresa_contratante',
            'empresa_nome', 'ativo', 'date_joined', 'last_login',
            'grupos', 'permissoes'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']
    
    def get_grupos(self, obj):
        """Retorna os grupos do usuário"""
        return [{
            'id': ug.grupo.id,
            'nome': ug.grupo.nome,
            'tipo': ug.grupo.tipo_grupo,
            'empresa': ug.grupo.empresa_contratante.nome_fantasia if ug.grupo.empresa_contratante else None,
        } for ug in obj.get_grupos_ativos()]
    
    def get_permissoes(self, obj):
        """Retorna as permissões do usuário"""
        return obj.get_permissoes()


class EmpresaDesktopSerializer(serializers.ModelSerializer):
    """Serializer para empresas no desktop"""
    total_usuarios = serializers.SerializerMethodField()
    total_eventos = serializers.SerializerMethodField()
    status_contrato = serializers.SerializerMethodField()
    
    class Meta:
        model = EmpresaContratante
        fields = [
            'id', 'nome', 'nome_fantasia', 'cnpj', 'email',
            'telefone', 'plano_contratado', 'valor_mensal',
            'data_contratacao', 'data_vencimento', 'ativo',
            'total_usuarios', 'total_eventos', 'status_contrato'
        ]
        read_only_fields = ['id', 'data_contratacao']
    
    def get_total_usuarios(self, obj):
        """Retorna o total de usuários da empresa"""
        return obj.usuarios.count()
    
    def get_total_eventos(self, obj):
        """Retorna o total de eventos da empresa"""
        return Evento.objects.filter(empresa_contratante=obj).count()
    
    def get_status_contrato(self, obj):
        """Retorna o status do contrato"""
        from django.utils import timezone
        if obj.data_vencimento < timezone.now().date():
            return 'vencido'
        elif obj.data_vencimento <= timezone.now().date() + timezone.timedelta(days=30):
            return 'vencendo'
        else:
            return 'ativo'


class EventoDesktopSerializer(serializers.ModelSerializer):
    """Serializer para eventos no desktop"""
    empresa_nome = serializers.CharField(source='empresa_contratante.nome_fantasia', read_only=True)
    total_vagas = serializers.SerializerMethodField()
    total_candidaturas = serializers.SerializerMethodField()
    status_evento = serializers.SerializerMethodField()
    
    class Meta:
        model = Evento
        fields = [
            'id', 'nome', 'descricao', 'data_inicio', 'data_fim',
            'empresa_contratante', 'empresa_nome', 'local',
            'ativo', 'total_vagas', 'total_candidaturas', 'status_evento'
        ]
        read_only_fields = ['id']
    
    def get_total_vagas(self, obj):
        """Retorna o total de vagas do evento"""
        return Vaga.objects.filter(setor__evento=obj).count()
    
    def get_total_candidaturas(self, obj):
        """Retorna o total de candidaturas do evento"""
        return Candidatura.objects.filter(vaga__setor__evento=obj).count()
    
    def get_status_evento(self, obj):
        """Retorna o status do evento"""
        from django.utils import timezone
        now = timezone.now()
        
        if obj.data_inicio > now:
            return 'agendado'
        elif obj.data_inicio <= now <= obj.data_fim:
            return 'em_andamento'
        else:
            return 'finalizado'


class FreelancerDesktopSerializer(serializers.ModelSerializer):
    """Serializer para freelancers no desktop"""
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)
    usuario_email = serializers.EmailField(source='usuario.email', read_only=True)
    total_candidaturas = serializers.SerializerMethodField()
    candidaturas_aprovadas = serializers.SerializerMethodField()
    
    class Meta:
        model = Freelance
        fields = [
            'id', 'usuario', 'usuario_username', 'usuario_email',
            'nome_completo', 'cpf', 'telefone', 'sexo',
            'data_nascimento', 'cadastro_completo', 'atualizado_em',
            'total_candidaturas', 'candidaturas_aprovadas'
        ]
        read_only_fields = ['id', 'atualizado_em']
    
    def get_total_candidaturas(self, obj):
        """Retorna o total de candidaturas do freelancer"""
        return Candidatura.objects.filter(freelance=obj).count()
    
    def get_candidaturas_aprovadas(self, obj):
        """Retorna o total de candidaturas aprovadas"""
        return Candidatura.objects.filter(freelance=obj, status='aprovado').count()


class VagaDesktopSerializer(serializers.ModelSerializer):
    """Serializer para vagas no desktop"""
    evento_nome = serializers.CharField(source='setor.evento.nome', read_only=True)
    empresa_nome = serializers.CharField(source='setor.evento.empresa_contratante.nome_fantasia', read_only=True)
    total_candidaturas = serializers.SerializerMethodField()
    candidaturas_aprovadas = serializers.SerializerMethodField()
    
    class Meta:
        model = Vaga
        fields = [
            'id', 'titulo', 'descricao', 'quantidade', 'remuneracao',
            'setor', 'evento_nome', 'empresa_nome', 'ativa',
            'total_candidaturas', 'candidaturas_aprovadas'
        ]
        read_only_fields = ['id']
    
    def get_total_candidaturas(self, obj):
        """Retorna o total de candidaturas para a vaga"""
        return Candidatura.objects.filter(vaga=obj).count()
    
    def get_candidaturas_aprovadas(self, obj):
        """Retorna o total de candidaturas aprovadas"""
        return Candidatura.objects.filter(vaga=obj, status='aprovado').count()


class EquipamentoDesktopSerializer(serializers.ModelSerializer):
    """Serializer para equipamentos no desktop"""
    empresa_proprietaria_nome = serializers.CharField(source='empresa_proprietaria.nome', read_only=True)
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)
    
    class Meta:
        model = Equipamento
        fields = [
            'id', 'codigo_patrimonial', 'categoria', 'categoria_nome',
            'descricao', 'marca', 'modelo', 'numero_serie',
            'estado_conservacao', 'empresa_proprietaria', 'empresa_proprietaria_nome',
            'data_aquisicao', 'valor_aquisicao', 'ativo'
        ]
        read_only_fields = ['id']


class CandidaturaDesktopSerializer(serializers.ModelSerializer):
    """Serializer para candidaturas no desktop"""
    freelance_nome = serializers.CharField(source='freelance.nome_completo', read_only=True)
    vaga_titulo = serializers.CharField(source='vaga.titulo', read_only=True)
    evento_nome = serializers.CharField(source='vaga.setor.evento.nome', read_only=True)
    empresa_nome = serializers.CharField(source='vaga.setor.evento.empresa_contratante.nome_fantasia', read_only=True)
    
    class Meta:
        model = Candidatura
        fields = [
            'id', 'freelance', 'freelance_nome', 'vaga', 'vaga_titulo',
            'evento_nome', 'empresa_nome', 'status', 'data_candidatura',
            'observacoes'
        ]
        read_only_fields = ['id', 'data_candidatura']


class DashboardDesktopSerializer(serializers.Serializer):
    """Serializer para dados do dashboard desktop"""
    usuario = UsuarioDesktopSerializer(read_only=True)
    estatisticas = serializers.DictField(read_only=True)
    alertas = serializers.ListField(read_only=True)
    atividades_recentes = serializers.ListField(read_only=True)


class EstatisticasDesktopSerializer(serializers.Serializer):
    """Serializer para estatísticas do desktop"""
    periodo = serializers.IntegerField()
    dados = serializers.DictField()


class ConfiguracoesDesktopSerializer(serializers.Serializer):
    """Serializer para configurações do desktop"""
    usuario = serializers.DictField()
    sistema = serializers.DictField()
    preferencias = serializers.DictField()
