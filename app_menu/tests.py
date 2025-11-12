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
    TipoEmpresa,
)

from .models import FichaTecnica, Menu, Prato


User = get_user_model()


class MenuAPITestCase(APITestCase):
    def setUp(self):
        tipo = TipoEmpresa.objects.create(nome="Buffet", descricao="")
        self.empresa_fornecedora = Empresa.objects.create(
            nome="Fornecedor",
            cnpj="11.111.111/0001-11",
            tipo_empresa=tipo,
            telefone="",
            email="fornecedor@example.com",
            ativo=True,
        )

        self.local = LocalEvento.objects.create(
            nome="Casa",
            endereco="Rua A",
            capacidade=200,
            descricao="",
            empresa_proprietaria=self.empresa_fornecedora,
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
            local=self.local,
            empresa_produtora=self.empresa_fornecedora,
        )

        self.usuario = User.objects.create_user(
            username="coordenador",
            password="password123",
            tipo_usuario="admin_empresa",
            empresa_contratante=self.empresa,
        )

        self.client.force_authenticate(self.usuario)
        self.menu_url = reverse("api_v01:menu_list_create", kwargs={"evento_id": self.evento.id})

    def test_criar_menu_e_prato(self):
        response_menu = self.client.post(
            self.menu_url,
            {"titulo": "Menu Principal", "observacoes": ""},
            format="json",
        )
        self.assertEqual(response_menu.status_code, status.HTTP_201_CREATED)
        menu_id = response_menu.data["id"]
        self.assertTrue(Menu.objects.filter(id=menu_id).exists())

        prato_url = reverse(
            "api_v01:menu_pratos",
            kwargs={"evento_id": self.evento.id, "menu_id": menu_id},
        )
        response_prato = self.client.post(
            prato_url,
            {
                "nome": "Risoto",
                "categoria": "Principal",
                "custo_estimado": "35.50",
                "tempo_preparo_min": 25,
            },
            format="json",
        )
        self.assertEqual(response_prato.status_code, status.HTTP_201_CREATED)
        prato_id = response_prato.data["id"]
        self.assertTrue(Prato.objects.filter(id=prato_id).exists())

        ficha_url = reverse(
            "api_v01:menu_fichas",
            kwargs={
                "evento_id": self.evento.id,
                "menu_id": menu_id,
                "prato_id": prato_id,
            },
        )
        response_ficha = self.client.post(
            ficha_url,
            {
                "modo_preparo": "Refogar e finalizar",
                "rendimento": "10",
                "tempo_execucao": 30,
                "insumos": {"arroz": "1kg", "queijo": "200g"},
            },
            format="json",
        )
        self.assertEqual(response_ficha.status_code, status.HTTP_201_CREATED)
        self.assertTrue(FichaTecnica.objects.filter(prato_id=prato_id).exists())

        response_get = self.client.get(self.menu_url)
        self.assertEqual(response_get.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_get.data), 1)

