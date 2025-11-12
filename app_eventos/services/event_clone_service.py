from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional, Any

from django.db import transaction

from app_eventos.models import (
    Evento,
    SetorEvento,
    Vaga,
    ChecklistEvento,
    ItemChecklist,
    Tarefa,
    InsumoEvento,
    InsumoSetor,
    DespesaEvento,
    ReceitaEvento,
)


@dataclass
class EventCloneOptions:
    copy_setores: bool = True
    copy_vagas: bool = True
    copy_checklists: bool = True
    copy_tarefas: bool = True
    copy_insumos: bool = True
    copy_financeiro: bool = True

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "EventCloneOptions":
        if not data:
            return cls()
        options = cls()
        for field_name in cls.__dataclass_fields__.keys():  # type: ignore[attr-defined]
            if field_name in data:
                setattr(options, field_name, bool(data[field_name]))
        return options


@dataclass
class EventCloneResult:
    event: Evento
    setor_map: Dict[int, SetorEvento] = field(default_factory=dict)
    insumo_evento_map: Dict[int, InsumoEvento] = field(default_factory=dict)


NOT_PROVIDED = object()


class EventCloneService:
    def __init__(self, *, usuario, evento_origem: Evento):
        self.usuario = usuario
        self.evento_origem = evento_origem

    @transaction.atomic
    def clone_event(
        self,
        *,
        nome: str,
        data_inicio,
        data_fim,
        descricao: Optional[str] = None,
        local=NOT_PROVIDED,
        empresa_produtora=NOT_PROVIDED,
        options: Optional[EventCloneOptions] = None,
    ) -> EventCloneResult:
        options = options or EventCloneOptions()

        evento_clone = Evento.objects.create(
            empresa_contratante=self.evento_origem.empresa_contratante,
            nome=nome,
            data_inicio=data_inicio,
            data_fim=data_fim,
            descricao=descricao if descricao is not None else self.evento_origem.descricao,
            local=self.evento_origem.local if local is NOT_PROVIDED else local,
            empresa_produtora=(
                self.evento_origem.empresa_produtora if empresa_produtora is NOT_PROVIDED else empresa_produtora
            ),
            ativo=True,
        )

        result = EventCloneResult(event=evento_clone)

        if options.copy_setores:
            self._clone_setores(evento_clone, result)

        if options.copy_insumos:
            self._clone_insumos(evento_clone, result)

        if options.copy_vagas:
            self._clone_vagas(evento_clone, result)

        if options.copy_checklists:
            self._clone_checklists(evento_clone, result)

        if options.copy_tarefas:
            self._clone_tarefas(evento_clone)

        if options.copy_financeiro:
            self._clone_financeiro(evento_clone)

        return result

    def _clone_setores(self, evento_clone: Evento, result: EventCloneResult) -> None:
        for setor in self.evento_origem.setores.all():
            novo_setor = SetorEvento.objects.create(
                evento=evento_clone,
                nome=setor.nome,
                descricao=setor.descricao,
                capacidade=setor.capacidade,
                ativo=setor.ativo,
            )
            result.setor_map[setor.id] = novo_setor

    def _clone_vagas(self, evento_clone: Evento, result: EventCloneResult) -> None:
        for vaga in self.evento_origem.vagas_diretas.all():
            setor_original_id = vaga.setor_id
            setor_destino = result.setor_map.get(setor_original_id)

            Vaga.objects.create(
                evento=evento_clone,
                setor=setor_destino,
                empresa_contratante=vaga.empresa_contratante,
                titulo=vaga.titulo,
                funcao=vaga.funcao,
                quantidade=vaga.quantidade,
                quantidade_preenchida=0,
                remuneracao=vaga.remuneracao,
                tipo_remuneracao=vaga.tipo_remuneracao,
                descricao=vaga.descricao,
                requisitos=vaga.requisitos,
                responsabilidades=vaga.responsabilidades,
                beneficios=vaga.beneficios,
                nivel_experiencia=vaga.nivel_experiencia,
                experiencia_minima=vaga.experiencia_minima,
                data_limite_candidatura=vaga.data_limite_candidatura,
                data_inicio_trabalho=vaga.data_inicio_trabalho,
                data_fim_trabalho=vaga.data_fim_trabalho,
                ativa=False,
                publicada=False,
                urgente=vaga.urgente,
                criado_por=vaga.criado_por,
            )

    def _clone_checklists(self, evento_clone: Evento, result: EventCloneResult) -> None:
        for checklist in self.evento_origem.checklists.all():
            novo_checklist = ChecklistEvento.objects.create(
                empresa_contratante=checklist.empresa_contratante,
                evento=evento_clone,
                titulo=checklist.titulo,
                descricao=checklist.descricao,
                responsavel=checklist.responsavel,
                data_limite=checklist.data_limite,
                concluido=False,
            )

            for item in checklist.itens.all():
                ItemChecklist.objects.create(
                    checklist=novo_checklist,
                    descricao=item.descricao,
                    ordem=item.ordem,
                    responsavel=item.responsavel,
                    concluido=False,
                    observacoes=item.observacoes,
                )

    def _clone_tarefas(self, evento_clone: Evento) -> None:
        for tarefa in self.evento_origem.tarefas.all():
            Tarefa.objects.create(
                empresa_contratante=tarefa.empresa_contratante,
                titulo=tarefa.titulo,
                descricao=tarefa.descricao,
                responsavel=tarefa.responsavel,
                criado_por=tarefa.criado_por,
                prioridade=tarefa.prioridade,
                status='pendente',
                data_limite=tarefa.data_limite,
                evento_relacionado=evento_clone,
            )

    def _clone_insumos(self, evento_clone: Evento, result: EventCloneResult) -> None:
        for insumo_evento in self.evento_origem.insumos_evento.all():
            novo_insumo_evento = InsumoEvento.objects.create(
                evento=evento_clone,
                insumo=insumo_evento.insumo,
                quantidade_total_necessaria=insumo_evento.quantidade_total_necessaria,
                quantidade_alocada_evento=0,
                quantidade_distribuida_setores=0,
                quantidade_utilizada_evento=0,
                responsavel_alocacao=insumo_evento.responsavel_alocacao,
                observacoes=insumo_evento.observacoes,
                status='pendente',
            )
            result.insumo_evento_map[insumo_evento.id] = novo_insumo_evento

        if not result.insumo_evento_map:
            return

        for insumo_setor in InsumoSetor.objects.filter(setor__evento=self.evento_origem):
            novo_setor = result.setor_map.get(insumo_setor.setor_id)
            novo_insumo_evento = result.insumo_evento_map.get(insumo_setor.insumo_evento_id)

            if not novo_insumo_evento:
                continue

            InsumoSetor.objects.create(
                setor=novo_setor,
                insumo_evento=novo_insumo_evento,
                quantidade_necessaria=insumo_setor.quantidade_necessaria,
                quantidade_alocada=0,
                quantidade_transportada=0,
                quantidade_utilizada=0,
                observacoes=insumo_setor.observacoes,
                data_necessidade=insumo_setor.data_necessidade,
                responsavel_insumo=insumo_setor.responsavel_insumo,
                status='pendente',
            )

    def _clone_financeiro(self, evento_clone: Evento) -> None:
        for despesa in self.evento_origem.despesas.all():
            DespesaEvento.objects.create(
                evento=evento_clone,
                categoria=despesa.categoria,
                descricao=despesa.descricao,
                valor=despesa.valor,
                data_vencimento=despesa.data_vencimento,
                fornecedor=despesa.fornecedor,
                numero_documento=despesa.numero_documento,
                status='pendente',
                observacoes=despesa.observacoes,
            )

        for receita in self.evento_origem.receitas.all():
            ReceitaEvento.objects.create(
                evento=evento_clone,
                categoria=receita.categoria,
                descricao=receita.descricao,
                valor=receita.valor,
                data_vencimento=receita.data_vencimento,
                cliente=receita.cliente,
                numero_documento=receita.numero_documento,
                status='pendente',
                observacoes=receita.observacoes,
            )
