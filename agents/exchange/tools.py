from langchain_core.tools import tool

from services import exchange_service


def build_exchange_tools(session):
    @tool
    def consultar_cotacao(moeda: str) -> str:
        """Consulta a cotação da moeda informada em relação ao real."""
        return exchange_service.consultar_cotacao(moeda)

    @tool
    def finalizar_atendimento() -> str:
        """Encerra o atendimento atual."""
        session.finished = True
        return "Atendimento encerrado."

    return [consultar_cotacao, finalizar_atendimento]
