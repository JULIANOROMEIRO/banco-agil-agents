"""Executa um agente com tool calling. Uma função, sem framework."""

import logging

from fastapi import HTTPException
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from crud.arquivos import DataFileError
from skills.loader import load_skill, render_skill

logger = logging.getLogger(__name__)


def _texto(resposta) -> str:
    conteudo = resposta.content
    if isinstance(conteudo, str):
        return conteudo
    if isinstance(conteudo, list):
        partes = []
        for parte in conteudo:
            if isinstance(parte, dict):
                partes.append(parte.get("text", ""))
            else:
                partes.append(str(parte))
        return "".join(partes)
    return str(conteudo or "")


def run_tool_agent(*, session, skill_name: str, tools: list) -> str:
    from core.llm import get_llm

    skill = load_skill(skill_name)
    sistema = (
        f"{render_skill(skill)}\n\n"
        f"CPF autenticado: {session.cpf}. Use este CPF nas actions. "
        "Não invente números: apresente somente o retorno das actions."
    )
    mensagens = [SystemMessage(content=sistema)]
    for item in session.history:
        if item.role == "user":
            mensagens.append(HumanMessage(content=item.content))
        else:
            mensagens.append(AIMessage(content=item.content))

    modelo = get_llm().bind_tools(tools)
    por_nome = {ferramenta.name: ferramenta for ferramenta in tools}

    for _ in range(4):
        resposta = modelo.invoke(mensagens)
        mensagens.append(resposta)
        if not getattr(resposta, "tool_calls", None):
            return _texto(resposta) or "Não consegui formular uma resposta."
        for chamada in resposta.tool_calls:
            nome = chamada["name"]
            try:
                resultado = por_nome[nome].invoke(chamada.get("args") or {})
            except DataFileError as exc:
                logger.exception("Falha ao executar a tool %s", nome)
                resultado = str(exc)
            except HTTPException as exc:
                logger.exception("Falha ao executar a tool %s", nome)
                detalhe = exc.detail
                resultado = detalhe if isinstance(detalhe, str) else "Não foi possível executar esta operação."
            except Exception:
                logger.exception("Falha ao executar a tool %s", nome)
                resultado = "Não foi possível executar esta operação."
            mensagens.append(
                ToolMessage(content=str(resultado), tool_call_id=chamada["id"])
            )
    return "Não consegui concluir a solicitação. Tente reformular."
