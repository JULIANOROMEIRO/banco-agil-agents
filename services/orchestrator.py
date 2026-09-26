"""Orquestração explícita do atendimento."""

from agents import credit, credit_interview, exchange, triage
from services.comandos import quer_encerrar
from services.routing_service import decidir

MENSAGEM_ENCERRADO = "Este atendimento já foi encerrado. Inicie uma nova sessão para continuar."


def processar_mensagem(session, texto: str) -> str:
    if session.finished:
        return MENSAGEM_ENCERRADO

    if quer_encerrar(texto):
        session.finished = True
        return "Atendimento encerrado."

    if not session.authenticated:
        return triage.atender(session, texto)

    if session.active_agent is None:
        decisao = decidir(texto)
        if decisao.next_agent == "finish":
            session.finished = True
            return "Atendimento encerrado."
        session.active_agent = decisao.next_agent

    if session.active_agent == "credit":
        return credit.atender(session, texto)

    if session.active_agent == "credit_interview":
        return credit_interview.atender(session, texto)

    if session.active_agent == "exchange":
        return exchange.atender(session, texto)

    return "Não encontrei um agente para este atendimento."
