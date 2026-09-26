"""Cliente do modelo. Azure OpenAI tem prioridade. OpenRouter fica como alternativa."""

from langchain_openai import AzureChatOpenAI, ChatOpenAI

from core.config import settings


class LLMNotConfigured(RuntimeError):
    pass


def get_llm() -> ChatOpenAI | AzureChatOpenAI:
    if settings.AZURE_OPENAI_API_KEY:
        if not settings.AZURE_OPENAI_ENDPOINT or not settings.AZURE_OPENAI_DEPLOYMENT_CHAT:
            raise LLMNotConfigured(
                "AZURE_OPENAI_ENDPOINT e AZURE_OPENAI_DEPLOYMENT_CHAT são obrigatórios junto com a chave."
            )
        return AzureChatOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_deployment=settings.AZURE_OPENAI_DEPLOYMENT_CHAT,
            temperature=0,
        )
    if not settings.OPENROUTER_API_KEY:
        raise LLMNotConfigured(
            "Nenhuma chave de modelo configurada. Informe AZURE_OPENAI_API_KEY ou OPENROUTER_API_KEY."
        )
    return ChatOpenAI(
        model=settings.OPENROUTER_MODEL,
        api_key=settings.OPENROUTER_API_KEY,
        base_url=settings.OPENROUTER_BASE_URL,
        temperature=0,
    )
