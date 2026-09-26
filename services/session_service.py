"""Sessões de atendimento em memória."""

import uuid

from fastapi import HTTPException

from schemas.session_schema import HistoryItem, MessageResponse, SessionState
from services.orchestrator import processar_mensagem

_SESSOES: dict[str, SessionState] = {}

SAUDACAO = "Olá, eu sou o atendimento do Banco Ágil. Para começar, informe o seu CPF."


def limpar() -> None:
    _SESSOES.clear()


def criar() -> SessionState:
    session = SessionState(session_id=str(uuid.uuid4()))
    session.history.append(HistoryItem(role="assistant", content=SAUDACAO))
    _SESSOES[session.session_id] = session
    return session


def obter(session_id: str) -> SessionState:
    session = _SESSOES.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Sessão não encontrada.")
    return session


def enviar_mensagem(session_id: str, texto: str) -> MessageResponse:
    session = obter(session_id)
    session.history.append(HistoryItem(role="user", content=texto))
    resposta = processar_mensagem(session, texto)
    session.history.append(HistoryItem(role="assistant", content=resposta))
    return MessageResponse(reply=resposta, session=session)
