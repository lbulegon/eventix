# api_mobile/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from app_eventos.models import (
    Vaga, Candidatura, Evento, Freelance, EmpresaContratante, PlanoContratacao, GrupoEmpresarial,
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
            empresa_contratante_recursos=self.empresa_proprietaria
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

    def test_onboarding_nivel2_freelancer(self):
        """GET/PATCH /freelancers/onboarding/ — estado nível 2 e atualização parcial segura."""
        self.client.force_authenticate(user=self.user_freelancer)
        url = reverse('freelancer-onboarding')
        r0 = self.client.get(url)
        self.assertEqual(r0.status_code, status.HTTP_200_OK)
        self.assertIn('onboarding', r0.data)
        self.assertIn('prompt_suporte_nivel2', r0.data)
        self.assertIn('nivel2_dados_complementares', r0.data['onboarding'])
        r1 = self.client.patch(
            url,
            {'cidade': 'São Paulo', 'uf': 'SP', 'cep': '01001000'},
            format='json',
        )
        self.assertEqual(r1.status_code, status.HTTP_200_OK)
        self.assertTrue(r1.data.get('success'))
        self.freelancer.refresh_from_db()
        self.assertEqual(self.freelancer.cidade, 'São Paulo')

    def test_onboarding_nivel2_rejeita_nao_freelancer(self):
        self.client.force_authenticate(user=self.user_empresa)
        url = reverse('freelancer-onboarding')
        r = self.client.get(url)
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)


