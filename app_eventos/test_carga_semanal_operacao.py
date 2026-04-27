"""Testes da lógica de agrupamento da carga semanal (sem dependência de HTTP)."""
from datetime import time

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from app_eventos.services.carga_semanal_operacao import (
    DiaGrade,
    agrupar_carga_para_regras,
)


class CargaSemanalAgruparTest(SimpleTestCase):
    def test_agrupa_dias_com_mesma_carga_e_horario(self):
        dias = [
            DiaGrade(0, True, '08:00', '16:00', [{'funcao_id': 1, 'quantidade': 4}]),
            DiaGrade(1, True, '08:00', '16:00', [{'funcao_id': 1, 'quantidade': 4}]),
            DiaGrade(2, True, '08:00', '16:00', [{'funcao_id': 1, 'quantidade': 4}]),
            DiaGrade(5, True, '08:00', '16:00', [{'funcao_id': 1, 'quantidade': 6}]),
        ]
        grupos = agrupar_carga_para_regras(dias)
        self.assertEqual(len(grupos), 2)
        for wds, t0, t1, _carga in grupos:
            self.assertEqual((t0, t1), (time(8, 0), time(16, 0)))
        mapa = {tuple(wds): dict(c) for wds, _a, _b, c in grupos}
        self.assertEqual(mapa[(0, 1, 2)], {1: 4})
        self.assertEqual(mapa[(5,)], {1: 6})

    def test_todos_inativos_retorna_vazio(self):
        dias = [DiaGrade(i, False, '08:00', '16:00', []) for i in range(7)]
        self.assertEqual(agrupar_carga_para_regras(dias), [])

    def test_dia_ativo_sem_demanda_falha(self):
        dias = [DiaGrade(0, True, '08:00', '16:00', [])]
        with self.assertRaises(ValidationError):
            agrupar_carga_para_regras(dias)

    def test_soma_quantidades_mesma_funcao_linhas_duplicadas(self):
        dias = [
            DiaGrade(
                0,
                True,
                '08:00',
                '16:00',
                [
                    {'funcao_id': 1, 'quantidade': 2},
                    {'funcao_id': 1, 'quantidade': 3},
                ],
            )
        ]
        g = agrupar_carga_para_regras(dias)
        self.assertEqual(len(g), 1)
        _w, _a, _b, c = g[0]
        self.assertEqual(dict(c), {1: 5})
