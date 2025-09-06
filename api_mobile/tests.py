# api_mobile/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from app_eventos.models import (
    Vaga, Candidatura, Evento, Freelance, EmpresaContratante,
    SetorEvento, Funcao, LocalEvento, TipoFuncao, Empresa
)

User = get_user_model()


class VagaAPITestCase(APITestCase):
    def setUp(self):
        # Criar empresa contratante
        self.empresa = EmpresaContratante.objects.create(
            nome_fantasia="Empresa Teste",
            cnpj="12345678000199",
            email="teste@empresa.com",
            data_vencimento="2025-12-31",
            plano_contratado="Premium",
            valor_mensal=500.00
        )
        
        # Criar usuário empresa
        self.user_empresa = User.objects.create_user(
            username="empresa@teste.com",
            email="empresa@teste.com",
            password="testpass123",
            tipo_usuario="admin_empresa",
            empresa_contratante=self.empresa
        )
        
        # Criar usuário freelancer
        self.user_freelancer = User.objects.create_user(
            username="freelancer@teste.com",
            email="freelancer@teste.com",
            password="testpass123",
            tipo_usuario="freelancer"
        )
        
        # Criar freelancer
        self.freelancer = Freelance.objects.create(
            usuario=self.user_freelancer,
            nome_completo="Freelancer Teste",
            cpf="12345678901"
        )
        
        # Criar empresa proprietária do local (fornecedor)
        self.empresa_proprietaria = Empresa.objects.create(
            nome="Empresa Proprietária do Local",
            cnpj="98765432000199"
        )
        
        # Criar local
        self.local = LocalEvento.objects.create(
            nome="Local Teste",
            endereco="Rua Teste, 123",
            capacidade=100,
            empresa_proprietaria=self.empresa_proprietaria,
            empresa_contratante=self.empresa
        )
        
        # Criar evento
        self.evento = Evento.objects.create(
            nome="Evento Teste",
            descricao="Descrição do evento",
            data_inicio="2024-12-01",
            data_fim="2024-12-02",
            local=self.local,
            empresa_contratante=self.empresa,
            empresa_contratante_mao_obra=self.empresa_proprietaria
        )
        
        # Criar setor
        self.setor = SetorEvento.objects.create(
            nome="Setor Teste",
            evento=self.evento
        )
        
        # Criar tipo de função
        self.tipo_funcao = TipoFuncao.objects.create(
            nome="Alimentação"
        )
        
        # Criar função
        self.funcao = Funcao.objects.create(
            nome="Garçom",
            descricao="Atendimento ao cliente",
            tipo_funcao=self.tipo_funcao
        )
        
        # Criar vaga
        self.vaga = Vaga.objects.create(
            setor=self.setor,
            titulo="Garçom para Evento",
            funcao=self.funcao,
            quantidade=5,
            remuneracao=100.00,
            descricao="Vaga para garçom"
        )
    
    def test_listar_vagas_autenticado(self):
        """Teste para listar vagas com usuário autenticado"""
        self.client.force_authenticate(user=self.user_freelancer)
        url = reverse('vaga-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_listar_vagas_nao_autenticado(self):
        """Teste para listar vagas sem autenticação"""
        url = reverse('vaga-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_candidatar_se_vaga(self):
        """Teste para candidatar-se a uma vaga"""
        self.client.force_authenticate(user=self.user_freelancer)
        url = reverse('candidatura-list')
        data = {'vaga_id': self.vaga.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verificar se candidatura foi criada
        candidatura = Candidatura.objects.filter(
            freelance=self.freelancer,
            vaga=self.vaga
        ).first()
        self.assertIsNotNone(candidatura)
        self.assertEqual(candidatura.status, 'pendente')
    
    def test_listar_minhas_candidaturas(self):
        """Teste para listar candidaturas do freelancer"""
        # Criar candidatura
        Candidatura.objects.create(
            freelance=self.freelancer,
            vaga=self.vaga
        )
        
        self.client.force_authenticate(user=self.user_freelancer)
        url = reverse('candidatura-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_aprovar_candidatura_empresa(self):
        """Teste para empresa aprovar candidatura"""
        # Criar candidatura
        candidatura = Candidatura.objects.create(
            freelance=self.freelancer,
            vaga=self.vaga
        )
        
        self.client.force_authenticate(user=self.user_empresa)
        url = reverse('candidatura-aprovar', kwargs={'pk': candidatura.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar se status foi alterado
        candidatura.refresh_from_db()
        self.assertEqual(candidatura.status, 'aprovado')
    
    def test_cancelar_candidatura(self):
        """Teste para cancelar candidatura"""
        # Criar candidatura
        candidatura = Candidatura.objects.create(
            freelance=self.freelancer,
            vaga=self.vaga
        )
        
        self.client.force_authenticate(user=self.user_freelancer)
        url = reverse('candidatura-cancelar', kwargs={'pk': candidatura.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar se candidatura foi removida
        self.assertFalse(Candidatura.objects.filter(id=candidatura.id).exists())
    
    def test_listar_eventos(self):
        """Teste para listar eventos"""
        self.client.force_authenticate(user=self.user_freelancer)
        url = reverse('evento-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_criar_evento_empresa(self):
        """Teste para empresa criar evento"""
        self.client.force_authenticate(user=self.user_empresa)
        url = reverse('evento-list')
        data = {
            'nome': 'Novo Evento',
            'descricao': 'Descrição do novo evento',
            'data_inicio': '2024-12-15',
            'data_fim': '2024-12-16',
            'local_id': self.local.id,
            'empresa_contratante_mao_obra_id': self.empresa_proprietaria.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verificar se evento foi criado
        evento = Evento.objects.filter(nome='Novo Evento').first()
        self.assertIsNotNone(evento)
        self.assertEqual(evento.empresa_contratante, self.empresa)
    
    def test_perfil_usuario(self):
        """Teste para obter perfil do usuário"""
        self.client.force_authenticate(user=self.user_freelancer)
        url = reverse('user-profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'freelancer@teste.com')
        self.assertEqual(response.data['tipo_usuario'], 'freelancer')
    
    def test_pre_cadastro_freelancer(self):
        """Teste para pré-cadastro de freelancer"""
        url = reverse('freelancer-pre-cadastro')
        data = {
            'nome_completo': 'Novo Freelancer',
            'telefone': '11999999999',
            'cpf': '98765432100',
            'email': 'novo@freelancer.com',
            'password': 'testpass123',
            'data_nascimento': '1990-01-01',
            'sexo': 'M',
            'habilidades': 'Garçom, Bartender'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verificar se usuário foi criado
        user = User.objects.filter(email='novo@freelancer.com').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.tipo_usuario, 'freelancer')
        
        # Verificar se freelancer foi criado
        freelance = Freelance.objects.filter(usuario=user).first()
        self.assertIsNotNone(freelance)
        self.assertEqual(freelance.nome_completo, 'Novo Freelancer')