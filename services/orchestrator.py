"""Orquestração explícita do atendimento."""

from agents import credit, credit_interview, exchange, triage
from services.comandos import quer_encerrar
from services.routing_service import decidir

MENSAGEM_ENCERRADO = "Este atendimento já foi encerrado. Inicie uma nova sessão para continuar."

_CAMBIO = ("dólar", "dolar", "cotação", "cotacao", "câmbio", "cambio", "euro")
_CREDITO = ("limite", "crédito", "credito", "aumento")


def _outro_assunto(texto: str, ativo: str) -> str | None:
    normalizado = (texto or "").lower()
    pede_cambio = any(palavra in normalizado for palavra in _CAMBIO)
    pede_credito = any(palavra in normalizado for palavra in _CREDITO)
    if ativo == "credit" and pede_cambio and not pede_credito:
        return "exchange"
    if ativo == "exchange" and pede_credito and not pede_cambio:
        return "credit"
    return None


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

    if session.active_agent in {"credit", "exchange"}:
        outro = _outro_assunto(texto, session.active_agent)
        if outro:
            session.awaiting_interview_confirmation = False
            session.active_agent = outro

    if session.active_agent == "credit":
        return credit.atender(session, texto)

    if session.active_agent == "credit_interview":
        return credit_interview.atender(session, texto)

    if session.active_agent == "exchange":
        return exchange.atender(session, texto)

    return "Não encontrei um agente para este atendimento."
