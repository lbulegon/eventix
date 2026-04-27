from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from app_eventos.models import (
    Candidatura,
    Empresa,
    EmpresaContratante,
    Evento,
    Freelance,
    FreelancerFuncao,
    Funcao,
    LocalEvento,
    PlanoContratacao,
    SetorEvento,
    TipoEmpresa,
    TipoFuncao,
    Vaga,
)

User = get_user_model()


class VagaDisponibilidadeApiTestCase(APITestCase):
    def setUp(self):
        self.plano = PlanoContratacao.objects.create(
            nome="Plano API Vagas",
            tipo_plano="profissional",
            descricao="Plano para testes de disponibilidade",
            max_eventos_mes=100,
            max_usuarios=100,
            max_freelancers=1000,
            max_equipamentos=1000,
            max_locais=100,
            valor_mensal=Decimal("500.00"),
            valor_anual=Decimal("5400.00"),
            desconto_anual=Decimal("10.00"),
            percentual_comissao=Decimal("6.00"),
            ativo=True,
        )

        self.empresa_contratante = EmpresaContratante.objects.create(
            nome="Empresa Teste",
            nome_fantasia="Empresa Teste",
            razao_social="Empresa Teste LTDA",
            cnpj="12.345.678/0001-90",
            email="contato@empresa-teste.com",
            data_vencimento="2030-12-31",
            plano_contratado=self.plano,
            valor_mensal=Decimal("500.00"),
        )

        tipo_empresa = TipoEmpresa.objects.create(nome="Buffet", descricao="")
        self.empresa_produtora = Empresa.objects.create(
            nome="Produtora X",
            cnpj="98.765.432/0001-10",
            tipo_empresa=tipo_empresa,
            email="produtora@x.com",
        )

        self.local = LocalEvento.objects.create(
            nome="Arena Central",
            endereco="Rua Teste, 123",
            capacidade=500,
            empresa_proprietaria=self.empresa_produtora,
        )

        self.evento = Evento.objects.create(
            nome="Show de Teste",
            descricao="Evento para teste",
            data_inicio="2030-01-10",
            data_fim="2030-01-11",
            local=self.local,
            empresa_contratante=self.empresa_contratante,
            empresa_produtora=self.empresa_produtora,
        )

        self.setor = SetorEvento.objects.create(nome="Palco", evento=self.evento)
        tipo_funcao = TipoFuncao.objects.create(nome="Operação")
        self.funcao = Funcao.objects.create(nome="Segurança", tipo_funcao=tipo_funcao, ativo=True)

        self.user_freelancer = User.objects.create_user(
            username="freela@test.com",
            email="freela@test.com",
            password="teste12345",
            tipo_usuario="freelancer",
        )
        self.freelancer = Freelance.objects.create(
            usuario=self.user_freelancer,
            nome_completo="Freelancer Teste",
            telefone="11999990000",
            cpf="12345678909",
        )
        FreelancerFuncao.objects.create(
            freelancer=self.freelancer,
            funcao=self.funcao,
            nivel="iniciante",
            ativo=True,
        )

        self.tipo_funcao = tipo_funcao

    def _criar_vaga(self, *, inicio_offset_horas: int) -> Vaga:
        now = timezone.now()
        return Vaga.objects.create(
            setor=self.setor,
            evento=self.evento,
            empresa_contratante=self.empresa_contratante,
            titulo="Vaga Teste",
            funcao=self.funcao,
            quantidade=3,
            remuneracao=Decimal("120.00"),
            descricao="Descrição",
            ativa=True,
            publicada=True,
            data_limite_candidatura=now + timedelta(hours=6),
            data_inicio_trabalho=now + timedelta(hours=inicio_offset_horas),
        )

    def test_vaga_com_turno_iniciado_nao_aparece_na_lista(self):
        self._criar_vaga(inicio_offset_horas=-1)
        self.client.force_authenticate(user=self.user_freelancer)

        response = self.client.get(reverse("vaga-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

    def test_candidatura_bloqueada_quando_turno_ja_iniciou(self):
        vaga = self._criar_vaga(inicio_offset_horas=-1)
        self.client.force_authenticate(user=self.user_freelancer)

        response = self.client.post(reverse("candidatura-list"), {"vaga_id": vaga.id})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Candidatura.objects.filter(vaga=vaga, freelance=self.freelancer).exists())

    def test_vaga_legada_evento_passado_sem_inicio_nao_aparece(self):
        self.evento.data_inicio = timezone.localdate() - timedelta(days=1)
        self.evento.save(update_fields=["data_inicio"])

        Vaga.objects.create(
            setor=self.setor,
            evento=self.evento,
            empresa_contratante=self.empresa_contratante,
            titulo="Vaga Legada",
            funcao=self.funcao,
            quantidade=2,
            remuneracao=Decimal("100.00"),
            descricao="Legada sem data_inicio_trabalho",
            ativa=True,
            publicada=True,
            data_inicio_trabalho=None,
            data_limite_candidatura=None,
        )

        self.client.force_authenticate(user=self.user_freelancer)
        response = self.client.get(reverse("vaga-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

    def test_listagem_filtra_por_especialidade_do_freelancer(self):
        funcao_outra = Funcao.objects.create(
            nome="Garçom",
            tipo_funcao=self.tipo_funcao,
            ativo=True,
        )
        self._criar_vaga(inicio_offset_horas=2)
        Vaga.objects.create(
            setor=self.setor,
            evento=self.evento,
            empresa_contratante=self.empresa_contratante,
            titulo="Vaga Outra Especialidade",
            funcao=funcao_outra,
            quantidade=1,
            remuneracao=Decimal("90.00"),
            descricao="Descrição",
            ativa=True,
            publicada=True,
            data_limite_candidatura=timezone.now() + timedelta(hours=6),
            data_inicio_trabalho=timezone.now() + timedelta(hours=2),
        )
        self.client.force_authenticate(user=self.user_freelancer)
        response = self.client.get(reverse("vaga-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["funcao"]["nome"], "Segurança")

    def test_candidatura_bloqueada_sem_especialidade(self):
        funcao_outra = Funcao.objects.create(
            nome="Bartender",
            tipo_funcao=self.tipo_funcao,
            ativo=True,
        )
        vaga = Vaga.objects.create(
            setor=self.setor,
            evento=self.evento,
            empresa_contratante=self.empresa_contratante,
            titulo="Vaga Bartender",
            funcao=funcao_outra,
            quantidade=1,
            remuneracao=Decimal("110.00"),
            descricao="Descrição",
            ativa=True,
            publicada=True,
            data_limite_candidatura=timezone.now() + timedelta(hours=6),
            data_inicio_trabalho=timezone.now() + timedelta(hours=1),
        )
        self.client.force_authenticate(user=self.user_freelancer)
        response = self.client.post(reverse("candidatura-list"), {"vaga_id": vaga.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Candidatura.objects.filter(vaga=vaga, freelance=self.freelancer).exists())
