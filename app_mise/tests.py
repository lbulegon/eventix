from datetime import date

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app_eventos.models import (
    Empresa,
    EmpresaContratante,
    Evento,
    LocalEvento,
    SetorEvento,
    TipoEmpresa,
)
from .models import MiseEnPlace


User = get_user_model()


class MiseEnPlaceAPITestCase(APITestCase):
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

        self.setor = SetorEvento.objects.create(
            evento=self.evento,
            nome="Cozinha",
            descricao="",
            capacidade=10,
            ativo=True,
        )

        self.usuario = User.objects.create_user(
            username="coordenador",
            password="password123",
            tipo_usuario="admin_empresa",
            empresa_contratante=empresa,
        )

        self.client.force_authenticate(self.usuario)
        self.url = reverse("api_v01:mise", kwargs={"evento_id": self.evento.id})

    def test_criar_e_atualizar_mise(self):
        payload = {
            "setor": self.setor.id,
            "tarefa": "Preparar estações",
            "tempo_estimado_min": 60,
            "status": "pendente",
        }

        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mise_id = response.data["id"]
        self.assertTrue(MiseEnPlace.objects.filter(id=mise_id).exists())

        response_list = self.client.get(self.url)
        self.assertEqual(response_list.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_list.data), 1)

        response_patch = self.client.patch(
            self.url,
            {"id": mise_id, "status": "em_execucao"},
            format="json",
        )
        self.assertEqual(response_patch.status_code, status.HTTP_200_OK)
        self.assertEqual(response_patch.data["status"], "em_execucao")

