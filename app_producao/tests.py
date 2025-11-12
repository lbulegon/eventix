from datetime import date, datetime, timezone

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app_eventos.models import Empresa, EmpresaContratante, Evento, LocalEvento, TipoEmpresa
from .models import CronogramaPreProducao


User = get_user_model()


class CronogramaPreProducaoAPITestCase(APITestCase):
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

        self.empresa = EmpresaContratante.objects.create(
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
            empresa_contratante=self.empresa,
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
            empresa_contratante=self.empresa,
        )

        self.client.force_authenticate(self.usuario)
        self.url = reverse("api_v01:preproducao_cronograma", kwargs={"evento_id": self.evento.id})

    def test_criar_e_listar_cronograma(self):
        payload = {
            "etapa": "Confirmar fornecedores",
            "prazo": datetime(2030, 4, 5, 12, 0, tzinfo=timezone.utc).isoformat(),
            "status": "pendente",
            "observacoes": "Enviar e-mail de confirmação",
        }

        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CronogramaPreProducao.objects.filter(evento=self.evento).exists())

        response_list = self.client.get(self.url)
        self.assertEqual(response_list.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_list.data), 1)

        item_id = response_list.data[0]["id"]
        response_patch = self.client.patch(
            self.url,
            {"id": item_id, "status": "concluido"},
            format="json",
        )
        self.assertEqual(response_patch.status_code, status.HTTP_200_OK)
        self.assertEqual(response_patch.data["status"], "concluido")

