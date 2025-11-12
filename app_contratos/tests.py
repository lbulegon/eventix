import shutil
import tempfile
from datetime import date

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app_eventos.models import Empresa, EmpresaContratante, Evento, LocalEvento, TipoEmpresa
from app_financeiro.models import OrcamentoOperacional
from .models import ContratoEvento


User = get_user_model()


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ContratoEventoAPITestCase(APITestCase):
    @classmethod
    def tearDownClass(cls):  # pragma: no cover
        media_root = getattr(cls, "_overridden_settings", {}).get("MEDIA_ROOT")
        if media_root:
            shutil.rmtree(media_root, ignore_errors=True)
        super().tearDownClass()

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

        self.orcamento = OrcamentoOperacional.objects.create(
            evento=self.evento,
            subtotal="10000.00",
            margem="20",
            lucro_minimo="1000.00",
            total="12000.00",
            tipo_precificacao="percentual",
            detalhes_custos={"insumos": 7000, "equipe": 3000},
        )

        self.usuario = User.objects.create_user(
            username="coordenador",
            password="password123",
            tipo_usuario="admin_empresa",
            empresa_contratante=empresa,
        )

        self.client.force_authenticate(self.usuario)
        self.gerar_url = reverse("api_v01:contrato_gerar", kwargs={"evento_id": self.evento.id})
        self.assinar_url = reverse("api_v01:contrato_assinar", kwargs={"evento_id": self.evento.id})

    def test_gerar_e_assinar_contrato(self):
        payload = {
            "orcamento": self.orcamento.id,
            "condicoes_gerais": "Pagamento em 30 dias.",
        }

        response = self.client.post(self.gerar_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        contrato = ContratoEvento.objects.get(evento=self.evento)
        self.assertFalse(contrato.assinatura_cliente)
        self.assertTrue(contrato.pdf_url.endswith(".pdf") or contrato.pdf_url.endswith(".txt"))

        assinatura = self.client.post(self.assinar_url, {"data_assinatura": "2030-04-01T10:00:00Z"}, format="json")
        self.assertEqual(assinatura.status_code, status.HTTP_200_OK)
        contrato.refresh_from_db()
        self.assertTrue(contrato.assinatura_cliente)

