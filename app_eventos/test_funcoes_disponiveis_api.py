from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app_eventos.models import (
    EmpresaContratante,
    Freelance,
    Funcao,
    PlanoContratacao,
    TipoFuncao,
)

User = get_user_model()


class FuncoesDisponiveisApiTestCase(APITestCase):
    def setUp(self):
        plano = PlanoContratacao.objects.create(
            nome="Plano Funcoes",
            tipo_plano="profissional",
            descricao="Plano teste",
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
        empresa = EmpresaContratante.objects.create(
            nome="Empresa",
            nome_fantasia="Empresa",
            razao_social="Empresa LTDA",
            cnpj="11.111.111/0001-11",
            email="empresa@test.com",
            data_vencimento="2030-12-31",
            plano_contratado=plano,
            valor_mensal=Decimal("100.00"),
        )
        user = User.objects.create_user(
            username="freela.funcoes@test.com",
            email="freela.funcoes@test.com",
            password="12345678",
            tipo_usuario="freelancer",
            empresa_contratante=empresa,
        )
        Freelance.objects.create(usuario=user, nome_completo="Freela Teste")
        self.user = user

        tipo = TipoFuncao.objects.create(nome="Operação")
        Funcao.objects.create(nome="Segurança", tipo_funcao=tipo, ativo=True)
        Funcao.objects.create(nome="Garçom", tipo_funcao=tipo, ativo=True)

    def test_lista_funcoes_retorna_todas_ativas(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("funcao-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        nomes = [item["nome"] for item in response.data["results"]]
        self.assertIn("Segurança", nomes)
        self.assertIn("Garçom", nomes)