class VagaEmissaoContratoTestCase(APITestCase):
    def setUp(self):
        self.plano = PlanoContratacao.objects.create(
            nome="Plano Teste API",
            tipo_plano="profissional",
            descricao="Plano para testes de emissão de vagas",
            max_eventos_mes=100,
            max_usuarios=100,
            max_freelancers=1000,
            max_equipamentos=1000,
            max_locais=100,
            valor_mensal=500.00,
            valor_anual=5400.00,
            desconto_anual=10.00,
            percentual_comissao=6.00,
            ativo=True,
        )

        self.empresa_a = EmpresaContratante.objects.create(
            nome_fantasia="Empresa A",
            cnpj="11111111000111",
            email="a@empresa.com",
            data_vencimento="2026-12-31",
            plano_contratado=self.plano,
            valor_mensal=500.00,
        )
        self.empresa_b = EmpresaContratante.objects.create(
            nome_fantasia="Empresa B",
            cnpj="22222222000122",
            email="b@empresa.com",
            data_vencimento="2026-12-31",
            plano_contratado=self.plano,
            valor_mensal=500.00,
        )

        self.user_empresa_a = User.objects.create_user(
            username="admin.a@teste.com",
            email="admin.a@teste.com",
            password="testpass123",
            tipo_usuario="admin_empresa",
            empresa_contratante=self.empresa_a,
        )

        self.user_freelancer = User.objects.create_user(
            username="freelancer.contrato@teste.com",
            email="freelancer.contrato@teste.com",
            password="testpass123",
            tipo_usuario="freelancer",
        )
        self.freelancer = Freelance.objects.create(
            usuario=self.user_freelancer,
            nome_completo="Freelancer Contrato",
            cpf="32165498700",
        )

        self.grupo = GrupoEmpresarial.objects.create(nome="Grupo Teste")
        self.empresa_a.grupo_empresarial = self.grupo
        self.empresa_a.save(update_fields=['grupo_empresarial'])
        self.empresa_b.grupo_empresarial = self.grupo
        self.empresa_b.save(update_fields=['grupo_empresarial'])
        self.user_gestor = User.objects.create_user(
            username="gestor.grupo@teste.com",
            email="gestor.grupo@teste.com",
            password="testpass123",
            tipo_usuario="gestor_grupo",
            grupo_empresarial=self.grupo,
        )

        self.empresa_proprietaria = Empresa.objects.create(
            nome="Empresa Proprietaria",
            cnpj="33333333000133",
        )

        self.local_a = LocalEvento.objects.create(
            nome="Local A",
            endereco="Rua A, 100",
            capacidade=100,
            empresa_proprietaria=self.empresa_proprietaria,
        )
        self.local_b = LocalEvento.objects.create(
            nome="Local B",
            endereco="Rua B, 200",
            capacidade=100,
            empresa_proprietaria=self.empresa_proprietaria,
        )

        self.evento_a = Evento.objects.create(
            nome="Evento A",
            descricao="Evento empresa A",
            data_inicio="2026-01-10",
            data_fim="2026-01-11",
            local=self.local_a,
            empresa_contratante=self.empresa_a,
            empresa_produtora=self.empresa_proprietaria,
        )
        self.evento_b = Evento.objects.create(
            nome="Evento B",
            descricao="Evento empresa B",
            data_inicio="2026-01-12",
            data_fim="2026-01-13",
            local=self.local_b,
            empresa_contratante=self.empresa_b,
            empresa_produtora=self.empresa_proprietaria,
        )

        self.setor_a = SetorEvento.objects.create(nome="Setor A", evento=self.evento_a)
        self.setor_b = SetorEvento.objects.create(nome="Setor B", evento=self.evento_b)

        self.tipo_funcao = TipoFuncao.objects.create(nome="Operacao")
        self.funcao_global = Funcao.objects.create(
            nome="Garcom Global",
            descricao="Funcao global",
            tipo_funcao=self.tipo_funcao,
            ativo=True,
            disponivel_para_vagas=True,
        )
        self.funcao_empresa_b = Funcao.objects.create(
            nome="Funcao Privada B",
            descricao="Funcao tenant B",
            tipo_funcao=self.tipo_funcao,
            empresa_contratante=self.empresa_b,
            ativo=True,
            disponivel_para_vagas=True,
        )

    def test_empresa_nao_pode_criar_vaga_com_setor_de_outro_tenant(self):
        self.client.force_authenticate(user=self.user_empresa_a)
        url = reverse('vaga-avancada-list')
        payload = {
            'titulo': 'Vaga invalida cross-tenant',
            'setor_id': self.setor_b.id,
            'funcao_id': self.funcao_global.id,
            'quantidade': 2,
            'remuneracao': 130.0,
            'descricao': 'Teste',
            'ativa': True,
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Vaga.objects.filter(titulo='Vaga invalida cross-tenant').count(), 0)

    def test_empresa_nao_pode_criar_vaga_com_funcao_privada_de_outro_tenant(self):
        self.client.force_authenticate(user=self.user_empresa_a)
        url = reverse('vaga-avancada-list')
        payload = {
            'titulo': 'Vaga funcao invalida',
            'setor_id': self.setor_a.id,
            'funcao_id': self.funcao_empresa_b.id,
            'quantidade': 1,
            'remuneracao': 150.0,
            'descricao': 'Teste',
            'ativa': True,
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Vaga.objects.filter(titulo='Vaga funcao invalida').count(), 0)

    def test_empresa_nao_pode_publicar_vaga_de_outro_tenant(self):
        vaga_b = Vaga.objects.create(
            evento=self.evento_b,
            setor=self.setor_b,
            empresa_contratante=self.empresa_b,
            titulo='Vaga B privada',
            funcao=self.funcao_global,
            quantidade=3,
            remuneracao=120.0,
            descricao='Teste',
            ativa=True,
            publicada=False,
        )
        self.client.force_authenticate(user=self.user_empresa_a)
        url = reverse('vaga-avancada-publicar', kwargs={'pk': vaga_b.id})
        response = self.client.post(url, {}, format='json')
        # O queryset do viewset restringe por tenant e devolve 404 antes da action.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        vaga_b.refresh_from_db()
        self.assertFalse(vaga_b.publicada)

    def test_freelancer_lista_vagas_ativas_em_mercado_aberto(self):
        Vaga.objects.create(
            evento=self.evento_a,
            setor=self.setor_a,
            empresa_contratante=self.empresa_a,
            titulo='Vaga aberta A',
            funcao=self.funcao_global,
            quantidade=2,
            remuneracao=110.0,
            descricao='A',
            ativa=True,
            publicada=True,
        )
        Vaga.objects.create(
            evento=self.evento_b,
            setor=self.setor_b,
            empresa_contratante=self.empresa_b,
            titulo='Vaga aberta B',
            funcao=self.funcao_global,
            quantidade=2,
            remuneracao=115.0,
            descricao='B',
            ativa=True,
            publicada=True,
        )
        self.client.force_authenticate(user=self.user_freelancer)
        url = reverse('vaga-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titulos = [item['titulo'] for item in response.data['results']]
        self.assertIn('Vaga aberta A', titulos)
        self.assertIn('Vaga aberta B', titulos)

    def test_empresa_pode_patch_vaga_do_proprio_tenant(self):
        vaga_a = Vaga.objects.create(
            evento=self.evento_a,
            setor=self.setor_a,
            empresa_contratante=self.empresa_a,
            titulo='Vaga A patch',
            funcao=self.funcao_global,
            quantidade=2,
            remuneracao=100.0,
            descricao='A',
            ativa=True,
        )
        self.client.force_authenticate(user=self.user_empresa_a)
        url = reverse('vaga-avancada-detail', kwargs={'pk': vaga_a.id})
        response = self.client.patch(url, {'titulo': 'Vaga A patch editada'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        vaga_a.refresh_from_db()
        self.assertEqual(vaga_a.titulo, 'Vaga A patch editada')

    def test_empresa_nao_pode_put_vaga_de_outro_tenant(self):
        vaga_b = Vaga.objects.create(
            evento=self.evento_b,
            setor=self.setor_b,
            empresa_contratante=self.empresa_b,
            titulo='Vaga B put',
            funcao=self.funcao_global,
            quantidade=2,
            remuneracao=100.0,
            descricao='B',
            ativa=True,
        )
        self.client.force_authenticate(user=self.user_empresa_a)
        url = reverse('vaga-avancada-detail', kwargs={'pk': vaga_b.id})
        response = self.client.put(
            url,
            {
                'titulo': 'Tentativa indevida',
                'setor_id': self.setor_b.id,
                'funcao_id': self.funcao_global.id,
                'quantidade': 3,
                'remuneracao': 120.0,
                'descricao': 'x',
                'ativa': True,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_gestor_grupo_sem_contexto_nao_pode_criar_vaga(self):
        self.client.force_authenticate(user=self.user_gestor)
        url = reverse('vaga-avancada-list')
        response = self.client.post(
            url,
            {
                'titulo': 'Vaga sem contexto',
                'setor_id': self.setor_a.id,
                'funcao_id': self.funcao_global.id,
                'quantidade': 1,
                'remuneracao': 100.0,
                'descricao': 'x',
                'ativa': True,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_gestor_grupo_com_contexto_pode_criar_vaga_no_tenant(self):
        self.client.force_authenticate(user=self.user_gestor)
        self.client.credentials(HTTP_X_EMPRESA_CONTEXT_ID=str(self.empresa_a.id))
        url = reverse('vaga-avancada-list')
        response = self.client.post(
            url,
            {
                'titulo': 'Vaga gestor contexto',
                'setor_id': self.setor_a.id,
                'funcao_id': self.funcao_global.id,
                'quantidade': 1,
                'remuneracao': 100.0,
                'descricao': 'x',
                'ativa': True,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Vaga.objects.filter(
                titulo='Vaga gestor contexto',
                empresa_contratante=self.empresa_a,
            ).exists()
        )

    def test_gestor_grupo_contexto_errado_nao_publica_vaga_de_outro_tenant(self):
        """Contexto empresa A: vaga da empresa B não aparece no queryset → 404."""
        vaga_b = Vaga.objects.create(
            evento=self.evento_b,
            setor=self.setor_b,
            empresa_contratante=self.empresa_b,
            titulo='Vaga B gestor contexto errado',
            funcao=self.funcao_global,
            quantidade=1,
            remuneracao=100.0,
            descricao='B',
            ativa=True,
            publicada=False,
        )
        self.client.force_authenticate(user=self.user_gestor)
        self.client.credentials(HTTP_X_EMPRESA_CONTEXT_ID=str(self.empresa_a.id))
        url = reverse('vaga-avancada-publicar', kwargs={'pk': vaga_b.id})
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        vaga_b.refresh_from_db()
        self.assertFalse(vaga_b.publicada)

    def test_gestor_grupo_contexto_errado_nao_despublica_vaga_de_outro_tenant(self):
        vaga_b = Vaga.objects.create(
            evento=self.evento_b,
            setor=self.setor_b,
            empresa_contratante=self.empresa_b,
            titulo='Vaga B despublicar bloqueado',
            funcao=self.funcao_global,
            quantidade=1,
            remuneracao=100.0,
            descricao='B',
            ativa=True,
            publicada=True,
        )
        self.client.force_authenticate(user=self.user_gestor)
        self.client.credentials(HTTP_X_EMPRESA_CONTEXT_ID=str(self.empresa_a.id))
        url = reverse('vaga-avancada-despublicar', kwargs={'pk': vaga_b.id})
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        vaga_b.refresh_from_db()
        self.assertTrue(vaga_b.publicada)