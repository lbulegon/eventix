"""
Regras de onboarding de freelancer (níveis) — fonte única para API, UI e textos de assistente.

- Nível 1: conta + perfil mínimo (pré-cadastro / registro) — já existente.
- Nível 2: dados pessoais e endereço (sem dados bancários e sem documentos arquivados).
- Nível 3: documentos (cadastro_completo do modelo) — usa verificar_cadastro_completo / uploads existentes.

Não duplica serializers: apenas expõe metadados e cálculo de pendências.
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

# Campos que o fluxo "nível 2" pode editar (subset explícito; fora: bancário e arquivos do modelo).
FREELANCE_ONBOARDING_NIVEL2_WRITE_FIELDS: Tuple[str, ...] = (
    "nome_completo",
    "telefone",
    "codigo_telefonico_pais",
    "documento",
    "habilidades",
    "cpf",
    "rg",
    "orgao_expedidor",
    "uf_rg",
    "data_nascimento",
    "sexo",
    "estado_civil",
    "nacionalidade",
    "naturalidade",
    "cep",
    "logradouro",
    "numero",
    "complemento",
    "bairro",
    "cidade",
    "uf",
    "observacoes",
)

# Campos considerados para dizer se o "nível 2" está completo (ordem informativa).
NIVEL2_CAMPOS_ESPERADOS: Tuple[str, ...] = (
    "data_nascimento",
    "sexo",
    "cep",
    "logradouro",
    "numero",
    "bairro",
    "cidade",
    "uf",
    "habilidades",
)


def _vazio(val: Any) -> bool:
    if val is None:
        return True
    if isinstance(val, str) and not val.strip():
        return True
    return False


def listar_pendentes_nivel2(freelance) -> List[str]:
    pendentes: List[str] = []
    for campo in NIVEL2_CAMPOS_ESPERADOS:
        if _vazio(getattr(freelance, campo, None)):
            pendentes.append(campo)
    return pendentes


def calcular_marcadores_onboarding(freelance) -> Dict[str, Any]:
    pendentes = listar_pendentes_nivel2(freelance)
    total = len(NIVEL2_CAMPOS_ESPERADOS)
    preenchidos = total - len(pendentes)
    pct = round(100.0 * preenchidos / total, 1) if total else 100.0

    doc_ok = bool(getattr(freelance, "cadastro_completo", False))

    return {
        "nivel1_conta_criada": True,
        "nivel2_dados_complementares": {
            "completo": len(pendentes) == 0,
            "percentual": pct,
            "pendentes": pendentes,
        },
        "nivel3_documentos": {
            "completo": doc_ok,
            "alinhado_ao_campo_cadastro_completo": doc_ok,
        },
        "observacoes_ux": _observacoes_ux_niveis(
            pendentes=pendentes,
            cadastro_completo=doc_ok,
        ),
    }


def _observacoes_ux_niveis(pendentes: List[str], cadastro_completo: bool) -> str:
    if not pendentes:
        if not cadastro_completo:
            return (
                "Dados pessoais e endereço estão preenchidos. Próximo passo: enviar documentos "
                "obrigatórios na área de perfil/documentos, conforme a política da plataforma."
            )
        return "Cadastro básico e documentos concluídos. Mantenha o perfil atualizado."
    return "Complete os itens pendentes do nível 2 (dados pessoais e endereço) com calma, em poucos passos."


def gerar_texto_assistente_nivel2(
    nome_exibicao: str,
    *,
    pendentes: List[str] | None = None,
) -> str:
    """
    Texto base (PT-BR) para colar em um assistente de IA (gerador de prompt) ou tela in-app.
    Não chama modelos de linguagem — apenas compõe o contexto.
    """
    nome = (nome_exibicao or "Olá").strip() or "Olá"
    pend = pendentes or []
    if not pend:
        return (
            f"{nome}, seu cadastro de nível 2 está completo quanto a dados pessoais e endereço. "
            f"Se ainda faltar documentos, a plataforma avisará na área de perfil."
        )
    pendentes_fmt = ", ".join(pend)
    return (
        f"{nome}, faltam alguns itens do nível 2: {pendentes_fmt}. "
        f"Peça de forma amigável só um tópico por vez (data, endereço ou competências) "
        f"e confirme antes de avançar. Não peça dados bancários nesta etapa."
    )
