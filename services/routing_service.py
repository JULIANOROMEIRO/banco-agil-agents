"""Identifica o próximo agente com Structured Output."""

from langchain_core.messages import HumanMessage, SystemMessage

from schemas.routing_schema import RoutingDecision
from skills.loader import load_skill


def montar_prompt_roteamento() -> str:
    credito = load_skill("credit")
    cambio = load_skill("exchange")
    return (
        "Você classifica a mensagem de um cliente já autenticado do Banco Ágil. "
        "Escolha somente um próximo agente.\n"
        f"- credit: {credito.description.strip()}\n"
        f"- exchange: {cambio.description.strip()}\n"
        "- finish: o cliente quer encerrar o atendimento.\n"
        "Não invente outro agente."
    )


def decidir(mensagem: str) -> RoutingDecision:
    from core.llm import get_llm

    modelo = get_llm().with_structured_output(RoutingDecision)
    return modelo.invoke(
        [
            SystemMessage(content=montar_prompt_roteamento()),
            HumanMessage(content=mensagem),
        ]
    )
