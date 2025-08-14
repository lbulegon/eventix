from django.urls import path
from api_v01.views.auth_views import SignupFreelancerView, SignupEmpresaView
from api_v01.views.core_views import (
    EventoCreateView, VagaCreateView, VagaListByEventoView,
    CandidatarVagaView, MinhasCandidaturasView,
    CandidaturaUpdateStatusView, CriarAlocacaoView,
)

urlpatterns = [
    # SIGNUP
    path("signup/freelancer/", SignupFreelancerView.as_view(), name="signup-freelancer"),
    path("signup/empresa/", SignupEmpresaView.as_view(), name="signup-empresa"),

    # EVENTO/VAGA
    path("eventos/criar/", EventoCreateView.as_view(), name="evento-criar"),
    path("vagas/criar/", VagaCreateView.as_view(), name="vaga-criar"),
    path("eventos/<int:evento_id>/vagas/", VagaListByEventoView.as_view(), name="vagas-por-evento"),

    # CANDIDATURAS
    path("vagas/candidatar/", CandidatarVagaView.as_view(), name="candidatar-vaga"),
    path("candidaturas/minhas/", MinhasCandidaturasView.as_view(), name="minhas-candidaturas"),
    path("candidaturas/<int:pk>/status/", CandidaturaUpdateStatusView.as_view(), name="candidatura-status"),

    # ALOCAÇÃO
    path("alocacoes/criar/", CriarAlocacaoView.as_view(), name="alocacao-criar"),
]
