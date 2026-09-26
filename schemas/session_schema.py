from typing import Any, Literal

from pydantic import BaseModel, Field


class HistoryItem(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class SessionState(BaseModel):
    session_id: str
    cpf: str | None = None
    data_nascimento: str | None = None
    authenticated: bool = False
    auth_attempts: int = 0
    active_agent: Literal["credit", "credit_interview", "exchange"] | None = None
    awaiting_interview_confirmation: bool = False
    interview_data: dict[str, Any] = Field(default_factory=dict)
    finished: bool = False
    history: list[HistoryItem] = Field(default_factory=list)


class MessageCreate(BaseModel):
    message: str = Field(min_length=1)


class MessageResponse(BaseModel):
    reply: str
    session: SessionState
