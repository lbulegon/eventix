from django.urls import path

from app_briefing.views import BriefingView
from app_contratos.views import ContratoAssinarView, ContratoGerarView
from app_financeiro.views import OrcamentoOperacionalView
from app_mise.views import MiseEnPlaceView
from app_producao.views import CronogramaPreProducaoView
from app_operacao.views import OperacaoEventoView
from app_finalizacao.views import FinalizacaoEventoView
from app_fechamento.views import FechamentoInternoView
from app_planejamento.views import InsightEventoView
from app_menu.views import FichaTecnicaListCreateView, MenuListCreateView, PratoListCreateView


app_name = "api_v01"


urlpatterns = [
    path("eventos/<int:evento_id>/briefing/", BriefingView.as_view(), name="evento_briefing"),
    path("eventos/<int:evento_id>/menu/", MenuListCreateView.as_view(), name="menu_list_create"),
    path(
        "eventos/<int:evento_id>/menu/<int:menu_id>/pratos/",
        PratoListCreateView.as_view(),
        name="menu_pratos",
    ),
    path(
        "eventos/<int:evento_id>/menu/<int:menu_id>/pratos/<int:prato_id>/fichas/",
        FichaTecnicaListCreateView.as_view(),
        name="menu_fichas",
    ),
    path(
        "eventos/<int:evento_id>/orcamento/gerar",
        OrcamentoOperacionalView.as_view(),
        name="orcamento_gerar",
    ),
    path(
        "eventos/<int:evento_id>/contrato/gerar",
        ContratoGerarView.as_view(),
        name="contrato_gerar",
    ),
    path(
        "eventos/<int:evento_id>/contrato/assinar",
        ContratoAssinarView.as_view(),
        name="contrato_assinar",
    ),
    path(
        "eventos/<int:evento_id>/preproducao/cronograma",
        CronogramaPreProducaoView.as_view(),
        name="preproducao_cronograma",
    ),
    path(
        "eventos/<int:evento_id>/mise/",
        MiseEnPlaceView.as_view(),
        name="mise",
    ),
    path(
        "eventos/<int:evento_id>/operacao/timeline",
        OperacaoEventoView.as_view(),
        name="operacao_timeline",
    ),
    path(
        "eventos/<int:evento_id>/finalizacao/",
        FinalizacaoEventoView.as_view(),
        name="finalizacao",
    ),
    path(
        "eventos/<int:evento_id>/fechamento/",
        FechamentoInternoView.as_view(),
        name="fechamento",
    ),
    path(
        "eventos/<int:evento_id>/planejamento/insights",
        InsightEventoView.as_view(),
        name="planejamento_insights",
    ),
]
