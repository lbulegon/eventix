"""
Utilitários compartilhados para links de convite e cadastro rápido de freelancers.
"""
from __future__ import annotations

import json
from typing import Any, Dict, Optional

from django.core import signing
from django.http import HttpRequest
from django.urls import reverse

from .models import EmpresaContratante, Funcao

# Convite com pré-preenchimento (vai para /freelancer/cadastro/?convite=...).
CADASTRO_CONVITE_SALT = "freelancer-convite"

# Identifica a empresa dona da página pública (sem autenticação) em
# /freelancer/gerar-convite/?empresa=...
EMPRESA_PUBLICA_GERAR_CONVITE_SALT = "freelancer-empresa-publica-gerar-convite"


def assinar_empresa_para_gerar_convite_publico(empresa_id: int) -> str:
    return signing.dumps({"empresa_id": int(empresa_id)}, salt=EMPRESA_PUBLICA_GERAR_CONVITE_SALT)


def desassinar_empresa_para_gerar_convite_publico(token: str) -> Optional[int]:
    if not token or not str(token).strip():
        return None
    try:
        data = signing.loads(token, salt=EMPRESA_PUBLICA_GERAR_CONVITE_SALT)
        if not isinstance(data, dict) or "empresa_id" not in data:
            return None
        return int(data["empresa_id"])
    except (signing.BadSignature, TypeError, ValueError):
        return None


def funcoes_disponiveis_para_empresa(empresa: EmpresaContratante):
    from django.db.models import Q

    return (
        Funcao.objects.filter(
            Q(empresa_contratante=empresa) | Q(empresa_contratante__isnull=True),
            ativo=True,
        )
        .select_related("tipo_funcao")
        .order_by("tipo_funcao__nome", "nome")
    )


def montar_payload_convite_cadastro(
    request: HttpRequest,
    empresa: EmpresaContratante,
    telefone: str = "",
    funcao_id: Optional[int] = None,
) -> Dict[str, Any]:
    """Gera o JSON padrão com link e mensagem WhatsApp para um convite de cadastro."""
    token_payload: Dict[str, Any] = {"empresa_id": empresa.id}
    t = (telefone or "").strip()
    if t:
        token_payload["telefone"] = t
    if funcao_id is not None:
        token_payload["funcao_id"] = int(funcao_id)

    convite = signing.dumps(token_payload, salt=CADASTRO_CONVITE_SALT)
    cadastro_path = reverse("freelancer_publico:cadastro")
    link_cadastro = request.build_absolute_uri(f"{cadastro_path}?convite={convite}")
    mensagem = (
        f"Olá! 👋\n"
        f"Faça seu cadastro rápido de freelancer na Eventix:\n{link_cadastro}\n\n"
        f"Leva menos de 2 minutos."
    )
    return {
        "sucesso": True,
        "link_cadastro": link_cadastro,
        "mensagem_whatsapp": mensagem,
    }


def parse_json_ou_post(request) -> dict:
    if request.content_type and "application/json" in request.content_type:
        try:
            return json.loads(request.body or "{}")
        except Exception:
            return {}
    return {k: v for k, v in request.POST.items()}
