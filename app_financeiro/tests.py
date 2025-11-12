from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app_eventos.models import Empresa, EmpresaContratante, Evento, LocalEvento, TipoEmpresa
from .models import OrcamentoOperacional


User = get_user_model()


class OrcamentoOperacionalAPITestCase(APITestCase):
    def setUp(self):
        tipo = TipoEmpresa.objects.create(nome="Buffet", descricao="")
        empresa_fornecedora = Empresa.objects.create(
            nome="Fornecedor",
            cnpj="11.111.111/0001-11",
            tipo_empresa=tipo,
            telefone="",
            email="fornecedor@example.com",
            ativo=True,
        )

        local = LocalEvento.objects.create(
            nome="Casa",
            endereco="Rua A",
            capacidade=200,
            descricao="",
            empresa_proprietaria=empresa_fornecedora,
            ativo=True,
        )

        empresa = EmpresaContratante.objects.create(
            nome="Empresa",
            cnpj="22.222.222/0001-22",
            razao_social="Empresa LTDA",
            nome_fantasia="Empresa",
            telefone="",
            email="empresa@example.com",
            valor_mensal="1000.00",
            data_vencimento=date(2030, 1, 1),
        )

        self.evento = Evento.objects.create(
            empresa_contratante=empresa,
            nome="Evento",
            data_inicio=date(2030, 5, 10),
            data_fim=date(2030, 5, 11),
            descricao="",
            local=local,
            empresa_produtora=empresa_fornecedora,
        )

        self.usuario = User.objects.create_user(
            username="coordenador",
            password="password123",
            tipo_usuario="admin_empresa",
            empresa_contratante=empresa,
        )

        self.client.force_authenticate(self.usuario)
        self.url = reverse("api_v01:orcamento_gerar", kwargs={"evento_id": self.evento.id})

    def test_gerar_orcamento_operacional(self):
        payload = {
            "subtotal": "10000.00",
            "margem": "20",
            "lucro_minimo": "1500.00",
            "tipo_precificacao": "minimo",
            "detalhes_custos": {"insumos": 6000, "equipe": 3000},
        }

        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(OrcamentoOperacional.objects.filter(evento=self.evento).exists())

        orcamento = OrcamentoOperacional.objects.get(evento=self.evento)
        esperado = max(Decimal("10000.00") + Decimal("1500.00"), Decimal("10000.00") * Decimal("1.20"))
        self.assertEqual(orcamento.total, esperado)

        payload_update = {
            "subtotal": "9000.00",
            "margem": "10",
            "lucro_minimo": "500.00",
            "tipo_precificacao": "percentual",
            "detalhes_custos": {"insumos": 5000, "equipe": 2500},
        }

        response_update = self.client.post(self.url, payload_update, format="json")
        self.assertEqual(response_update.status_code, status.HTTP_200_OK)
        orcamento.refresh_from_db()
        self.assertEqual(orcamento.total, Decimal("9900.00"))

