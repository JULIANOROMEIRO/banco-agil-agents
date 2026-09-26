from langchain_core.messages import AIMessage

from schemas.routing_schema import RoutingDecision


class _Bound:
    def invoke(self, messages):
        return AIMessage(content="Resposta simulada do agente.")


class _Structured:
    def invoke(self, messages):
        texto = []
        for message in messages:
            content = getattr(message, "content", "")
            if isinstance(content, str):
                texto.append(content.lower())
        junto = "\n".join(texto)
        if any(palavra in junto for palavra in ("dolar", "dólar", "cambio", "câmbio")):
            return RoutingDecision(next_agent="exchange", reason="Câmbio")
        if any(palavra in junto for palavra in ("limite", "credito", "crédito")):
            return RoutingDecision(next_agent="credit", reason="Crédito")
        return RoutingDecision(next_agent="finish", reason="Encerrar")


class FakeLLM:
    """Substitui o modelo nos testes. Não chama o OpenRouter."""

    def with_structured_output(self, schema):
        return _Structured()

    def bind_tools(self, tools):
        return _Bound()

    def invoke(self, messages):
        return AIMessage(content="Qual é a sua renda mensal?")
