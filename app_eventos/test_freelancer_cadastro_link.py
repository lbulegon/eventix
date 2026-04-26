"""
Testes do cadastro público de freelancer (link com convite assinado).
Fluxo: /freelancer/cadastro/?convite=... e app_eventos.convite_freelancer
"""
from decimal import Decimal

from django.core import signing
from django.test import TestCase, Client, override_settings
from django.test.client import RequestFactory
from django.urls import reverse

from app_eventos.convite_freelancer import (
    CADASTRO_CONVITE_SALT,
    montar_payload_convite_cadastro,
)
from app_eventos.models import (
    EmpresaContratante,
    Freelance,
    FreelancerFuncao,
    Funcao,
    PlanoContratacao,
    TipoFuncao,
)
from django.contrib.auth import get_user_model

User = get_user_model()


@override_settings(FREELANCER_REACT_UX_URL="")
class FreelancerCadastroLinkTestCase(TestCase):
    def setUp(self):
        self.plano = PlanoContratacao.objects.create(
            nome="Plano Teste Cadastro",
            tipo_plano="profissional",
            descricao="Teste",
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
        # Fallback do cadastro (nome com "Eventix")
        self.emp_eventix = EmpresaContratante.objects.create(
            nome="Eventix",
            cnpj="00.000.000/0001-00",
            razao_social="Eventix Test LTDA",
            nome_fantasia="Eventix Plataforma",
            email="x@eventix.com",
            data_vencimento="2030-12-31",
            plano_contratado=self.plano,
            valor_mensal=Decimal("0.00"),
        )
        self.emp_convidada = EmpresaContratante.objects.create(
            nome="Empresa Convidada",
            cnpj="11.222.333/0001-44",
            razao_social="EC LTDA",
            nome_fantasia="Buffet Sabor & Arte",
            email="contato@buffet.com",
            data_vencimento="2030-12-31",
            plano_contratado=self.plano,
            valor_mensal=Decimal("100.00"),
        )
        self.tipo_func = TipoFuncao.objects.create(nome="Cozinha")
        self.funcao = Funcao.objects.create(
            nome="Ajudante de Cozinha",
            descricao="Apoio",
            tipo_funcao=self.tipo_func,
            ativo=True,
        )

    def _token_convite(self, empresa_id, **extra):
        payload = {"empresa_id": int(empresa_id), **extra}
        return signing.dumps(payload, salt=CADASTRO_CONVITE_SALT)

    def test_get_cadastro_sem_convite_200(self):
        client = Client()
        url = reverse("freelancer_publico:cadastro")
        r = client.get(url)
        self.assertEqual(r.status_code, 200)

    def test_get_cadastro_com_convite_monta_empresa_nome(self):
        client = Client()
        token = self._token_convite(self.emp_convidada.id)
        url = reverse("freelancer_publico:cadastro") + f"?convite={token}"
        r = client.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Buffet Sabor", status_code=200)

    def test_montar_payload_convite_tem_link_e_whatsapp(self):
        rf = RequestFactory()
        req = rf.get("/")
        p = montar_payload_convite_cadastro(
            req, self.emp_convidada, telefone="11999998888", funcao_id=self.funcao.id
        )
        self.assertTrue(p.get("sucesso"))
        self.assertIn("/freelancer/cadastro/?convite=", p["link_cadastro"])
        self.assertIn("http://", p["link_cadastro"])
        self.assertIn("Faça seu cadastro rápido", p["mensagem_whatsapp"])

    def test_post_cadastro_cria_freelance_vinculado_empresa_convite(self):
        client = Client()
        phone = "11988776601"
        token = self._token_convite(
            self.emp_convidada.id, funcao_id=self.funcao.id, telefone=phone
        )
        url = reverse("freelancer_publico:cadastro")
        r = client.post(
            url,
            {
                "nome_completo": "Maria Teste Link",
                "telefone": phone,
                "email": "maria.teste.link@example.com",
                "cpf": "52998224725",
                "senha": "SenhaForte-99",
                "convite": token,
            },
        )
        # redirect após sucesso
        self.assertIn(r.status_code, (301, 302, 303))
        user = User.objects.get(email="maria.teste.link@example.com")
        self.assertEqual(user.tipo_usuario, "freelancer")
        self.assertEqual(user.empresa_contratante_id, self.emp_convidada.id)
        fl = Freelance.objects.get(usuario=user)
        self.assertEqual(fl.telefone, phone)
        self.assertTrue(
            FreelancerFuncao.objects.filter(
                freelancer=fl, funcao=self.funcao
            ).exists()
        )

    def test_post_telefone_duplicado_redireciona_login(self):
        # primeiro cadastro
        u = User.objects.create_user(
            username="fr_9988776602",
            email="dup@example.com",
            password="x",
            tipo_usuario="freelancer",
        )
        Freelance.objects.create(
            usuario=u, nome_completo="Já Existe", telefone="11988776602"
        )
        client = Client()
        url = reverse("freelancer_publico:cadastro")
        r = client.post(
            url,
            {
                "nome_completo": "Tentativa Dup",
                "telefone": "11988776602",
                "email": "outro@example.com",
                "senha": "SenhaForte-99",
            },
        )
        self.assertIn(r.status_code, (301, 302, 303))
        self.assertIn(reverse("freelancer_publico:login"), r["Location"])

