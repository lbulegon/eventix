from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from app_eventos.models import (
    CategoriaFinanceira,
    CategoriaInsumo,
    DespesaEvento,
    Empresa,
    EmpresaContratante,
    Evento,
    Fornecedor,
    Insumo,
    InsumoEvento,
    InsumoSetor,
    ItemChecklist,
    LocalEvento,
    ReceitaEvento,
    SetorEvento,
    Tarefa,
    TipoEmpresa,
    Vaga,
    ChecklistEvento,
)
from app_eventos.services.event_clone_service import EventCloneService, EventCloneOptions


User = get_user_model()


class EventCloneServiceTest(TestCase):
    def setUp(self):
        self.tipo_empresa = TipoEmpresa.objects.create(nome="Buffet", descricao="")
        self.empresa_fornecedora = Empresa.objects.create(
            nome="Fornecedora X",
            cnpj="11.111.111/0001-11",
            tipo_empresa=self.tipo_empresa,
            telefone="",
            email="fornecedor@example.com",
        )

        self.local = LocalEvento.objects.create(
            nome="Casa de Eventos",
            endereco="Rua A",
            capacidade=200,
            empresa_proprietaria=self.empresa_fornecedora,
        )

        self.empresa_contratante = EmpresaContratante.objects.create(
            nome="Empresa Teste",
            cnpj="22.222.222/0001-22",
            razao_social="Empresa Teste LTDA",
            nome_fantasia="Empresa Teste",
            telefone="",
            email="contato@empresa.com",
            valor_mensal=Decimal("1000.00"),
            data_vencimento=date(2030, 1, 1),
        )

        self.usuario = User.objects.create_user(
            username="coordenador",
            password="senha_forte",
            tipo_usuario='admin_empresa',
            empresa_contratante=self.empresa_contratante,
        )

        self.evento = Evento.objects.create(
            empresa_contratante=self.empresa_contratante,
            nome="Evento Original",
            data_inicio=date(2030, 5, 10),
            data_fim=date(2030, 5, 12),
            descricao="Evento completo",
            local=self.local,
            empresa_produtora=self.empresa_fornecedora,
        )

        self.setor = SetorEvento.objects.create(
            evento=self.evento,
            nome="Cozinha",
            descricao="",
            capacidade=10,
            ativo=True,
        )

        self.vaga = Vaga.objects.create(
            evento=self.evento,
            setor=self.setor,
            empresa_contratante=self.empresa_contratante,
            titulo="Chef",
            funcao=None,
            quantidade=3,
            quantidade_preenchida=2,
            remuneracao=Decimal("350.00"),
            tipo_remuneracao='por_dia',
            descricao="",
            requisitos="",
            responsabilidades="",
            beneficios="",
            nivel_experiencia='avancado',
            experiencia_minima=12,
            ativa=True,
            publicada=True,
        )

        self.categoria_financeira = CategoriaFinanceira.objects.create(
            empresa_contratante=self.empresa_contratante,
            nome="Alimentação",
            descricao="",
            tipo='despesa',
        )

        self.fornecedor = Fornecedor.objects.create(
            empresa_contratante=self.empresa_contratante,
            nome_fantasia="Fornecedor Buffet",
            razao_social="Fornecedor Buffet LTDA",
            cnpj="33.333.333/0001-33",
            tipo_fornecedor='alimentacao',
            telefone="",
            email="",
            website="",
        )

        self.despesa = DespesaEvento.objects.create(
            evento=self.evento,
            categoria=self.categoria_financeira,
            descricao="Compra de alimentos",
            valor=Decimal("500.00"),
            data_vencimento=date(2030, 4, 30),
            fornecedor=self.fornecedor,
            numero_documento="DOC123",
            status='pago',
        )

        self.receita = ReceitaEvento.objects.create(
            evento=self.evento,
            categoria=self.categoria_financeira,
            descricao="Pagamento cliente",
            valor=Decimal("1500.00"),
            data_vencimento=date(2030, 5, 1),
            cliente="Cliente XPTO",
            numero_documento="REC456",
            status='recebido',
        )

        self.checklist = ChecklistEvento.objects.create(
            empresa_contratante=self.empresa_contratante,
            evento=self.evento,
            titulo="Pré-evento",
            descricao="",
            responsavel=self.usuario,
            data_limite=date(2030, 5, 5),
            concluido=True,
        )

        ItemChecklist.objects.create(
            checklist=self.checklist,
            descricao="Confirmar fornecedores",
            ordem=1,
            responsavel=self.usuario,
            concluido=True,
        )

        self.tarefa = Tarefa.objects.create(
            empresa_contratante=self.empresa_contratante,
            titulo="Reunião com equipe",
            descricao="",
            responsavel=self.usuario,
            criado_por=self.usuario,
            prioridade='alta',
            status='em_andamento',
            evento_relacionado=self.evento,
        )

        self.categoria_insumo = CategoriaInsumo.objects.create(
            empresa_contratante=self.empresa_contratante,
            nome="Gastronomia",
        )

        self.insumo = Insumo.objects.create(
            empresa_contratante=self.empresa_contratante,
            empresa_fornecedora=self.empresa_fornecedora,
            codigo="INS-1",
            categoria=self.categoria_insumo,
            nome="Camarão",
            unidade_medida='kg',
            estoque_minimo=10,
            estoque_atual=50,
        )

        self.insumo_evento = InsumoEvento.objects.create(
            evento=self.evento,
            insumo=self.insumo,
            quantidade_total_necessaria=20,
            quantidade_alocada_evento=15,
            quantidade_distribuida_setores=10,
            quantidade_utilizada_evento=5,
            observacoes="",
            status='alocado',
        )

        InsumoSetor.objects.create(
            setor=self.setor,
            insumo_evento=self.insumo_evento,
            quantidade_necessaria=10,
            quantidade_alocada=8,
            quantidade_transportada=6,
            quantidade_utilizada=5,
            observacoes="",
            status='em_transporte',
        )

    def test_clone_event_with_all_modules(self):
        service = EventCloneService(usuario=self.usuario, evento_origem=self.evento)
        result = service.clone_event(
            nome="Evento Clonado",
            data_inicio=date(2030, 6, 1),
            data_fim=date(2030, 6, 2),
            descricao="Copiado",
        )

        evento_clonado = result.event
        self.assertEqual(evento_clonado.nome, "Evento Clonado")
        self.assertEqual(evento_clonado.empresa_contratante, self.empresa_contratante)
        self.assertEqual(evento_clonado.descricao, "Copiado")
        self.assertEqual(evento_clonado.local, self.local)

        self.assertEqual(evento_clonado.setores.count(), 1)
        novo_setor = evento_clonado.setores.first()
        self.assertIsNotNone(novo_setor)
        self.assertEqual(novo_setor.nome, self.setor.nome)

        vagas = evento_clonado.vagas_diretas.all()
        self.assertEqual(vagas.count(), 1)
        nova_vaga = vagas.first()
        self.assertEqual(nova_vaga.quantidade_preenchida, 0)
        self.assertFalse(nova_vaga.ativa)
        self.assertFalse(nova_vaga.publicada)
        self.assertEqual(nova_vaga.remuneracao, self.vaga.remuneracao)

        checklists = evento_clonado.checklists.all()
        self.assertEqual(checklists.count(), 1)
        checklist_clonado = checklists.first()
        self.assertFalse(checklist_clonado.concluido)
        self.assertEqual(checklist_clonado.itens.count(), 1)
        item_clonado = checklist_clonado.itens.first()
        self.assertFalse(item_clonado.concluido)

        tarefas = evento_clonado.tarefas.all()
        self.assertEqual(tarefas.count(), 1)
        self.assertEqual(tarefas.first().status, 'pendente')

        self.assertEqual(evento_clonado.insumos_evento.count(), 1)
        novo_insumo_evento = evento_clonado.insumos_evento.first()
        self.assertEqual(novo_insumo_evento.quantidade_alocada_evento, 0)
        self.assertEqual(novo_insumo_evento.setores_distribuicao.count(), 1)
        novo_insumo_setor = novo_insumo_evento.setores_distribuicao.first()
        self.assertEqual(novo_insumo_setor.quantidade_alocada, 0)

        self.assertEqual(evento_clonado.despesas.count(), 1)
        self.assertEqual(evento_clonado.despesas.first().status, 'pendente')
        self.assertEqual(evento_clonado.receitas.count(), 1)
        self.assertEqual(evento_clonado.receitas.first().status, 'pendente')

    def test_clone_event_without_optional_modules(self):
        options = EventCloneOptions(
            copy_setores=False,
            copy_vagas=False,
            copy_checklists=False,
            copy_tarefas=False,
            copy_insumos=False,
            copy_financeiro=False,
        )

        service = EventCloneService(usuario=self.usuario, evento_origem=self.evento)
        result = service.clone_event(
            nome="Evento Minimal",
            data_inicio=date(2030, 7, 1),
            data_fim=date(2030, 7, 2),
            options=options,
        )

        evento_clonado = result.event
        self.assertEqual(evento_clonado.setores.count(), 0)
        self.assertEqual(evento_clonado.vagas_diretas.count(), 0)
        self.assertEqual(evento_clonado.checklists.count(), 0)
        self.assertEqual(evento_clonado.tarefas.count(), 0)
        self.assertEqual(evento_clonado.insumos_evento.count(), 0)
        self.assertEqual(evento_clonado.despesas.count(), 0)
        self.assertEqual(evento_clonado.receitas.count(), 0)
