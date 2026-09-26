import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from core.llm import LLMNotConfigured
from schemas.session_schema import MessageCreate, MessageResponse, SessionState
from services import session_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("", response_model=SessionState)
def create_session() -> Any:
    """Inicia um atendimento."""
    logger.info("Criando sessão")
    return session_service.criar()


@router.get("/{session_id}", response_model=SessionState)
def read_session(session_id: str) -> Any:
    """Retorna o estado e o histórico da sessão."""
    logger.info("Consultando sessão %s", session_id)
    return session_service.obter(session_id)


@router.post("/{session_id}/messages", response_model=MessageResponse)
def create_message(session_id: str, payload: MessageCreate) -> Any:
    """Envia uma mensagem do cliente para o agente ativo."""
    logger.info("Mensagem na sessão %s", session_id)
    try:
        return session_service.enviar_mensagem(session_id, payload.message)
    except LLMNotConfigured as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
