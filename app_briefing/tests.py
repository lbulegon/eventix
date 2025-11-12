from datetime import date

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app_eventos.models import (
    EmpresaContratante,
    Evento,
    TipoEmpresa,
    Empresa,
    LocalEvento,
)


User = get_user_model()


class BriefingAPITestCase(APITestCase):
    def setUp(self):
        self.tipo_empresa = TipoEmpresa.objects.create(nome="Buffet", descricao="")
        self.empresa_fornecedora = Empresa.objects.create(
            nome="Fornecedor Teste",
            cnpj="11.111.111/0001-11",
            tipo_empresa=self.tipo_empresa,
            telefone="",
            email="fornecedor@example.com",
            ativo=True,
        )

        self.local_evento = LocalEvento.objects.create(
            nome="Casa de Eventos",
            endereco="Rua A",
            capacidade=200,
            descricao="",
            empresa_proprietaria=self.empresa_fornecedora,
            ativo=True,
        )

        self.empresa_contratante = EmpresaContratante.objects.create(
            nome="Empresa Teste",
            cnpj="22.222.222/0001-22",
            razao_social="Empresa Teste LTDA",
            nome_fantasia="Empresa Teste",
            telefone="",
            email="contato@empresa.com",
            valor_mensal="1000.00",
            data_vencimento=date(2030, 1, 1),
        )

        self.evento = Evento.objects.create(
            empresa_contratante=self.empresa_contratante,
            nome="Evento de Teste",
            data_inicio=date(2030, 5, 10),
            data_fim=date(2030, 5, 11),
            descricao="",
            local=self.local_evento,
            empresa_produtora=self.empresa_fornecedora,
        )

        self.usuario = User.objects.create_user(
            username="coordenador",
            password="password123",
            tipo_usuario="admin_empresa",
            empresa_contratante=self.empresa_contratante,
        )

        self.client.force_authenticate(self.usuario)
        self.url = reverse("api_v01:evento_briefing", kwargs={"evento_id": self.evento.id})

    def test_criar_e_recuperar_briefing(self):
        payload = {
            "proposito": "Apresentar nova coleção",
            "experiencia_desejada": "Imersiva",
            "tipo_servico": "Coquetel",
            "publico_estimado": 150,
            "restricoes_alimentares": "Veganos e sem glúten",
            "orcamento_disponivel": "50000.00",
            "infraestrutura_local": "Cozinha aberta",
            "observacoes": "Recepção com música ao vivo",
        }

        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["tipo_servico"], "Coquetel")

        response_get = self.client.get(self.url)
        self.assertEqual(response_get.status_code, status.HTTP_200_OK)
        self.assertEqual(response_get.data["publico_estimado"], 150)

    def test_atualizar_briefing(self):
        self.test_criar_e_recuperar_briefing()

        update_payload = {
            "proposito": "Apresentar nova coleção",
            "experiencia_desejada": "Sensorial",
            "tipo_servico": "Jantar",
            "publico_estimado": 120,
            "restricoes_alimentares": "Sem lactose",
            "orcamento_disponivel": "55000.00",
            "infraestrutura_local": "Cozinha fechada",
            "observacoes": "Adicionar iluminação cênica",
        }

        response = self.client.put(self.url, update_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["tipo_servico"], "Jantar")
        self.assertEqual(response.data["experiencia_desejada"], "Sensorial")

