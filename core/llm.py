"""Cliente do modelo via OpenRouter."""

from langchain_openai import ChatOpenAI

from core.config import settings


class LLMNotConfigured(RuntimeError):
    pass


def get_llm() -> ChatOpenAI:
    if not settings.OPENROUTER_API_KEY:
        raise LLMNotConfigured(
            "OPENROUTER_API_KEY não configurada. Copie .env.example para .env e informe a chave."
        )
    return ChatOpenAI(
        model=settings.OPENROUTER_MODEL,
        api_key=settings.OPENROUTER_API_KEY,
        base_url=settings.OPENROUTER_BASE_URL,
        temperature=0,
    )
